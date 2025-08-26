#!/usr/bin/env python3

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask-socketio", "python-socketio[client]"])

def start_server():
    """Start the multiplayer server"""
    print("Starting multiplayer server...")
    subprocess.run([sys.executable, "server.py"])

if __name__ == "__main__":
    try:
        install_dependencies()
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped.")