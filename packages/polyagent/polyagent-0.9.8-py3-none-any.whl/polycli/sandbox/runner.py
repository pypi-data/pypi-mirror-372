"""Sandbox runner for Docker execution."""

import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path


def run(project_dir=".", input_folder=None, stream=True, ports=None):
    """Run sandbox in Docker."""
    
    base = Path(project_dir).resolve()
    
    # Check .polyconfig exists
    config_file = base / ".polyconfig"
    if not config_file.exists():
        print("❌ No .polyconfig found. Run 'polycli sandbox init' first.")
        return
    
    # Check Claude directory permissions
    claude_dir = Path.home() / ".claude"
    if claude_dir.exists():
        # Check if directory is writable by others (need at least 0o777)
        mode = claude_dir.stat().st_mode & 0o777
        if mode < 0o777:
            print("⚠️  Warning: ~/.claude/ directory needs write permissions for Docker")
            print(f"   Current: {oct(mode)}, needs: 0o777")
            print("   Fix with: chmod -R 777 ~/.claude")
            print("   This allows the container to write cache/session data")
            response = input("Continue anyway? [y/N]: ")
            if response.lower() != 'y':
                return
    
    # Parse config for entry point
    config = {}
    for line in config_file.read_text().splitlines():
        if ':' in line and not line.startswith('#'):
            key, value = line.split(':', 1)
            config[key.strip()] = value.strip()
    
    entry = config.get('entry', 'workflow/main.py')
    config_ports = config.get('ports', '')
    # Cache is enabled by default unless explicitly disabled in config
    cache_enabled = config.get('cache', 'true').lower() != 'false'
    
    # Determine which input folders to run
    input_dir = base / "input"
    if input_folder:
        # Run specific input folder
        folders = [input_dir / input_folder] if (input_dir / input_folder).exists() else []
    else:
        # Run all input folders
        folders = [f for f in input_dir.iterdir() if f.is_dir()]
    
    if not folders:
        print("❌ No input folders found")
        return
    
    # Check Docker image exists
    result = subprocess.run(
        ["docker", "images", "-q", "polycli-sandbox"],
        capture_output=True,
        text=True
    )
    
    if not result.stdout.strip():
        print("❌ Docker image 'polycli-sandbox' not found")
        print("  Build it with: docker build -t polycli-sandbox <path-to-dockerfile>")
        return
    
    # Disable streaming if multiple folders (parallel execution)
    if len(folders) > 1 and stream:
        print("⚠ Streaming disabled for multiple inputs")
        stream = False
    
    # Run for each input folder
    for folder in folders:
        folder_name = folder.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"run_{timestamp}_{folder_name}"
        
        print(f"\n▶ Running with input/{folder_name}/...")
        
        # Create output directory for this run
        output_dir = base / "output" / run_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the output subdirectory that will be mounted
        (output_dir / "output").mkdir(exist_ok=True)
        # Set permissions so container can write (777 for simplicity)
        (output_dir / "output").chmod(0o777)
        
        # Setup cache directory if enabled
        if cache_enabled:
            cache_dir = base / '.polycache'
            cache_dir.mkdir(exist_ok=True)
            cache_dir.chmod(0o777)
            if stream:  # Only show message once if streaming
                print(f"  Cache: Enabled (.polycache/ mounted)")
        
        # Copy input to output for record keeping
        shutil.copytree(folder, output_dir / "input")
        
        # Prepare Docker command
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{base / 'workflow'}:/workspace/workflow:ro",
            "-v", f"{folder}:/workspace/input:ro",
            "-v", f"{output_dir / 'output'}:/workspace/output",
            "-v", f"{Path.home() / '.claude'}:/home/node/.claude",
            "-w", "/workspace",
        ]
        
        # Mount models.json if it exists (for API configuration)
        models_json = base / "models.json"
        if models_json.exists():
            cmd.extend(["-v", f"{models_json}:/workspace/models.json:ro"])
        
        # Add cache mount and environment variable if enabled
        if cache_enabled:
            cmd.extend([
                "-v", f"{cache_dir}:/workspace/.polycache",
                "-e", "POLYCLI_CACHE=true"
            ])
        
        # Always set PYTHONUNBUFFERED for real-time output
        cmd.extend(["-e", "PYTHONUNBUFFERED=1"])
        
        # Add port mappings (CLI args override config)
        port_mappings = ports or config_ports
        
        if port_mappings:
            for port_mapping in port_mappings.split(','):
                port_mapping = port_mapping.strip()
                if port_mapping:
                    cmd.extend(["-p", port_mapping])
        
        cmd.extend([
            "polycli-sandbox",
            "python", f"/workspace/{entry}"
        ])
        
        # Open log file for terminal output
        log_file = output_dir / "terminal.log"
        
        if stream:
            # Run with real-time streaming
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    env={**os.environ, 'PYTHONUNBUFFERED': '1'}
                )
                
                for line in process.stdout:
                    print(line, end='')
                    log.write(line)
                    log.flush()
                
                process.wait()
                
                if process.returncode != 0:
                    print(f"❌ Container exited with code {process.returncode}")
        else:
            # Run without streaming (capture all at once)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Save terminal output
            with open(log_file, 'w') as log:
                if result.stdout:
                    log.write(result.stdout)
                if result.stderr:
                    log.write("\n--- STDERR ---\n")
                    log.write(result.stderr)
            
            # Show summary
            if result.returncode != 0:
                print(f"❌ Container exited with code {result.returncode}")
        
        print(f"✓ Output saved to: output/{run_name}/")
        
        # Create/update symlink to latest run
        latest_link = base / "output" / "latest"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(run_name)
        
        if stream:  # Only show this message once per run in streaming mode
            print(f"  Latest run: output/latest/ -> {run_name}/")