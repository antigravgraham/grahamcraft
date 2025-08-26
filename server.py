import random
import signal
import sys
from flask import Flask, request
from flask_socketio import SocketIO, emit
import json
from datetime import datetime

from voxel import Voxel

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

game_state = {"players": {}, "voxels": [], "world_settings": {"has_gravity": True}}


def signal_handler(sig, frame):
    print('\nShutting down server gracefully...')
    sys.exit(0)


@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")

    player_id = request.sid
    game_state["players"][player_id] = {"position": [10, 1, 10], "color": "red"}

    emit("game_state", game_state)
    emit(
        "player_joined",
        {"player_id": player_id, "player": game_state["players"][player_id]},
        broadcast=True,
    )


@socketio.on("disconnect")
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    player_id = request.sid
    if player_id in game_state["players"]:
        del game_state["players"][player_id]
        emit("player_left", {"player_id": player_id}, broadcast=True)


@socketio.on("player_move")
def handle_player_move(data):
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
def handle_voxel_place(data):
    voxel_data = {
        "position": data["position"],
        "color": data["color"],
        "timestamp": datetime.now().isoformat(),
    }
    game_state["voxels"].append(voxel_data)
    emit("voxel_placed", voxel_data, broadcast=True)


@socketio.on("voxel_destroy")
def handle_voxel_destroy(data):
    position = data["position"]
    game_state["voxels"] = [
        v for v in game_state["voxels"] if v["position"] != position
    ]
    emit("voxel_destroyed", {"position": position}, broadcast=True)


@socketio.on("world_save")
def handle_world_save(data):
    filename = data.get("filename", "multiplayer_world.json")
    try:
        with open(filename, "w") as f:
            json.dump(game_state, f)
        emit("world_saved", {"filename": filename, "success": True})
    except Exception as e:
        emit("world_saved", {"filename": filename, "success": False, "error": str(e)})


@socketio.on("world_load")
def handle_world_load(data):
    filename = data.get("filename", "multiplayer_world.json")
    try:
        with open(filename, "r") as f:
            loaded_state = json.load(f)
            game_state["voxels"] = loaded_state.get("voxels", [])
            game_state["world_settings"] = loaded_state.get(
                "world_settings", {"has_gravity": True}
            )
        emit(
            "world_loaded",
            {"filename": filename, "success": True, "game_state": game_state},
            broadcast=True,
        )
    except Exception as e:
        emit("world_loaded", {"filename": filename, "success": False, "error": str(e)})


@socketio.on("gravity_toggle")
def handle_gravity_toggle():
    game_state["world_settings"]["has_gravity"] = not game_state["world_settings"][
        "has_gravity"
    ]
    emit(
        "gravity_changed",
        {"has_gravity": game_state["world_settings"]["has_gravity"]},
        broadcast=True,
    )


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting multiplayer server on http://localhost:5000")
    for z in range(20):
        for x in range(20):
            # voxel = Voxel(position=(x, 0, z))
            voxel = {
                "position": (x, 0, z),
                "color": random.choice(["red", "blue", "green"]),
            }
            game_state["voxels"].append(voxel)

    socketio.run(app, host="0.0.0.0", port=5001, debug=True, allow_unsafe_werkzeug=True)

