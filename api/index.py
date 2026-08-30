import sys
import os

# Add root and backend directories to sys.path so all imports resolve correctly on Vercel
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(root_dir, "backend")

sys.path.append(root_dir)
sys.path.append(backend_dir)

# Import the FastAPI application from backend/main.py
from backend.main import app
