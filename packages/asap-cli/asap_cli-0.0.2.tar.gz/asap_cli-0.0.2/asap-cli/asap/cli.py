import typer
import sys
import os

# Add the parent directory to Python path so we can import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

app = typer.Typer(help="🚀 ASAP CLI Tool")

# Direct import and registration
try:
    from asap.agent.main import register
    register(app)
except Exception as e:
    print(f"Warning: Could not load agent command: {e}")

def main():
    app()
