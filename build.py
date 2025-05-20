import os
import subprocess
import sys
import time
import logging
from pathlib import Path
from dotenv import load_dotenv
import requests

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('build.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configure UTF-8 encoding for Windows
if sys.platform == "win32":
    import os
    os.system("")  # enable ANSI/UTF-8 on Windows Terminal
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Platform detection
is_windows = sys.platform.startswith("win")

def run_command(command, cwd=None, shell=True, check=True, timeout=120):
    """Run a shell command and return its output"""
    cmd_str = command if isinstance(command, str) else " ".join(command)
    logging.info(f"[INFO] Running command: {cmd_str}")
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=shell,
            check=check,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Log both stdout and stderr on success
        if result.stdout:
            print("\n[COMMAND STDOUT]")
            print(result.stdout)
            logging.info(f"Command stdout:\n{result.stdout}")
        
        if result.stderr:
            print("\n[COMMAND STDERR]")
            print(result.stderr)
            logging.warning(f"Command stderr:\n{result.stderr}")
        
        return True, result.stdout
        
    except subprocess.TimeoutExpired as e:
        error_msg = f"Command timed out after {timeout}s: {cmd_str}"
        print(f"\n[ERROR] {error_msg}")
        logging.error(error_msg)
        if e.stdout:
            print("\n[COMMAND STDOUT]")
            print(e.stdout)
            logging.error(f"Timeout stdout:\n{e.stdout}")
        if e.stderr:
            print("\n[COMMAND STDERR]")
            print(e.stderr)
            logging.error(f"Timeout stderr:\n{e.stderr}")
        return False, error_msg
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed with exit code {e.returncode}: {cmd_str}"
        print(f"\n[ERROR] {error_msg}")
        logging.error(error_msg)
        if e.stdout:
            print("\n[COMMAND STDOUT]")
            print(e.stdout)
            logging.error(f"Error stdout:\n{e.stdout}")
        if e.stderr:
            print("\n[COMMAND STDERR]")
            print(e.stderr)
            logging.error(f"Error stderr:\n{e.stderr}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error running command: {cmd_str}"
        print(f"\n[ERROR] {error_msg}")
        logging.exception(error_msg)
        return False, str(e)

def upgrade_pip():
    """Upgrade pip to the latest version"""
    logging.info("[INFO] Upgrading pip...")
    success, output = run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        shell=False,
        timeout=60
    )
    if not success:
        logging.error(f"[ERROR] Failed to upgrade pip: {output}")
        return False
    logging.info("[INFO] Pip upgraded successfully")
    return True

def install_dependencies(max_attempts=3):
    """Install Python dependencies with conflict resolution"""
    logging.info("[INFO] Installing dependencies...")
    
    for attempt in range(max_attempts):
        success, output = run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            shell=False,
            timeout=300  # 5 minutes for pip install
        )
        
        if success:
            logging.info("[INFO] Dependencies installed successfully")
            return True
            
        logging.warning(f"Attempt {attempt + 1}/{max_attempts} failed:")
        logging.warning(output)
        
        if attempt < max_attempts - 1:
            logging.info("[INFO] Retrying with pip's dependency resolver...")
            success, output = run_command(
                [sys.executable, "-m", "pip", "install", "--no-deps", "-r", "requirements.txt"],
                shell=False,
                timeout=300
            )
            if success:
                logging.info("[INFO] Dependencies installed with --no-deps")
                return True
    
    logging.error("[ERROR] Failed to install dependencies after all attempts")
    return False

def setup_python_env():
    """Setup Python virtual environment and install dependencies"""
    logging.info("[INFO] Setting up Python environment...")
    
    try:
        # Create virtual environment if it doesn't exist
        if not os.path.exists("venv"):
            success, output = run_command("python -m venv venv")
            if not success:
                logging.error(f"[ERROR] Failed to create virtual environment: {output}")
                return False
        
        # Upgrade pip and install dependencies
        if not upgrade_pip():
            return False
        
        if not install_dependencies():
            return False
        
        logging.info("[INFO] Python environment setup complete")
        return True
    except Exception as e:
        logging.exception("[ERROR] Unexpected error in setup_python_env")
        return False

def setup_backend():
    """Setup backend environment"""
    logging.info("[INFO] Setting up backend...")
    
    try:
        # Load backend environment variables
        if not os.path.exists("backend/.env"):
            logging.error("[ERROR] Missing backend/.env file")
            return False
        
        load_dotenv("backend/.env")
        
        # Verify required environment variables
        required_vars = [
            "SUPABASE_URL",
            "SUPABASE_SERVICE_KEY",
            "SUPABASE_JWT_SECRET",
            "FRONTEND_URL"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logging.error(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        logging.info("[INFO] Backend setup complete")
        return True
    except Exception as e:
        logging.exception("[ERROR] Unexpected error in setup_backend")
        return False

def setup_frontend():
    """Setup frontend environment"""
    logging.info("[INFO] Setting up frontend...")
    
    try:
        # Load frontend environment variables
        if not os.path.exists("frontend/.env.local"):
            logging.error("[ERROR] Missing frontend/.env.local file")
            return False
        
        load_dotenv("frontend/.env.local")
        
        # Verify required environment variables
        required_vars = [
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "NEXT_PUBLIC_API_BASE"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logging.error(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        # Install frontend dependencies
        commands = [
            "npm install",
            "npm install axios @supabase/supabase-js tailwindcss postcss autoprefixer ag-grid-react ag-grid-community",
            "npm install --save-dev typescript @types/react @types/react-dom @types/node",
            "npx tailwindcss init -p"
        ]
        
        for cmd in commands:
            success, output = run_command(cmd, cwd="frontend")
            if not success:
                logging.error(f"[ERROR] Failed to install dependencies: {output}")
                return False
        
        logging.info("[INFO] Frontend setup complete")
        return True
    except Exception as e:
        logging.exception("[ERROR] Unexpected error in setup_frontend")
        return False

def poll_url(url, proc, attempts=5, delay=5):
    """Poll a URL until it responds or max attempts reached"""
    for i in range(attempts):
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                logging.info(f"[INFO] {url} is ready")
                return True
        except Exception as e:
            logging.warning(f"[WARNING] {url} not ready (attempt {i+1}/{attempts}): {e}")
        time.sleep(delay)
    logging.error(f"[ERROR] {url} failed to respond after {attempts} attempts")
    proc.terminate()
    return False

def start_services():
    """Start backend and frontend services"""
    logging.info("[INFO] Starting services...")
    
    try:
        # Start backend
        logging.info("[INFO] Starting backend dev server...")
        backend_proc = subprocess.Popen(
            ["uvicorn", "main:app", "--reload"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Start frontend
        logging.info("[INFO] Starting frontend dev server...")
        if is_windows:
            frontend_cmd = "npm.cmd run dev"
            shell = True
        else:
            frontend_cmd = ["npm", "run", "dev"]
            shell = False

        frontend_proc = subprocess.Popen(
            frontend_cmd,
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell
        )

        # Poll backend docs
        if not poll_url("http://localhost:8000/docs", backend_proc):
            frontend_proc.terminate()
            return None, None

        # Poll frontend
        if not poll_url("http://localhost:3000", frontend_proc):
            backend_proc.terminate()
            return None, None

        return backend_proc, frontend_proc

    except Exception as e:
        logging.exception("[ERROR] Failed to start services")
        return None, None

def main():
    """Main build script"""
    try:
        # Setup environments
        if not setup_python_env():
            sys.exit(1)
        if not setup_backend():
            sys.exit(1)
        if not setup_frontend():
            sys.exit(1)

        # Start services
        backend_proc, frontend_proc = start_services()
        if not backend_proc or not frontend_proc:
            sys.exit(1)

        # Run smoke tests
        success, output = run_command("python smoke_test.py", timeout=120)
        if not success:
            # Dump logs from smoke_test.log
            logging.error("[ERROR] Smoke test failed—see smoke_test.log")
            with open("smoke_test.log", encoding="utf-8") as f:
                for line in f.readlines()[-50:]:
                    print(line.rstrip())
            # Kill dev servers
            backend_proc.terminate()
            frontend_proc.terminate()
            sys.exit(1)

        # Shutdown servers on success
        backend_proc.terminate()
        frontend_proc.terminate()
        logging.info("[INFO] All smoke tests passed")
        return 0

    except Exception as e:
        logging.exception("[ERROR] Fatal error in build script")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 