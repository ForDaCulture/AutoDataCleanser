import time
import requests
import os
import logging
import sys
from dotenv import load_dotenv

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('smoke_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configure UTF-8 encoding for Windows
if sys.platform == "win32":
    import os
    os.system("")  # enable ANSI/UTF-8 on Windows Terminal
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv('backend/.env')

API_BASE = "http://localhost:8000/api"

def wait_for_service(url, max_retries=5, delay=2):
    """Wait for a service to become available"""
    for i in range(max_retries):
        try:
            logging.info(f"[INFO] Checking service at {url} (attempt {i+1}/{max_retries})")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                logging.info(f"[INFO] Service at {url} is available")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if i < max_retries - 1:
                logging.warning(f"[WARNING] Service not ready at {url}: {str(e)}")
                time.sleep(delay)
            continue
        except Exception as e:
            logging.exception(f"[ERROR] Unexpected error checking service at {url}")
            return False
    logging.error(f"[ERROR] Service at {url} failed to respond after {max_retries} attempts")
    return False

def run_smoke_test():
    """Run the smoke test suite"""
    logging.info("[INFO] Starting smoke test suite...")
    
    try:
        # Wait for services to be ready
        if not wait_for_service("http://localhost:8000/docs"):
            raise Exception("Backend service not available")
        
        if not wait_for_service("http://localhost:3000"):
            raise Exception("Frontend service not available")
        
        # 1. Sign up
        logging.info("[INFO] Starting signup test...")
        try:
            r = requests.post(
                f"{API_BASE}/auth/signup",
                json={"email": "smoketest@example.com", "password": "Test1234!"},
                timeout=10
            )
            assert r.status_code in (200, 201), f"Signup failed: {r.text}"
            logging.info("[INFO] Signup test passed")
        except Exception as e:
            logging.exception("[ERROR] Signup test failed")
            raise
        
        # 2. Sign in
        logging.info("[INFO] Starting signin test...")
        try:
            r = requests.post(
                f"{API_BASE}/auth/signin",
                json={"email": "smoketest@example.com", "password": "Test1234!"},
                timeout=10
            )
            assert r.status_code == 200, f"Signin failed: {r.text}"
            token = r.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            logging.info("[INFO] Signin test passed")
        except Exception as e:
            logging.exception("[ERROR] Signin test failed")
            raise
        
        # 3. Upload CSV
        logging.info("[INFO] Starting file upload test...")
        try:
            files = {"file": ("test.csv", "col1,col2\n1,2\n3,4", "text/csv")}
            r = requests.post(f"{API_BASE}/upload", headers=headers, files=files, timeout=30)
            assert r.status_code == 201, f"Upload failed: {r.text}"
            session_id = r.json()["session_id"]
            logging.info("[INFO] File upload test passed")
        except Exception as e:
            logging.exception("[ERROR] File upload test failed")
            raise
        
        # 4. Profile
        logging.info("[INFO] Starting profile test...")
        try:
            r = requests.get(f"{API_BASE}/profile/{session_id}", headers=headers, timeout=10)
            assert r.status_code == 200, f"Profile failed: {r.text}"
            logging.info("[INFO] Profile test passed")
        except Exception as e:
            logging.exception("[ERROR] Profile test failed")
            raise
        
        # 5. Clean
        logging.info("[INFO] Starting clean test...")
        try:
            r = requests.post(
                f"{API_BASE}/clean",
                headers=headers,
                json={"session_id": session_id},
                timeout=30
            )
            assert r.status_code == 200, f"Clean failed: {r.text}"
            logging.info("[INFO] Clean test passed")
        except Exception as e:
            logging.exception("[ERROR] Clean test failed")
            raise
        
        # 6. Download
        logging.info("[INFO] Starting download test...")
        try:
            r = requests.get(f"{API_BASE}/download/{session_id}", headers=headers, timeout=10)
            assert r.status_code == 200, f"Download failed: {r.text}"
            logging.info("[INFO] Download test passed")
        except Exception as e:
            logging.exception("[ERROR] Download test failed")
            raise
        
        # 7. Features
        logging.info("[INFO] Starting features test...")
        try:
            r = requests.post(
                f"{API_BASE}/features",
                headers=headers,
                json={"session_id": session_id},
                timeout=10
            )
            assert r.status_code == 200, f"Features failed: {r.text}"
            logging.info("[INFO] Features test passed")
        except Exception as e:
            logging.exception("[ERROR] Features test failed")
            raise
        
        logging.info("[INFO] All smoke tests passed successfully")
        return True
        
    except Exception as e:
        logging.exception("[ERROR] Smoke test suite failed")
        return False

if __name__ == "__main__":
    try:
        success = run_smoke_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        logging.exception("[ERROR] Fatal error in smoke test script")
        sys.exit(1) 