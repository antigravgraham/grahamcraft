from ursina import (
    scene,
    raycast,
    camera,
    mouse,
    destroy,
    color,
    Ursina,
    application,
)
from arrow_key_controller import ArrowKeyController
from voxel import Voxel
from character import Character
from world_manager import save_world, load_world

app = Ursina()

application.blender_paths["default"] = (
    "/Applications/Blender.app/Contents/MacOS/Blender"
)



player = ArrowKeyController(gravity=1)
player.cursor.scale = 0.00025
app.has_gravity = True




voxels = []




for z in range(20):
    for x in range(20):
        voxel = Voxel(position=(x, 0, z))
        voxels.append(voxel)

character = Character(position=(10, 1, 10))


def input(key):
    if key == "left mouse down":
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            new_voxel = Voxel(position=hit_info.entity.position + hit_info.normal)
            voxels.append(new_voxel)
    if key == "right mouse down" and mouse.hovered_entity:
        if mouse.hovered_entity in voxels:
            voxels.remove(mouse.hovered_entity)
        destroy(mouse.hovered_entity)
    if key == "escape":
        quit()
    if key == "r":
        (x, y, z) = player.position
        player.position = (x, y + 0.55, z)
    if key == "f":
        (x, y, z) = player.position
        player.position = (x, y - 0.55, z)

    if key == "g":
        app.has_gravity = not app.has_gravity
        if app.has_gravity:
            player.gravity = 1
        else:
            player.gravity = 0

    if key == "k":
        save_world(voxels, player, app)

    if key == "l":
        load_world(voxels, player, app)


app.run()
