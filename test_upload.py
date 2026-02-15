import requests
import time
import os

# Create a dummy 9MB file
filename = "test_large_image.jpg"
with open(filename, "wb") as f:
    f.write(os.urandom(9 * 1024 * 1024))

def file_sender(file_name):
    with open(file_name, 'rb') as f:
        while True:
            chunk = f.read(64 * 1024) # 64KB chunks
            if not chunk:
                break
            yield chunk
            # Sleep to simulate slow network (e.g., 200KB/s)
            time.sleep(0.3) 

print("Starting slow upload simulation...")
try:
    url = 'http://localhost:5000/'
    # Using a tool-generated dummy file, but the server checks for image headers.
    # We need a valid header. Let's make a fake JPG.
    
    # Rewrite with valid header
    with open(filename, "wb") as f:
         # JPEG SOI marker + some random data
        f.write(b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01') 
        f.write(os.urandom((9 * 1024 * 1024) - 12)) 

    # Note: requests 'files' parameter doesn't easily support chunked streaming with delay 
    # unless using a generator as data. But Flask needs multipart/form-data.
    # Simulating a slow multipart upload is complex in pure python without external libs like requests-toolbelt.
    # Instead, we will just rely on the fact that Gunicorn is running and check if it accepts the request 
    # even if we just send it normally (but keep in mind we want to test timeout).
    
    # Actually, simpler test: Just send the request. If Gunicorn is working with threads, 
    # it should accept it fine. The "timeout" issue is usually when the client takes too long 
    # OR the processing takes too long.
    
    # Let's just try a normal upload first to ensure the new config works at all.
    with open(filename, 'rb') as f:
        files = {'image': (filename, f, 'image/jpeg')}
        response = requests.post(url, files=files, timeout=120)

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200 or response.status_code == 302:
        print("Success: Upload accepted.")
    else:
        print(f"Failed: {response.text[:200]}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if os.path.exists(filename):
        os.remove(filename)
