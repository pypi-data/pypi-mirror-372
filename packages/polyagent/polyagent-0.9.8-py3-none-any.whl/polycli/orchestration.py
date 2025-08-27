# orchestration.py
"""
Clean workflow system with full monitoring capabilities.
Single unified approach using context chains.
"""

import inspect
import copy
import json
import threading
from collections import defaultdict
from contextvars import ContextVar
from contextlib import contextmanager
from functools import wraps
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import mimetypes
import os
from typing import Optional, Any
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from .message import MessageList

# ---- Context variables for workflow ----
_context_chain = ContextVar("context_chain", default=[])
_current_session = ContextVar("current_session", default=None)

# ---- Transparent Future Implementation ----
class FutureResult:
    """A transparent future that proxies to its result when ready."""
    
    def __init__(self):
        self._result = None
        self._exception = None
        self._done = threading.Event()
    
    def set_result(self, result: Any) -> None:
        self._result = result
        self._done.set()
    
    def set_exception(self, exc: Exception) -> None:
        self._exception = exc
        self._done.set()
    
    def result(self, timeout: Optional[float] = None) -> Any:
        if not self._done.wait(timeout):
            raise TimeoutError(f"Future timed out after {timeout}s")
        if self._exception:
            raise self._exception
        return self._result
    
    @property
    def done(self) -> bool:
        return self._done.is_set()
    
    # Magic proxy methods - make future transparent
    def __getattr__(self, name):
        """Auto-forward any attribute access to the result."""
        return getattr(self.result(), name)
    
    def __getitem__(self, key):
        return self.result()[key]
    
    def __len__(self):
        return len(self.result())
    
    def __bool__(self):
        return bool(self.result())
    
    def __str__(self):
        if not self.done:
            return "<FutureResult pending>"
        return str(self._result)
    
    def __repr__(self):
        if not self.done:
            return "<FutureResult pending>"
        return f"<FutureResult: {repr(self._result)[:50]}...>"

class Context:
    """Context for the execution chain."""
    def __init__(self, type_name: str, context_id: str = None):
        self.type = type_name
        self.id = context_id or f"{type_name}_{id(self)}"
        self.tasks = []  # Only used by batch
        self.futures = []  # Futures corresponding to tasks

class Session:
    """Session with full monitoring and control capabilities."""
    
    def __init__(self, max_workers=10):
        # Records storage
        self.records = []
        self._lock = threading.RLock()
        
        # Pause-before-next + inbox for message injection
        self.pause_event = threading.Event()
        self.inbox = defaultdict(list)
        
        # SSE broadcaster
        self._clients = []
        self._next_id = 1
        
        # Thread pool for batch execution
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    # ---- SSE Broadcasting ----
    def _publish(self, event: dict):
        """Broadcast event to all SSE clients."""
        with self._lock:
            clients = list(self._clients)
        for q in clients:
            try:
                q.put_nowait(event)
            except queue.Full:
                pass
    
    def add_client(self, maxsize: int = 100) -> queue.Queue:
        q = queue.Queue(maxsize=maxsize)
        with self._lock:
            self._clients.append(q)
        return q
    
    def remove_client(self, q: queue.Queue):
        with self._lock:
            if q in self._clients:
                self._clients.remove(q)
    
    # ---- Recording ----
    def _next_rec_id(self) -> int:
        with self._lock:
            rid = self._next_id
            self._next_id += 1
            return rid
    
    def begin_record(self, rec: dict) -> int:
        """Start recording a pattern execution."""
        if "id" not in rec or rec["id"] is None:
            rec["id"] = self._next_rec_id()
        with self._lock:
            self.records.append(rec)
            idx = len(self.records) - 1
        self._publish({"type": "record-start", "record": _coerce_record_jsonable(rec)})
        return idx
    
    def finish_record(self, idx: int, after_map: dict, result):
        """Finish recording a pattern execution."""
        record = None
        with self._lock:
            if 0 <= idx < len(self.records):
                rec = self.records[idx]
                for name, meta in rec.get("agents", {}).items():
                    meta["messages"] = after_map.get(name, [])
                rec["result"] = result
                rec["status"] = "done"
                record = _coerce_record_jsonable(rec)
        if record:
            self._publish({"type": "record-finish", "record": record})
    
    def snapshot_records(self):
        with self._lock:
            return copy.deepcopy(self.records)
    
    # ---- Control Plane ----
    def request_pause(self):
        self.pause_event.set()
        self._publish({"type": "paused", "value": True})
    
    def clear_pause(self):
        self.pause_event.clear()
        self._publish({"type": "paused", "value": False})
    
    def is_paused(self) -> bool:
        return self.pause_event.is_set()
    
    def summon_agents(self, *agents):
        """Register agents for UI visibility."""
        agent_map = {}
        for i, agent in enumerate(agents):
            aid = getattr(agent, "id", None)
            if aid:
                messages = agent.messages.normalize_for_display() if hasattr(agent.messages, 'normalize_for_display') else agent.messages
                agent_map[f"agent_{i}"] = {
                    "id": aid,
                    "messages": messages
                }
        
        if agent_map:
            rec = {
                "pattern": "summon_agents",
                "status": "done",
                "inputs": {},
                "agents": agent_map,
                "result": f"Summoned {len(agent_map)} agent(s)",
                "batch_id": None,
                "batch_index": None,
                "batch_size": None
            }
            self.begin_record(rec)
    
    def inject(self, agent_id: str, text: str):
        """Queue message for injection."""
        if not text:
            return
        with self._lock:
            self.inbox[agent_id or "unnamed"].append(text)
    
    def publish_tokens(self, agent_id: str, tokens: str):
        """Publish streaming tokens to SSE clients."""
        self._publish({
            "type": "tokens",
            "agent_id": agent_id,
            "content": tokens,
            "timestamp": time.time()
        })
    
    def drain_into(self, agent) -> int:
        """Drain queued injections into agent."""
        aid = getattr(agent, "id", None)
        if aid is None:
            return 0
        with self._lock:
            pending = self.inbox.get(aid, [])
            self.inbox[aid] = []
        drained = 0
        for text in pending:
            if hasattr(agent, "add_user_message"):
                agent.add_user_message(text, position="end")
            else:
                agent.messages.append({"role": "user", "content": text})
            drained += 1
        return drained
    
    def wait_gate(self, agents: dict):
        """Pause gate - blocks while paused, then drains injections."""
        while self.is_paused():
            time.sleep(0.05)
        for ag in agents.values():
            self.drain_into(ag)
    
    def __str__(self):
        lines = []
        for rec in self.records:
            lines.append(f"------------- {rec['pattern']} ({rec.get('status','?')}) -------------")
            for param_name, meta in rec.get("agents", {}).items():
                agent_id = meta.get("id") or "unnamed"
                lines.append(f"{param_name}: {agent_id}")
            lines.append("")
        named_ids = {
            meta["id"]
            for rec in self.records
            for meta in rec.get("agents", {}).values()
            if meta.get("id")
        }
        lines.append("------------- statistics -------------")
        lines.append(f"number of named agents: {len(named_ids)}")
        lines.append(f"number of patterns executed: {len(self.records)}")
        return "\n".join(lines)

# ---- Helpers ----
def _is_agent(x):
    return hasattr(x, "messages")

def _split_agents_and_inputs(bound_arguments):
    """Split parameters into agents and non-agent inputs."""
    agents = {}
    inputs = {}
    
    for param_name, value in bound_arguments.items():
        if _is_agent(value):
            agents[param_name] = value
        elif isinstance(value, list):
            has_agents = False
            for i, item in enumerate(value):
                if _is_agent(item):
                    agents[f"{param_name}[{i}]"] = item
                    has_agents = True
            if not has_agents:
                inputs[param_name] = value
        elif isinstance(value, dict):
            has_agents = False
            for key, item in value.items():
                if _is_agent(item):
                    agents[f"{param_name}[{key}]"] = item
                    has_agents = True
            if not has_agents:
                inputs[param_name] = value
        else:
            inputs[param_name] = value
    
    return agents, inputs

def _coerce_jsonable(x):
    try:
        json.dumps(x)
        return x
    except TypeError:
        return repr(x)

def _coerce_record_jsonable(rec: dict) -> dict:
    """Ensure record is JSON serializable."""
    out = copy.deepcopy(rec)
    if "inputs" in out:
        out["inputs"] = {
            k: (v if isinstance(v, (str, int, float, bool, list, dict, type(None))) else repr(v))
            for k, v in out["inputs"].items()
        }
    if "result" in out:
        out["result"] = _coerce_jsonable(out["result"])
    return out

# ---- Pattern Decorator ----
def pattern(func):
    """Decorator that tracks pattern execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        chain = _context_chain.get()
        session = _current_session.get()
        
        # Check if we're in a batch context (collection phase)
        if chain and chain[-1].type == "batch":
            # Queue for batch execution
            batch_ctx = chain[-1]
            
            def executor():
                # Set up execution context in thread
                new_chain = chain[:-1] + [Context("pattern", f"pattern_{func.__name__}")]
                chain_token = _context_chain.set(new_chain)
                session_token = _current_session.set(session)
                
                try:
                    # Determine recording
                    should_record = False
                    batch_id = None
                    batch_index = None
                    batch_size = None
                    
                    if session and len(chain) == 2 and chain[0].type == "session" and chain[1].type == "batch":
                        should_record = True
                        batch_id = chain[1].id
                        batch_index = len(batch_ctx.tasks)  # Current position in batch
                        batch_size = None  # Will be set when batch executes
                    
                    # Bind arguments for agent detection
                    bound = inspect.signature(func).bind_partial(*args, **kwargs)
                    bound.apply_defaults()
                    agents, inputs = _split_agents_and_inputs(bound.arguments)
                    
                    # Pause gate and drain
                    if session:
                        session.wait_gate(agents)
                    
                    # Capture messages before
                    snap_messages = {
                        name: ag.messages.normalize_for_display() if hasattr(ag.messages, 'normalize_for_display') else ag.messages
                        for name, ag in agents.items()
                        if getattr(ag, "id", None) is not None
                    }
                    
                    # Record start
                    rec_idx = None
                    if should_record:
                        running_rec = {
                            "id": None,
                            "pattern": func.__name__,
                            "status": "running",
                            "inputs": inputs,
                            "agents": {
                                name: {
                                    "id": getattr(ag, "id", None),
                                    "messages": snap_messages.get(name, []),
                                } for name, ag in agents.items()
                                if getattr(ag, "id", None) is not None
                            },
                            "result": None,
                            "batch_id": batch_id,
                            "batch_index": batch_index,
                            "batch_size": batch_size
                        }
                        rec_idx = session.begin_record(running_rec)
                    
                    # Execute
                    result = func(*args, **kwargs)
                    
                    # Record end
                    if should_record and rec_idx is not None:
                        snap_after = {
                            name: ag.messages.normalize_for_display() if hasattr(ag.messages, 'normalize_for_display') else ag.messages
                            for name, ag in agents.items()
                            if getattr(ag, "id", None) is not None
                        }
                        session.finish_record(rec_idx, snap_after, result)
                    
                    return result
                finally:
                    _context_chain.reset(chain_token)
                    _current_session.reset(session_token)
            
            # Create future and store both task and future
            future = FutureResult()
            batch_ctx.tasks.append(executor)
            batch_ctx.futures.append(future)
            return future
        
        # Not in batch - execute immediately
        new_chain = chain + [Context("pattern", f"pattern_{func.__name__}")]
        chain_token = _context_chain.set(new_chain)
        
        try:
            # Determine if we should record (only top-level patterns)
            should_record = session and len(chain) == 1 and chain[0].type == "session"
            
            if not should_record:
                # Just execute without recording
                return func(*args, **kwargs)
            
            # Full recording for top-level pattern
            bound = inspect.signature(func).bind_partial(*args, **kwargs)
            bound.apply_defaults()
            agents, inputs = _split_agents_and_inputs(bound.arguments)
            
            # Pause gate and drain
            session.wait_gate(agents)
            
            # Capture messages before
            snap_messages = {
                name: ag.messages.normalize_for_display() if hasattr(ag.messages, 'normalize_for_display') else ag.messages
                for name, ag in agents.items()
                if getattr(ag, "id", None) is not None
            }
            
            # Record start
            running_rec = {
                "id": None,
                "pattern": func.__name__,
                "status": "running",
                "inputs": inputs,
                "agents": {
                    name: {
                        "id": getattr(ag, "id", None),
                        "messages": snap_messages.get(name, []),
                    } for name, ag in agents.items()
                    if getattr(ag, "id", None) is not None
                },
                "result": None,
                "batch_id": None,
                "batch_index": None,
                "batch_size": None
            }
            rec_idx = session.begin_record(running_rec)
            
            # Execute
            result = func(*args, **kwargs)
            
            # Capture messages after
            snap_after = {
                name: ag.messages.normalize_for_display() if hasattr(ag.messages, 'normalize_for_display') else ag.messages
                for name, ag in agents.items()
                if getattr(ag, "id", None) is not None
            }
            session.finish_record(rec_idx, snap_after, result)
            
            return result
            
        finally:
            _context_chain.reset(chain_token)
    
    return wrapper

# ---- Batch Context Manager ----
@contextmanager
def batch(max_workers: Optional[int] = None):
    """Context manager for parallel pattern execution."""
    chain = _context_chain.get()
    session = _current_session.get()
    
    # Create batch context
    batch_ctx = Context("batch")
    new_chain = chain + [batch_ctx]
    chain_token = _context_chain.set(new_chain)
    
    # Publish batch start event
    if session and len(chain) == 1 and chain[0].type == "session":
        session._publish({
            'type': 'batch-start',
            'batch_id': batch_ctx.id,
            'size': 0  # Will be updated
        })
    
    try:
        yield
    finally:
        _context_chain.reset(chain_token)
        
        # Execute all queued tasks in parallel
        if batch_ctx.tasks:
            # Update batch size in queued tasks
            for task in batch_ctx.tasks:
                # This is a bit hacky but works - the tasks haven't executed yet
                pass
            
            # Publish updated batch size
            if session and len(chain) == 1 and chain[0].type == "session":
                session._publish({
                    'type': 'batch-start',
                    'batch_id': batch_ctx.id,
                    'size': len(batch_ctx.tasks)
                })
            
            # Execute tasks in parallel
            executor = session._executor if (session and max_workers is None) else ThreadPoolExecutor(max_workers=max_workers or 10)
            use_local_executor = not (session and max_workers is None)
            
            try:
                # Execute tasks and get concurrent.futures objects
                exec_futures = [executor.submit(task) for task in batch_ctx.tasks]
                
                # Set results on our FutureResult objects as they complete
                for future_obj, exec_future in zip(batch_ctx.futures, exec_futures):
                    try:
                        result = exec_future.result()
                        future_obj.set_result(result)
                    except Exception as e:
                        future_obj.set_exception(e)
                
                # Publish batch complete
                if session and len(chain) == 1 and chain[0].type == "session":
                    session._publish({
                        'type': 'batch-complete',
                        'batch_id': batch_ctx.id,
                        'results': len(batch_ctx.futures)
                    })
                
                # Return the futures for backward compatibility
                return batch_ctx.futures
            finally:
                if use_local_executor:
                    executor.shutdown(wait=False)

# ---- Session Context Manager ----
@contextmanager
def session(s: Optional[Session] = None, max_workers: int = 10):
    """Context manager for session monitoring."""
    if s is None:
        s = Session(max_workers=max_workers)
    
    # Set up context chain
    session_ctx = Context("session")
    chain_token = _context_chain.set([session_ctx])
    session_token = _current_session.set(s)
    
    try:
        yield s
    finally:
        _context_chain.reset(chain_token)
        _current_session.reset(session_token)
        s._executor.shutdown(wait=False)

# ---- HTTP Server (unchanged) ----
class SessionMonitor:
    """Monitoring handler for Session objects."""
    
    def __init__(self, session: Session):
        self.session = session
        self.pkg_dir = os.path.dirname(__file__)
        self.static_dir = os.path.join(self.pkg_dir, "ui")
        self.ui_file = os.path.join(self.static_dir, "monitor.html")
    
    def handle_monitor_ui(self, base_path: str = "") -> tuple[int, str, bytes]:
        """Serve the monitoring UI HTML."""
        if os.path.exists(self.ui_file):
            with open(self.ui_file, "r", encoding="utf-8") as f:
                html = f.read()
            if base_path:
                html = html.replace('src="/static/', f'src="{base_path}/static/')
                html = html.replace("'/records'", f"'{base_path}/records'")
                html = html.replace("'/events'", f"'{base_path}/events'")
                html = html.replace("'/pause'", f"'{base_path}/pause'")
                html = html.replace("'/resume'", f"'{base_path}/resume'")
                html = html.replace("'/inject'", f"'{base_path}/inject'")
            return 200, "text/html; charset=utf-8", html.encode("utf-8")
        else:
            return 200, "text/html; charset=utf-8", b"<!doctype html><body style='background:#f8fafc;color:#111;font-family:sans-serif;margin:20px'><h1>Top-level Pattern Calls</h1><p>Missing ui/monitor.html</p></body>"
    
    def handle_static(self, path: str) -> tuple[int, str, bytes]:
        """Serve static assets."""
        rel = path[len("/static/"):]
        safe_rel = os.path.normpath(rel).replace("\\", "/")
        if safe_rel.startswith(".."):
            return 403, "text/plain", b"Forbidden"
        
        fp = os.path.join(self.static_dir, safe_rel)
        if os.path.isfile(fp):
            ctype, _ = mimetypes.guess_type(fp)
            ctype = ctype or "application/octet-stream"
            with open(fp, "rb") as f:
                return 200, ctype, f.read()
        else:
            return 404, "text/plain", b"Not found"
    
    def handle_records(self) -> dict:
        """Get session records and state."""
        data = self.session.snapshot_records()
        data = [_coerce_record_jsonable(r) for r in data]
        with self.session._lock:
            pending_injections = dict(self.session.inbox)
        return {
            "records": data,
            "paused": self.session.is_paused(),
            "pending_injections": pending_injections
        }
    
    def handle_pause(self) -> dict:
        """Pause the session."""
        self.session.request_pause()
        return {}
    
    def handle_resume(self) -> dict:
        """Resume the session."""
        self.session.clear_pause()
        return {}
    
    def handle_inject(self, agent_id: str, text: str) -> dict:
        """Inject a message into an agent."""
        self.session.inject(agent_id or "unnamed", text or "")
        return {}
    
    def handle_sse_client(self, write_func, flush_func):
        """Handle SSE streaming for a client."""
        q = self.session.add_client()
        try:
            init_evt = {"type": "paused", "value": self.session.is_paused()}
            write_func(b"data: " + json.dumps(init_evt).encode("utf-8") + b"\n\n")
            flush_func()
            
            while True:
                try:
                    evt = q.get(timeout=15.0)
                    write_func(b"data: " + json.dumps(evt).encode("utf-8") + b"\n\n")
                    flush_func()
                except queue.Empty:
                    write_func(b": keep-alive\n\n")
                    flush_func()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        except Exception as e:
            print(f"SSE: Error in event loop: {e}")
        finally:
            self.session.remove_client(q)

def serve_session(s: Session, host: str = None, port: int = 8765):
    """Start HTTP server to display session records."""
    if host is None:
        # Check if we're in Docker, default to 0.0.0.0 if so
        if os.path.exists('/.dockerenv'):
            host = os.environ.get('POLYCLI_HOST', '0.0.0.0')
        else:
            host = os.environ.get('POLYCLI_HOST', '127.0.0.1')
    elif host == "auto":
        host = '0.0.0.0'
    
    port = int(os.environ.get('POLYCLI_PORT', port))
    monitor = SessionMonitor(s)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            return
        
        def handle(self):
            try:
                super().handle()
            except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
                import sys
                if sys.platform == "win32" and hasattr(e, 'winerror'):
                    if e.winerror in [10053, 10054]:
                        pass
                    else:
                        raise
                else:
                    raise

        def _send_bytes(self, status: int, ctype: str, data: bytes):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, obj):
            body = json.dumps(obj).encode("utf-8")
            self._send_bytes(200, "application/json; charset=utf-8", body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                status, ctype, data = monitor.handle_monitor_ui()
                self._send_bytes(status, ctype, data)
                return

            if self.path.startswith("/static/"):
                status, ctype, data = monitor.handle_static(self.path)
                self._send_bytes(status, ctype, data)
                return

            if self.path == "/records":
                self._send_json(monitor.handle_records())
                return

            if self.path == "/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.end_headers()
                
                monitor.handle_sse_client(self.wfile.write, self.wfile.flush)
                return

            self.send_response(404); self.end_headers()

        def do_POST(self):
            def read_json():
                n = int(self.headers.get("Content-Length", "0") or "0")
                raw = self.rfile.read(n) if n else b""
                try:
                    return json.loads(raw.decode("utf-8")) if raw else {}
                except Exception:
                    return {}

            if self.path == "/pause":
                self._send_json(monitor.handle_pause())
                return

            if self.path == "/resume":
                self._send_json(monitor.handle_resume())
                return

            if self.path == "/inject":
                payload = read_json()
                agent_id = payload.get("agent_id", "unnamed")
                text = payload.get("text", "")
                self._send_json(monitor.handle_inject(agent_id, text))
                return

            self.send_response(404); self.end_headers()

    server = ThreadingHTTPServer((host, port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, t