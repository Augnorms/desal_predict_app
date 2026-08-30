import sys
import os
import multiprocessing
import uvicorn


def get_base_path():
    """Get the base path for the application (handles PyInstaller frozen exe)."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    multiprocessing.freeze_support()

    # When frozen, ensure we're in the right directory for relative imports
    base_path = get_base_path()
    if getattr(sys, 'frozen', False):
        os.chdir(base_path)

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)