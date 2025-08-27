#!/usr/bin/env python3
"""
Session Registry: Define sessions as triggerable functions with automatic UI generation.

This module provides:
- @session_def decorator to define reusable sessions
- SessionRegistry to manage and serve sessions via web UI
- Automatic form generation from function parameters
- Real-time monitoring of running sessions
"""

import inspect
import json
import threading
import uuid
import os
import time
from functools import wraps
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from contextlib import contextmanager

from .orchestration import session, serve_session, pattern, batch, _current_session, SessionMonitor
from .polyagent import PolyAgent


# Global registry instance (created when first session is defined)
_global_registry = None


class SessionRegistry:
    """Manages all registered sessions and serves control panel UI."""
    
    def __init__(self):
        self.registered_sessions = {}
        self.running_sessions = {}
        self.session_counter = 0
        self._lock = threading.RLock()
        self._session_threads = {}  # Track threads for cancellation
    
    def register(self, session_func):
        """Register a session function (called by @session_def decorator)."""
        with self._lock:
            session_id = session_func._session_id
            self.registered_sessions[session_id] = {
                "func": session_func,
                "name": session_func._session_name,
                "description": session_func._session_description,
                "params": session_func._session_params,
                "category": session_func._session_category,
            }
            print(f"[SessionRegistry] Registered session: {session_func._session_name}")
    
    def trigger_session(self, session_id: str, params: Dict[str, Any]) -> str:
        """Trigger a session execution with given parameters."""
        if session_id not in self.registered_sessions:
            raise ValueError(f"Unknown session: {session_id}")
        
        session_info = self.registered_sessions[session_id]
        func = session_info["func"]
        
        # Generate unique execution ID
        exec_id = f"{session_id}-{uuid.uuid4().hex[:8]}"
        
        # Execute in background thread
        thread = threading.Thread(
            target=self._run_session,
            args=(func, params, exec_id),
            daemon=True,
            name=f"session-{exec_id}"
        )
        
        # Store thread reference for cancellation
        with self._lock:
            self._session_threads[exec_id] = thread
        
        thread.start()
        
        return exec_id
    
    def _run_session(self, func: Callable, params: Dict[str, Any], exec_id: str):
        """Execute session function with automatic context and logging."""
        print(f"[SessionRegistry] Starting session execution: {exec_id}")
        
        # Create session context with higher worker count for triggered sessions
        with session(max_workers=30) as s:
            # Store session reference - monitoring available via control panel routes
            with self._lock:
                self.running_sessions[exec_id] = {
                    "session": s,
                    "start_time": time.time(),
                    "status": "running",
                    "params": params
                }
            print(f"\n{'='*60}")
            print(f"📦 Session started: {exec_id}")
            print(f"🔴 MONITORING: Available via control panel")
            print(f"{'='*60}\n")
            
            try:
                # Execute the session function
                result = func(**params)
                
                # Mark as completed
                with self._lock:
                    self.running_sessions[exec_id]["status"] = "completed"
                    self.running_sessions[exec_id]["result"] = result
                    self.running_sessions[exec_id]["end_time"] = time.time()
                    self.running_sessions[exec_id]["records"] = s.snapshot_records()  # Save final records
                
                print(f"\n{'='*60}")
                print(f"✅ Session completed: {exec_id}")
                print(f"📊 Pattern executions: {len(s.records)}")
                print(f"{'='*60}\n")
                
            except Exception as e:
                # Mark as failed
                with self._lock:
                    self.running_sessions[exec_id]["status"] = "failed"
                    self.running_sessions[exec_id]["error"] = str(e)
                    self.running_sessions[exec_id]["end_time"] = time.time()
                
                print(f"[SessionRegistry] Session failed: {exec_id} - {e}")
                raise
    
    def stop_session(self, exec_id: str) -> bool:
        """Stop a session (running or completed) and clean up resources."""
        with self._lock:
            if exec_id not in self.running_sessions:
                return False
            
            session_info = self.running_sessions[exec_id]
            
            # For completed sessions, just clean up
            if session_info["status"] == "completed":
                # Clean up from tracking
                del self.running_sessions[exec_id]
                if exec_id in self._session_threads:
                    del self._session_threads[exec_id]
                return True
            
            # For running sessions, cancel them
            elif session_info["status"] == "running":
                return self.cancel_session(exec_id)
            
            return False
    
    def cancel_session(self, exec_id: str) -> bool:
        """Force cancel a running session by killing its thread."""
        import ctypes
        
        with self._lock:
            if exec_id not in self.running_sessions:
                return False
            
            session_info = self.running_sessions[exec_id]
            if session_info["status"] != "running":
                return False
            
            # Mark as cancelled
            session_info["status"] = "cancelled"
            session_info["end_time"] = time.time()
            session_info["error"] = "Session was cancelled by user"
            
            # Get the thread
            thread = self._session_threads.get(exec_id)
            
        if thread and thread.is_alive():
            print(f"[SessionRegistry] Force cancelling session: {exec_id}")
            
            # Force kill the thread using ctypes
            try:
                # Get thread ID - use ident which is available in all Python 3.x
                thread_id = thread.ident
                
                if not thread_id:
                    print(f"[SessionRegistry] Could not get thread ID")
                    return False
                
                # Force terminate thread
                print(f"[SessionRegistry] Attempting to kill thread with ID: {thread_id}")
                
                # Try to inject SystemExit exception
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(thread_id),
                    ctypes.py_object(KeyboardInterrupt)  # Use KeyboardInterrupt instead of SystemExit
                )
                
                if res == 0:
                    print(f"[SessionRegistry] Thread {thread_id} not found")
                    return False
                elif res > 1:
                    # If it returns a number greater than 1, we're in trouble
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
                    print(f"[SessionRegistry] Failed to kill thread cleanly")
                    return False
                else:
                    print(f"[SessionRegistry] Successfully cancelled session thread: {exec_id}")
                    
                    # Clean up thread reference and session tracking
                    with self._lock:
                        if exec_id in self._session_threads:
                            del self._session_threads[exec_id]
                        # Remove from running_sessions to free the port
                        if exec_id in self.running_sessions:
                            del self.running_sessions[exec_id]
                    
                    return True
                        
            except Exception as e:
                print(f"[SessionRegistry] Error killing thread: {e}")
                return False
        
        return False
    
    def get_session_status(self, exec_id: str) -> Dict[str, Any]:
        """Get status of a running or completed session."""
        with self._lock:
            if exec_id in self.running_sessions:
                info = self.running_sessions[exec_id]
                session_obj = info["session"]
                
                return {
                    "exec_id": exec_id,
                    "status": info["status"],
                    "params": info["params"],
                    "start_time": info["start_time"],
                    "end_time": info.get("end_time"),
                    "result": info.get("result"),
                    "error": info.get("error"),
                    "records": session_obj.snapshot_records() if session_obj else []
                }
        return None
    
    def serve_control_panel(self, host: str = None, port: int = 8765):
        """Start web server for session control panel.
        
        Args:
            host: IP address to bind to. Options:
                  - None or "auto": Bind to 0.0.0.0 (all interfaces)
                  - "127.0.0.1" or "localhost": Local only
                  - Specific IP: Bind to that IP
                  - Can also be set via POLYCLI_HOST env variable
            port: Port to bind to (default 8765)
                  - Can also be set via POLYCLI_PORT env variable
        """
        # Check environment variables first
        if host is None:
            # Check if we're in Docker, default to 0.0.0.0 if so
            if os.path.exists('/.dockerenv'):
                host = os.environ.get('POLYCLI_HOST', '0.0.0.0')
            else:
                host = os.environ.get('POLYCLI_HOST', '127.0.0.1')
        elif host == "auto":
            host = '0.0.0.0'
        
        # Allow port override from environment
        port = int(os.environ.get('POLYCLI_PORT', port))
        registry_ref = self
        
        class ControlPanelHandler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                # Silence logs
                return
            
            def _send_json(self, obj):
                body = json.dumps(obj).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)
            
            def do_GET(self):
                # Handle session monitoring routes
                if self.path.startswith("/session/"):
                    # Extract exec_id and subpath
                    parts = self.path[9:].split("/", 1)  # Remove "/session/"
                    exec_id = parts[0]
                    subpath = "/" + parts[1] if len(parts) > 1 else "/"
                    
                    # Get the session
                    with registry_ref._lock:
                        session_info = registry_ref.running_sessions.get(exec_id)
                    
                    if not session_info or not session_info.get("session"):
                        self.send_response(404)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"Session not found")
                        return
                    
                    # Create monitor for this session
                    monitor = SessionMonitor(session_info["session"])
                    
                    # Route based on subpath
                    if subpath in ("/", "/index.html"):
                        # Pass base path for URL rewriting
                        base_path = f"/session/{exec_id}"
                        status, ctype, data = monitor.handle_monitor_ui(base_path)
                        self.send_response(status)
                        self.send_header("Content-Type", ctype)
                        self.end_headers()
                        self.wfile.write(data)
                    elif subpath.startswith("/static/"):
                        status, ctype, data = monitor.handle_static(subpath)
                        self.send_response(status)
                        self.send_header("Content-Type", ctype)
                        self.end_headers()
                        self.wfile.write(data)
                    elif subpath == "/records":
                        self._send_json(monitor.handle_records())
                    elif subpath == "/events":
                        # SSE stream
                        self.send_response(200)
                        self.send_header("Content-Type", "text/event-stream")
                        self.send_header("Cache-Control", "no-cache")
                        self.send_header("Connection", "keep-alive")
                        self.end_headers()
                        
                        # Use the reusable SSE handler
                        monitor.handle_sse_client(self.wfile.write, self.wfile.flush)
                    else:
                        self.send_response(404)
                        self.end_headers()
                    return
                
                if self.path == "/":
                    # Serve main control panel UI from static file
                    ui_file = Path(__file__).parent / "ui" / "control_panel.html"
                    if ui_file.exists():
                        with open(ui_file, "r", encoding="utf-8") as f:
                            html = f.read()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html; charset=utf-8")
                        self.end_headers()
                        self.wfile.write(html.encode())
                    else:
                        self.send_response(404)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"Control panel UI file not found")
                    
                elif self.path == "/api/sessions":
                    # Return all registered sessions
                    sessions = []
                    for sid, info in registry_ref.registered_sessions.items():
                        sessions.append({
                            "id": sid,
                            "name": info["name"],
                            "description": info["description"],
                            "category": info["category"],
                            "params": [
                                {"name": k, "type": v.__name__ if hasattr(v, '__name__') else str(v)}
                                for k, v in info["params"].items()
                            ]
                        })
                    self._send_json({"sessions": sessions})
                    
                elif self.path == "/api/running":
                    # Return all running sessions
                    running = []
                    with registry_ref._lock:
                        for exec_id, info in registry_ref.running_sessions.items():
                            running.append({
                                "exec_id": exec_id,
                                "status": info["status"],
                                "start_time": info["start_time"],
                                "params": info["params"],
                                "monitoring_available": True  # Monitoring via routes
                            })
                    self._send_json({"running": running})
                    
                elif self.path.startswith("/api/status/"):
                    # Get specific session status
                    exec_id = self.path.split("/")[-1]
                    status = registry_ref.get_session_status(exec_id)
                    if status:
                        self._send_json(status)
                    else:
                        self.send_response(404)
                        self.end_headers()
                        
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_POST(self):
                # Handle session monitoring POST routes
                if self.path.startswith("/session/"):
                    # Extract exec_id and subpath
                    parts = self.path[9:].split("/", 1)  # Remove "/session/"
                    exec_id = parts[0]
                    subpath = "/" + parts[1] if len(parts) > 1 else "/"
                    
                    # Get the session
                    with registry_ref._lock:
                        session_info = registry_ref.running_sessions.get(exec_id)
                    
                    if not session_info or not session_info.get("session"):
                        self.send_response(404)
                        self.end_headers()
                        return
                    
                    # Create monitor for this session
                    monitor = SessionMonitor(session_info["session"])
                    
                    # Read request body
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length) if content_length else b""
                    payload = json.loads(body.decode("utf-8")) if body else {}
                    
                    # Route based on subpath
                    if subpath == "/pause":
                        self._send_json(monitor.handle_pause())
                    elif subpath == "/resume":
                        self._send_json(monitor.handle_resume())
                    elif subpath == "/inject":
                        agent_id = payload.get("agent_id", "unnamed")
                        text = payload.get("text", "")
                        self._send_json(monitor.handle_inject(agent_id, text))
                    else:
                        self.send_response(404)
                        self.end_headers()
                    return
                
                if self.path == "/api/trigger":
                    # Trigger a session
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode("utf-8"))
                    
                    session_id = data["session_id"]
                    params = data["params"]
                    
                    try:
                        exec_id = registry_ref.trigger_session(session_id, params)
                        self._send_json({"success": True, "exec_id": exec_id})
                    except Exception as e:
                        self._send_json({"success": False, "error": str(e)})
                        
                elif self.path == "/api/stop":
                    # Stop a session (running or completed)
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode("utf-8"))
                    
                    exec_id = data["exec_id"]
                    
                    success = registry_ref.stop_session(exec_id)
                    self._send_json({"success": success})
                    
                elif self.path == "/api/cancel":
                    # Cancel a running session (backward compatibility)
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length)
                    data = json.loads(body.decode("utf-8"))
                    
                    exec_id = data["exec_id"]
                    
                    success = registry_ref.cancel_session(exec_id)
                    self._send_json({"success": success})
                    
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def do_OPTIONS(self):
                # Handle CORS preflight
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()
            
            
        
        server = ThreadingHTTPServer((host, port), ControlPanelHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        
        # Print accessible URLs
        if host == '0.0.0.0':
            import socket
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
                print(f"[SessionRegistry] Control panel running at:")
                print(f"  - http://localhost:{port}")
                print(f"  - http://127.0.0.1:{port}")
                print(f"  - http://{local_ip}:{port}")
                print(f"  - http://{hostname}:{port}")
            except:
                print(f"[SessionRegistry] Control panel running at http://0.0.0.0:{port} (all interfaces)")
        else:
            print(f"[SessionRegistry] Control panel running at http://{host}:{port}")
        return server, thread


def session_def(
    name: str = None,
    description: str = "",
    params: Dict[str, type] = None,
    category: str = "General"
):
    """
    Decorator that turns a function into a triggerable session.
    
    Args:
        name: Display name for the session
        description: Description shown in UI
        params: Parameter types for UI form generation
        category: Category for organizing sessions in UI
    
    Example:
        @session_def(
            name="Analyze Codebase",
            description="Analyze Python files for issues",
            params={"path": str, "max_files": int},
            category="Code Analysis"
        )
        def analyze_codebase(path: str, max_files: int = 10):
            agent = PolyAgent()
            # ... patterns run here ...
    """
    
    def decorator(func):
        # Extract parameter info from function signature if not provided
        if params is None:
            sig = inspect.signature(func)
            extracted_params = {}
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    extracted_params[param_name] = param.annotation
                else:
                    extracted_params[param_name] = str
        else:
            extracted_params = params
        
        # Store metadata
        func._session_id = func.__name__
        func._session_name = name or func.__name__.replace("_", " ").title()
        func._session_description = description or func.__doc__ or ""
        func._session_params = extracted_params
        func._session_category = category
        func._is_session_def = True
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if we're already in a session context
            current = _current_session.get()
            
            if current is None:
                # Not in session - create one automatically
                print(f"[session_def] Auto-creating session context for {func._session_name}")
                with session() as s:
                    # Optional: auto-serve UI if configured
                    if os.environ.get("AUTO_SERVE_SESSION_UI", "").lower() == "true":
                        serve_session(s)
                    
                    # Execute function in session context
                    return func(*args, **kwargs)
            else:
                # Already in session context (e.g., triggered from registry)
                return func(*args, **kwargs)
        
        # Auto-register with global registry
        global _global_registry
        if _global_registry is None:
            _global_registry = SessionRegistry()
        _global_registry.register(wrapper)
        
        return wrapper
    
    return decorator


# Convenience function to get global registry
def get_registry() -> SessionRegistry:
    """Get the global session registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = SessionRegistry()
    return _global_registry


