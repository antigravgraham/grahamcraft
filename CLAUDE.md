# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GrahamCraft is a multiplayer voxel-based game built with Python using the Ursina engine. The project supports both single-player offline mode and real-time multiplayer gameplay with a Flask-SocketIO server.

## Development Commands

### Setup and Installation
```bash
uv sync                               # Install dependencies
make dev-install                      # Install in development mode with entry points
```

### Running the Game
```bash
# Using module imports
uv run python -m grahamcraft.main    # Start game client
uv run python -m grahamcraft.start_server  # Start multiplayer server
uv run python -m grahamcraft.server  # Start server directly

# Using entry points (after dev-install)
uv run grahamcraft                    # Start game client
uv run grahamcraft-server             # Start multiplayer server

# Using Makefile
make install                          # Install dependencies only
make run                              # Start game client via module
make server                           # Start server via module
make run-entry                        # Start game client via entry point
make server-entry                     # Start server via entry point
```

## Architecture

### Module Structure

The project is organized as a Python package:
```
src/grahamcraft/
├── __init__.py
├── main.py                    # Main game entry point and input handling
├── network_manager.py         # Handles multiplayer networking with SocketIO client
├── server.py                  # Flask-SocketIO multiplayer server
├── start_server.py            # Server launcher script
├── world_manager.py           # World persistence (save/load) functionality
├── voxel.py                   # Individual voxel (block) entity
├── arrow_key_controller.py    # Player movement controller
├── character.py               # 3D character model
└── multiplayer_player.py      # Remote player representation
```

### Core Components

### Game Architecture Flow

1. **Game Initialization**: `grahamcraft.main` creates Ursina app, network manager, and player controller
2. **Connection Attempt**: Tries to connect to multiplayer server via NetworkManager
3. **Fallback Mode**: If server unavailable, creates local world and runs in offline mode
4. **Input Processing**: Mouse clicks for voxel placement/destruction, keyboard for movement and commands
5. **Network Sync**: All game actions (movement, voxel changes, world saves) sent to server if connected

### Multiplayer Architecture

- **Client-Server Model**: Multiple clients connect to central Flask-SocketIO server
- **Real-time Sync**: Player positions, voxel placement/destruction, and world settings synchronized
- **Persistent World**: Server maintains game state and can save/load world files
- **Graceful Degradation**: Clients fall back to offline mode if server unavailable

### Key Game Features

- **Voxel Building**: Left-click places voxels, right-click destroys them
- **Player Movement**: Arrow keys for horizontal movement, R/F for vertical
- **Gravity System**: Toggle with G key (synchronized in multiplayer)
- **World Persistence**: K to save, L to load (different formats for single/multiplayer)
- **Multiplayer Visibility**: Other players appear as blue cubes with name tags

## Important Files

- **pyproject.toml**: Project configuration, dependencies, and entry points
- **src/grahamcraft/**: Main module directory with all source code
- **world.pkl**: Default single-player world save file
- **multiplayer_world.json**: Default multiplayer world save file
- **models_compressed/**: Contains 3D model assets (character.bam, character.obj)
- **Makefile**: Development shortcuts for common tasks

## Network Configuration

- Default server URL: `http://192.168.1.243:5001` (configured in src/grahamcraft/network_manager.py:10)
- Default server port: 5001 (used by src/grahamcraft/server.py)
- Connection automatically falls back to offline mode on failure

## Development Notes

- Structured as a proper Python package with src/ layout
- Built on Ursina 3D engine for Python
- Uses relative imports within the grahamcraft module
- Uses pickle for single-player world persistence
- Uses JSON for multiplayer world persistence
- Server maintains centralized game state
- Client-side prediction not implemented (server authoritative)
- Entry points defined for easy command-line usage