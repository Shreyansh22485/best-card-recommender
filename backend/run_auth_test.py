#!/usr/bin/env python
"""
Script to run the authentication test with server startup and shutdown
"""
import subprocess
import time
import sys
import os
import signal
import platform
import shutil
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for self-signed certificates
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def run_command(command, check=True):
    """Run a command and return success status"""
    try:
        print(f"Running: {' '.join(command)}")
        subprocess.run(command, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: {e}")
        return False

def setup_environment():
    """Set up the test environment"""
    print("=== Setting up test environment ===")
    
    # Generate SSL certificates if they don't exist
    if not (os.path.exists("cert.pem") and os.path.exists("key.pem")):
        print("Generating SSL certificates...")
        if not run_command([sys.executable, "generate_cert.py"]):
            return False
    
    # Create test data (users, preferences)
    print("Creating test data...")
    if not run_command([sys.executable, "create_test_data.py"]):
        return False
    
    return True

def wait_for_server(url, max_retries=30, retry_interval=1):
    """Wait for the server to be available"""
    print(f"Waiting for server at {url}...")
    for i in range(max_retries):
        try:
            response = requests.get(url, verify=False, timeout=1)
            if response.status_code < 500:  # Accept any non-server error
                print(f"Server is up! (Status: {response.status_code})")
                return True
        except requests.RequestException:
            pass
        
        # Show progress every 5 seconds
        if i % 5 == 0 and i > 0:
            print(f"Still waiting... ({i} seconds)")
        
        time.sleep(retry_interval)
    
    print(f"Server failed to start after {max_retries} seconds")
    return False

def main():
    if not setup_environment():
        print("Environment setup failed. Exiting.")
        return 1
    
    # Start the server in the background
    print("\n=== Starting FastAPI server ===")
    if platform.system() == "Windows":
        server_process = subprocess.Popen(
            [sys.executable, "run.py"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        server_process = subprocess.Popen(
            [sys.executable, "run.py"],
            preexec_fn=os.setsid,
        )
    
    try:
        # Wait for server to start
        if not wait_for_server("https://localhost:8000/docs", max_retries=20):
            print("Server failed to start in time. Aborting test.")
            return 1
        
        # Run the authentication test
        print("\n=== Running authentication test ===")
        result = subprocess.run([sys.executable, "test_auth.py"], check=False)
        
        # Return the same exit code
        return result.returncode
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        return 1
    
    finally:
        # Terminate the server process
        print("\n=== Shutting down server ===")
        try:
            if platform.system() == "Windows":
                os.kill(server_process.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
            
            # Wait for the process to terminate
            server_process.wait(timeout=5)
            print("Server stopped successfully.")
        except Exception as e:
            print(f"Error shutting down server: {e}")
            # Force kill if normal termination fails
            if server_process.poll() is None:
                print("Force killing server process...")
                server_process.kill()
                server_process.wait(timeout=5)


if __name__ == "__main__":
    print("\n🔒 Best Card Recommender Auth Test Runner 🔒\n")
    exit_code = main()
    if exit_code == 0:
        print("\n✅ Authentication test completed successfully!")
    else:
        print("\n❌ Authentication test failed.")
    sys.exit(exit_code)
