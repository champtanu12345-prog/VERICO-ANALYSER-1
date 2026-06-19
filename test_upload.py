#!/usr/bin/env python
import sys
import requests
from pathlib import Path

# Simple test to check if upload endpoint works
BASE_URL = "http://localhost:8000"

def test_upload():
    # Create a simple test PDF file
    test_file_path = Path("test_document.txt")
    test_file_path.write_text("This is a test document for uploading.")
    
    try:
        print("Testing upload endpoint...")
        with open(test_file_path, "rb") as f:
            files = {"files": f}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Upload test passed!")
        else:
            print("✗ Upload test failed!")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        test_file_path.unlink(missing_ok=True)

if __name__ == "__main__":
    test_upload()
