# import random
import json

# from voxel import Voxel
import logging
import signal
import sys
from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, request
from flask_socketio import SocketIO, emit
from ursina import Vec3, color

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


# Basic configuration (sets up a StreamHandler to console by default)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Get a logger instance
logger: logging.Logger = logging.getLogger(__name__)

game_state: Dict[str, Any] = {"players": {}, "voxels": [], "world_settings": {"has_gravity": True}}


def signal_handler(sig: int, frame: Any) -> None:
    print("\nShutting down server gracefully...")
    sys.exit(0)


@socketio.on("connect")
def handle_connect() -> None:
    print(f"Client connected: {request.sid}")

    player_id = request.sid
    # game_state["players"][player_id] = {"position": [10, 1, 10], "color": "red"}
    game_state["players"][player_id] = {"position": [10, 1, 10], "color": [128, 0, 0, 1]}

    emit("game_state", game_state)
    emit(
        "player_joined",
        {"player_id": player_id, "player": game_state["players"][player_id]},
        broadcast=True,
    )


@socketio.on("disconnect")
def handle_disconnect() -> None:
    print(f"Client disconnected: {request.sid}")
    player_id = request.sid
    if player_id in game_state["players"]:
        del game_state["players"][player_id]
        emit("player_left", {"player_id": player_id}, broadcast=True)


@socketio.on("player_move")
def handle_player_move(data: Dict[str, Any]) -> None:
    player_id = request.sid
    if player_id in game_state["players"]:
        game_state["players"][player_id]["position"] = data["position"]
        emit(
            "player_moved",
            {"player_id": player_id, "position": data["position"]},
            broadcast=True,
            include_self=False,
        )


@socketio.on("voxel_place")
def handle_voxel_place(data: Dict[str, Any]) -> None:
    voxel_data = {
        "position": data["position"],
        "color": data["color"],
        "timestamp": datetime.now().isoformat(),
    }
    game_state["voxels"].append(voxel_data)
    emit("voxel_placed", voxel_data, broadcast=True)
    logger.info("voxel placed: ", str(voxel_data))


@socketio.on("voxel_destroy")
def handle_voxel_destroy(data: Dict[str, Any]) -> None:
    position = Vec3(tuple(data["position"]))
    game_state["voxels"] = [v for v in game_state["voxels"] if v["position"] != position]
    emit("voxel_destroyed", {"position": list(tuple(position))}, broadcast=True)
    logger.info("voxel destroyed")


@socketio.on("world_save")
def handle_world_save(data: Dict[str, Any]) -> None:
    filename = data.get("filename", "multiplayer_world.json")
    try:
        with open(filename, "w") as f:
            json.dump(game_state, f)
        emit("world_saved", {"filename": filename, "success": True})
    except Exception as e:
        emit("world_saved", {"filename": filename, "success": False, "error": str(e)})


@socketio.on("world_load")
def handle_world_load(data: Dict[str, Any]) -> None:
    filename = data.get("filename", "multiplayer_world.json")
    try:
        with open(filename, "r") as f:
            loaded_state = json.load(f)
            game_state["voxels"] = loaded_state.get("voxels", [])
            game_state["world_settings"] = loaded_state.get("world_settings", {"has_gravity": True})
        emit(
            "world_loaded",
            {"filename": filename, "success": True, "game_state": game_state},
            broadcast=True,
        )
    except Exception as e:
        emit("world_loaded", {"filename": filename, "success": False, "error": str(e)})


@socketio.on("gravity_toggle")
def handle_gravity_toggle() -> None:
    game_state["world_settings"]["has_gravity"] = not game_state["world_settings"]["has_gravity"]
    emit(
        "gravity_changed",
        {"has_gravity": game_state["world_settings"]["has_gravity"]},
        broadcast=True,
    )


def main() -> None:
    """Main entry point for the server"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Starting multiplayer server on http://localhost:5000")
    for z in range(20):
        for x in range(20):
            # voxel = Voxel(position=(x, 0, z))
            rcolor = color.random_color()

            voxel = {
                "position": (x, 0, z),
                "color": [rcolor.r, rcolor.g, rcolor.b, rcolor.brightness],
            }
            game_state["voxels"].append(voxel)

    socketio.run(app, host="0.0.0.0", port=5001, debug=True, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
