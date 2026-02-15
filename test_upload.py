import requests
import time
import os
import sys
import re
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- Configuration ---
FILENAME = "test_large_image.jpg"
# Default to localhost, change as needed for production testing
UPLOAD_URL = 'http://127.0.0.1:5000/' 
FILE_SIZE_MB = 9
TIMEOUT_SECONDS = 120

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def generate_dummy_image(filename, size_mb):
    """
    Generates a dummy file that passes basic MIME type checks.
    Starts with a valid JPEG SOI marker and fills the rest with random bytes.
    """
    try:
        with open(filename, "wb") as f:
            f.write(b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01') 
            f.write(os.urandom((size_mb * 1024 * 1024) - 12))
        logger.info(f"Generated {size_mb}MB dummy image: {filename}")
    except OSError as e:
        logger.error(f"Failed to generate dummy image: {e}")
        sys.exit(1)

def get_csrf_token(session, url):
    """Retrieves the CSRF token from the upload page HTML."""
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        
        # Regex extraction avoids heavy dependencies like BeautifulSoup
        match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', response.text)
        if match:
            return match.group(1)
        logger.warning("CSRF token not found in HTML form.")
        return None
    except Exception as e:
        logger.error(f"Failed to fetch CSRF token: {e}")
        return None

def test_upload(filename, url):
    """
    Uploads the test image to the specified URL.
    Verifies connection stability and handles CSRF authentication.
    """
    if not os.path.exists(filename):
        logger.error(f"File {filename} not found.")
        return

    logger.info(f"Starting upload to {url} (Timeout: {TIMEOUT_SECONDS}s)...")
    
    session = requests.Session()
    # Retry strategy for transient network issues
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        # 1. Obtain Session & Token
        csrf_token = get_csrf_token(session, url)
        
        # 2. Upload File
        start_time = time.time()
        
        # Use context manager to ensure file handle is closed immediately
        with open(filename, 'rb') as f:
            files = {'image': (filename, f, 'image/jpeg')}
            data = {'csrf_token': csrf_token} if csrf_token else {}
            
            # Request timeout is set higher than server timeout to detect server-side drops
            response = session.post(url, files=files, data=data, timeout=TIMEOUT_SECONDS)

        elapsed = time.time() - start_time
        logger.info(f"Request completed in {elapsed:.2f} seconds.")
        logger.info(f"Status Code: {response.status_code}")
        
        # 3. Analyze Response
        if response.status_code in (200, 302):
             logger.info("SUCCESS: Upload accepted and processed.")
        elif response.status_code == 400:
             if "csrf" in response.text.lower():
                 logger.error("FAILURE: CSRF validation failed.")
             else:
                 logger.error("FAILURE: Bad Request (400). Check server logs.")
        elif response.status_code == 502:
             logger.error("FAILURE: 502 Bad Gateway. Upstream timeout/crash likely.")
        elif response.status_code == 504:
             logger.error("FAILURE: 504 Gateway Timeout.")
        else:
             logger.info(f"Server response excerpt: {response.text[:200]}")

    except requests.exceptions.Timeout:
        logger.error(f"FAILURE: Client timed out after {TIMEOUT_SECONDS}s.")
    except requests.exceptions.ConnectionError as e:
         logger.error(f"FAILURE: Connection error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during upload")
    finally:
        # Cleanup
        if os.path.exists(filename):
            try:
                os.remove(filename)
                logger.info(f"Cleaned up {filename}")
            except OSError as e:
                logger.warning(f"Cleanup failed (locked file?): {e}")

if __name__ == "__main__":
    generate_dummy_image(FILENAME, FILE_SIZE_MB)
    test_upload(FILENAME, UPLOAD_URL)
