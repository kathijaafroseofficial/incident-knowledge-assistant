# show_structure_and_run.py — Print folder organization and verify app/API run
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def tree(dir_path: Path, prefix: str = "", exclude: set = None):
    exclude = exclude or {"venv", "__pycache__", ".git"}
    names = sorted([p.name for p in dir_path.iterdir()])
    dirs = [n for n in names if (dir_path / n).is_dir() and n not in exclude]
    files = [n for n in names if (dir_path / n).is_file()]
    all_ = dirs + files
    for i, name in enumerate(all_):
        is_last = i == len(all_) - 1
        current = "`-- " if is_last else "|-- "
        print(prefix + current + name)
        if (dir_path / name).is_dir() and name not in exclude:
            ext = "    " if is_last else "|   "
            tree(dir_path / name, prefix + ext, exclude)

print("=" * 60)
print("FOLDER ORGANIZATION - incident-knowledge-assistant")
print("=" * 60)
tree(ROOT)
print()
print("=" * 60)
print("RUN OUTPUT - API /chat test (Bearer token)")
print("=" * 60)
import sys
sys.path.insert(0, str(ROOT))
from api_server import app
from fastapi.testclient import TestClient
client = TestClient(app)
r = client.post(
    "/chat",
    json={"message": "What causes NullPointerException?", "context": "ERROR at PaymentService.process"},
    headers={"Authorization": "Bearer dev-token-change-in-production"},
)
print("POST /chat -> Status:", r.status_code)
print("Response body:", r.json())
print()
print("=" * 60)
print("Streamlit UI: run 'streamlit run app.py' -> http://localhost:8501")
print("API server:  run 'uvicorn api_server:app --port 8000' -> POST /chat")
print("=" * 60)
