#!/usr/bin/env python
import uvicorn
import os
import subprocess
import sys

if __name__ == "__main__":
    # Run database initialization
    print("Initializing database...")
    try:
        init_result = subprocess.run([sys.executable, "init_db.py"], 
                                    cwd=os.path.dirname(os.path.abspath(__file__)), 
                                    check=True)
        if init_result.returncode != 0:
            print("Database initialization failed. Exiting.")
            sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error during database initialization. Exiting.")
        sys.exit(1)
    
    # Start the server
    print("Starting FastAPI server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, 
                ssl_keyfile="./key.pem", ssl_certfile="./cert.pem")
