import os
import sys
from pathlib import Path

def run():
    """
    Launch the Denario Streamlit app programmatically.
    Equivalent to running: streamlit run src/app.py
    """
    # Find the app file relative to this package
    app_path = Path(__file__).resolve().parent / "app.py"  # if app.py is in package
    if not app_path.exists():
        # fallback if you keep app in src/app.py outside the package
        app_path = Path(__file__).resolve().parent.parent / "src" / "app.py"

    if not app_path.exists():
        print(f"❌ Could not find Streamlit app at {app_path}")
        sys.exit(1)

    # Call `streamlit run` as a subprocess
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    os.execv(sys.executable, cmd)  # replaces current process
