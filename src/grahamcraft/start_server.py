#!/usr/bin/env python3

import os
import subprocess
import sys


def install_dependencies() -> None:
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "flask-socketio", "python-socketio[client]"]
    )


def start_server() -> None:
    """Start the multiplayer server"""
    print("Starting multiplayer server...")
    # Import and run server directly instead of subprocess
    from . import server

    server.main()


def main() -> None:
    """Main entry point for the server launcher"""
    try:
        install_dependencies()
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
