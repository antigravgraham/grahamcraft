from typing import List

from ursina import (
    Ursina,
    camera,
    destroy,
    mouse,
    raycast,
    Vec3
)

from random import randint
from .arrow_key_controller import ArrowKeyController
from .network_manager import NetworkManager
from .voxel import Voxel
from .world_manager import load_world, save_world


# application.blender_paths["default"] = "/Applications/Blender.app/Contents/MacOS/Blender"

app = Ursina()
network_manager = NetworkManager()
start_pos = Vec3(randint(10, 20), randint(10, 20), randint(10, 20))
player = ArrowKeyController(initial_position=start_pos, gravity=1, network_manager=network_manager)
network_manager.set_position_setter(player.set_player_position)
player.cursor.scale = 0.00025
app.has_gravity = True
voxels: List[Voxel] = []


def input(key: str) -> None:
    if key == "left mouse down":
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            new_position = hit_info.entity.position + hit_info.normal
            new_voxel = Voxel(position=new_position)
            voxels.append(new_voxel)
            network_manager.send_voxel_place(
                (new_position.x, new_position.y, new_position.z), new_voxel.color
            )
    if key == "right mouse down" and mouse.hovered_entity:
        if mouse.hovered_entity in voxels:
            position = mouse.hovered_entity.position
            voxels.remove(mouse.hovered_entity)
            network_manager.send_voxel_destroy(list(position))
        destroy(mouse.hovered_entity)
    if key == "escape":
        network_manager.disconnect_from_server()
        quit()
    if key == "r":
        (x, y, z) = player.position
        player.position = (x, y + 0.55, z)
        network_manager.send_player_move(player.position)
    if key == "f":
        (x, y, z) = player.position
        player.position = (x, y - 0.55, z)
        network_manager.send_player_move(player.position)

    if key == "g":
        network_manager.send_gravity_toggle()

    if key == "k":
        if network_manager.connected:
            network_manager.send_world_save("multiplayer_world.json")
        else:
            save_world(voxels, player, app)
    if key == "t":
        if network_manager.connected:
            network_manager.send_teleport(player.position)


    if key == "l":
        if network_manager.connected:
            network_manager.send_world_load("multiplayer_world.json")
        else:
            load_world(voxels, player, app)


def create_world() -> None:
    for z in range(20):
        for x in range(20):
            voxel = Voxel(position=(x, 0, z))
            voxels.append(voxel)


def main() -> None:
    network_manager.set_game_objects(app, player, voxels)

    connected = network_manager.connect_to_server()

    if not connected:
        print("Failed to connect to multiplayer server. Starting in offline mode.")
        create_world()

    # character = Character(position=(10, 1, 10))
    app.run()


if __name__ == "__main__":
    main()
