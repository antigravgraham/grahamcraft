# Multiplayer GrahamCraft

Your game now supports multiplayer! Here's how to use it:

## Setup

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Start the server:**
   ```bash
   python start_server.py
   ```
   Or manually:
   ```bash
   python server.py
   ```
   The server will run on `http://localhost:5000`

3. **Start the game client:**
   ```bash
   python main.py
   ```

## How Multiplayer Works

- **Automatic Connection**: The game tries to connect to the server automatically
- **Fallback Mode**: If server isn't running, game starts in offline mode
- **Real-time Sync**: All players see each other's actions in real-time

## Multiplayer Features

- **Shared World**: All voxel placements/destruction synced across players
- **Player Visibility**: See other players as blue cubes with name tags
- **Synchronized Settings**: Gravity toggle affects all players
- **Persistent World**: Server saves/loads world state for all players

## Controls (Same as Single Player)

- **Arrow Keys**: Move around
- **Left Click**: Place voxel
- **Right Click**: Destroy voxel  
- **R/F**: Move up/down manually
- **G**: Toggle gravity (synced across all players)
- **K**: Save world (multiplayer format)
- **L**: Load world (multiplayer format)
- **Escape**: Quit and disconnect

## Running Multiple Clients

1. Start the server once: `python server.py`
2. Open multiple terminals and run `python main.py` in each
3. Each client connects as a separate player

## Troubleshooting

- **Connection Failed**: Make sure server is running first
- **Port Issues**: Server uses port 5000 by default
- **Dependencies**: Run `pip install flask-socketio python-socketio[client]` if needed

The game gracefully handles server disconnections and will continue working in offline mode.