import sys
import os

# Add root and backend directories to sys.path so all imports resolve correctly on Vercel
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(root_dir, "backend")

sys.path.append(root_dir)
sys.path.append(backend_dir)

# Import the FastAPI application
from backend.main import app as fastapi_app

class VercelPathMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            # Log path to Vercel console for verification
            print(f"[Vercel Router] Incoming path: {path}")
            
            # If the path is /health or /health/, let it pass (FastAPI has @app.get("/health"))
            if path in ("/health", "/health/"):
                pass
            # For other API routes, if Vercel stripped "/api", prepend it so FastAPI routes match
            elif not path.startswith("/api"):
                old_path = path
                scope["path"] = "/api" + path
                print(f"[Vercel Router] Prepending prefix: {old_path} -> {scope['path']}")
                
        await self.app(scope, receive, send)

# Expose the wrapped app as 'app' for Vercel
app = VercelPathMiddleware(fastapi_app)
