import sys
from pathlib import Path

# --- ✅ START: FIX FOR ModuleNotFoundError ---
# This block adds the project's root directory to the Python path.
# It allows this script to correctly import from the 'infra' module.
# __file__ is the path to the current file (ingest_worker.py)
# .resolve() makes the path absolute.
# .parents[2] goes up two directories (from /backend/app/ to the project root).
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))
# --- ✅ END: FIX FOR ModuleNotFoundError ---

from ingest.process_pdf import process as process_pdf_func

def enqueue_pdf(path: str, metadata: dict):
    """
    This function is called by the background task handler.
    It calls the actual PDF processing logic.
    """
    print(f"Background task started for: {path}")
    try:
        process_pdf_func(path, metadata.get("title", ""))
        print(f"Background task finished successfully for: {path}")
    except Exception as e:
        print(f"Background task failed for {path}: {e}")

