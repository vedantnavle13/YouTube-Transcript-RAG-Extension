import os
from dotenv import load_dotenv

# Try loading from backend/.env (relative to this file)
backend_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
if os.path.exists(backend_env_path):
    load_dotenv(backend_env_path)
else:
    # Try loading from workspace root .env
    root_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
    if os.path.exists(root_env_path):
        load_dotenv(root_env_path)
    else:
        # Standard fallback to whatever cwd is
        load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# We don't raise an error at module load time so the uvicorn server can at least boot and return helpful errors to clients,
# but we will check it when endpoints are loaded.
