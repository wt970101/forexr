from dotenv import load_dotenv
import os
import platform
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

APP_PATH = "webapp.app:app"

def main():
    system = platform.system().lower()
    port = os.environ.get("PORT", "5000")
    workers = os.environ.get("WORKERS", "4")
    debug = os.environ.get("DEBUG", "false").lower() == "true"

    if system == "windows":
        print("Detected Windows: Starting Flask development server...")
        os.environ.setdefault("FLASK_APP", "webapp.app")
        os.environ.setdefault("FLASK_RUN_HOST", "0.0.0.0")
        os.environ.setdefault("FLASK_RUN_PORT", port)
        if debug:
            os.environ.setdefault("FLASK_DEBUG", "1")
        subprocess.run([sys.executable, "-m", "flask", "run"])
    else:
        print("Detected Unix-like system: Starting Gunicorn production server...")
        subprocess.run([
            "gunicorn",
            APP_PATH,
            "--bind", f"0.0.0.0:{port}",
            "--workers", workers
        ])

if __name__ == "__main__":
    main()
