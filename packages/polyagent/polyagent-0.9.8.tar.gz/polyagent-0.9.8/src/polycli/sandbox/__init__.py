"""Sandbox module for safe polycli testing."""

from pathlib import Path


def init(project_dir="."):
    """Initialize a new sandbox project structure."""
    
    base = Path(project_dir)
    
    # Create directories
    (base / "workflow").mkdir(exist_ok=True)
    (base / "input" / "test1").mkdir(parents=True, exist_ok=True)
    (base / "output").mkdir(exist_ok=True)
    
    # Create minimal .polyconfig
    config_content = """# PolyCLI Sandbox Configuration
entry: workflow/main.py
ports: 8765:8765,8766:8766
# cache: true  # Cache enabled by default, set to false to disable
"""
    (base / ".polyconfig").write_text(config_content)
    
    # Create example entry point
    entry_content = '''"""Example PolyCLI sandbox entry."""

from polycli import PolyAgent
from pathlib import Path

# Read input
input_file = Path("input/sample.txt")
if input_file.exists():
    data = input_file.read_text()
    print(f"Read input: {data}")

# Process with agent
agent = PolyAgent()
result = agent.run(f"Summarize this: {data}")
print(f"Agent response: {result.content}")

# Write output
output_file = Path("output/summary.txt")
output_file.parent.mkdir(exist_ok=True)
output_file.write_text(result.content)
print(f"Wrote output to {output_file}")
'''
    (base / "workflow" / "main.py").write_text(entry_content)
    
    # Create sample input
    (base / "input" / "test1" / "sample.txt").write_text("Sample input data")
    
    print("✓ Created sandbox structure:")
    print("  workflow/   - Your workflow scripts")
    print("  input/      - Input data folders")  
    print("  output/     - Outputs will be captured here")
    print("  .polyconfig - Configuration")
    print("\nNext: Run 'polycli sandbox run' to test!")