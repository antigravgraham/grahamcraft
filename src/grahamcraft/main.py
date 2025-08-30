from typing import Any, List

from ursina import (
    Ursina,
    camera,
    destroy,
    mouse,
    raycast,
    Vec3
)
from functools import partial
from random import randint
from .arrow_key_controller import ArrowKeyController
from .network_manager import NetworkManager
from .voxel import Voxel
from .world_manager import load_world, save_world


class Game:
    def __init__(self):
        self.app = Ursina()
        self.network_manager = NetworkManager()
        start_pos = Vec3(randint(10, 20), randint(10, 20), randint(10, 20))
        self.player = ArrowKeyController(initial_position=start_pos, gravity=1, network_manager=self.network_manager)
        self.network_manager.set_position_setter(self.player.set_player_position)
        self.player.cursor.scale = 0.00025
        self.has_gravity = True
        self.voxels: List[Voxel] = []
        
    def create_world(self) -> None:
        for z in range(20):
            for x in range(20):
                voxel = Voxel(position=(x, 0, z))
                self.voxels.append(voxel)

    def run(self) -> None:
        self.network_manager.set_game_objects(self.app, self.player, self.voxels)
        connected = self.network_manager.connect_to_server()
        if not connected:
            print("Failed to connect to multiplayer server. Starting in offline mode.")
            self.create_world()
        self.app.run()

game = Game()

def main() -> None:
    game.run()

def input(key, is_raw:bool=False) -> None:
    if key == "left mouse down":
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            new_position = hit_info.entity.position + hit_info.normal
            new_voxel = Voxel(position=new_position)
            game.voxels.append(new_voxel)
            game.network_manager.send_voxel_place(
                (new_position.x, new_position.y, new_position.z), new_voxel.color
            )
    if key == "right mouse down" and mouse.hovered_entity:
        if mouse.hovered_entity in game.voxels:
            position = mouse.hovered_entity.position
            game.voxels.remove(mouse.hovered_entity)
            game.network_manager.send_voxel_destroy(position)
        destroy(mouse.hovered_entity)
    if key == "escape":
        game.network_manager.disconnect_from_server()
        quit()
    if key == "r":
        (x, y, z) = game.player.position
        game.player.position = (x, y + 0.55, z)
        game.network_manager.send_player_move(game.player.position)
    if key == "f":
        (x, y, z) = game.player.position
        game.player.position = (x, y - 0.55, z)
        game.network_manager.send_player_move(game.player.position)

    if key == "g":
        game.network_manager.send_gravity_toggle()

    if key == "k":
        if game.network_manager.connected:
            game.network_manager.send_world_save("multiplayer_world.json")
        else:
            save_world(game.voxels, game.player, game.app)
    if key == "t":
        if game.network_manager.connected:
            game.network_manager.send_teleport(game.player.position)

    if key == "l":
        if game.network_manager.connected:
            game.network_manager.send_world_load("multiplayer_world.json")
        else:
            load_world(game.voxels, game.player, game.app)

if __name__ == "__main__":
    main()
