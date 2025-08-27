"""Terminal chat that resumes from Claude Code sessions."""

import json
import sys
import threading
import time
from pathlib import Path
import requests

from .polyagent import PolyAgent
from .orchestration import Session, serve_session


def run_chat():
    """Run the terminal chat interface."""
    # Find latest Claude session for current directory
    import os
    
    # @@@ Encode current directory path like Claude Code does
    cwd = os.getcwd()
    cwd_encoded = cwd.replace("/", "-").replace("\\", "-").replace(":", "")
    
    claude_projects = Path.home() / ".claude" / "projects" / cwd_encoded
    session_files = list(claude_projects.glob("*.jsonl")) if claude_projects.exists() else []
    latest = max(session_files, key=lambda p: p.stat().st_mtime) if session_files else None
    
    # Get first model from models.json
    try:
        with open("models.json") as f:
            model = list(json.load(f)["models"].keys())[0]
    except:
        model = "claude-3-5-sonnet-20241022"
    
    # Create agent and load state
    agent = PolyAgent(id="chat")
    if latest:
        try:
            agent.load_state(str(latest))
            print(f"Resumed: {latest.name}")
        except Exception as e:
            print(f"Fresh start ({e})")
    
    # Start session server for streaming
    session = Session()
    server, _ = serve_session(session, host="127.0.0.1", port=8768)
    time.sleep(0.2)  # Let server start
    
    print(f"Chat [{model}]")
    print("-" * 40)
    
    # Set session context once (before SSE connection)
    from .orchestration import _current_session
    _current_session.set(session)
    
    # Start persistent SSE connection
    streamed_tokens = []
    def read_sse():
        try:
            resp = requests.get("http://127.0.0.1:8768/events", stream=True, timeout=None)
            for line in resp.iter_lines(decode_unicode=True, chunk_size=1):
                if line and line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        if data.get("type") == "tokens":
                            token = data["content"]
                            streamed_tokens.append(token)
                            sys.stdout.write(token)
                            sys.stdout.flush()
                    except:
                        pass
        except Exception as e:
            print(f"\n[SSE Error: {e}]")
    
    sse_thread = threading.Thread(target=read_sse, daemon=True)
    sse_thread.start()
    time.sleep(0.5)  # Wait for SSE connection to establish
    
    # Chat loop
    try:
        while True:
            user_input = input("\nYou: ")
            if not user_input:
                continue
            
            print("Assistant: ", end="", flush=True)
            
            try:
                # Clear token buffer
                streamed_tokens.clear()
                
                result = agent.run(user_input, model=model, cli="no-tools", stream=True)
                time.sleep(0.5)  # Give SSE time to finish streaming
                
                # If nothing was streamed, print the result directly
                if not streamed_tokens and result.content:
                    print(result.content, end="")
                print()  # Newline after response
            except Exception as e:
                print(f"\n[Error: {e}]")
            
    except KeyboardInterrupt:
        print("\nBye")
        server.shutdown()
        sys.exit(0)