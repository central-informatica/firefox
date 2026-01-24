"""
Root conftest.py to configure pytest path for backend tests
"""
import sys
from pathlib import Path

# Add backend directory to Python path so tests can import from 'tests' module
backend_dir = Path(__file__).parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
