import pickle
import os
from typing import List, Any
from ursina import destroy
from .voxel import Voxel


def save_world(voxels: List[Voxel], player: Any, app: Any, filename: str = "world.pkl") -> None:
    world_data = {
        "voxel_positions": [voxel.position for voxel in voxels],
        "voxel_colors": [voxel.color for voxel in voxels],
        "player_position": player.position,
        "has_gravity": app.has_gravity,
    }
    with open(filename, "wb") as f:
        pickle.dump(world_data, f)
    print(f"World saved to {filename}")


def load_world(voxels: List[Voxel], player: Any, app: Any, filename: str = "world.pkl") -> None:
    if not os.path.exists(filename):
        print(f"Save file {filename} not found")
        return

    for voxel in voxels[:]:
        destroy(voxel)
    voxels.clear()

    with open(filename, "rb") as f:
        world_data = pickle.load(f)

    for pos, col in zip(world_data["voxel_positions"], world_data["voxel_colors"]):
        voxel = Voxel(position=pos)
        voxel.color = col
        voxels.append(voxel)

    player.position = world_data["player_position"]
    app.has_gravity = world_data["has_gravity"]
    player.gravity = 1 if app.has_gravity else 0

    print(f"World loaded from {filename}")