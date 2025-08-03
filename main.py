from ursina import scene, raycast, camera, mouse, destroy, color, Button, Ursina, held_keys, time, Entity, application
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import pickle
import os

app = Ursina()

application.blender_paths['default'] = '/Applications/Blender.app/Contents/MacOS/Blender'

class ArrowKeyController(FirstPersonController):
    def update(self):
        speed = self.speed * time.dt
        if held_keys['up arrow']:
            self.position += self.forward * speed
        if held_keys['down arrow']:
            self.position -= self.forward * speed
        if held_keys['left arrow']:
            self.position -= self.right * speed
        if held_keys['right arrow']:
            self.position += self.right * speed
        super().update()

player = ArrowKeyController(gravity=1)
player.cursor.scale = 0.00025  
app.has_gravity = True


# mymodel=Entity(model="character.obj",scale=0.1, texture=("Grass.png"))
my_model = Entity(model='character.blend')

class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture='white_cube',
            # color=color.hsv(0, 0, random.uniform(.9, 1.0)),
            color=color.random_color(),
            highlight_color=color.lime,
        )

voxels = []

def save_world(filename='world.pkl'):
    world_data = {
        'voxel_positions': [voxel.position for voxel in voxels],
        'voxel_colors': [voxel.color for voxel in voxels],
        'player_position': player.position,
        'has_gravity': app.has_gravity
    }
    with open(filename, 'wb') as f:
        pickle.dump(world_data, f)
    print(f"World saved to {filename}")

def load_world(filename='world.pkl'):
    if not os.path.exists(filename):
        print(f"Save file {filename} not found")
        return
    
    for voxel in voxels[:]:
        destroy(voxel)
    voxels.clear()
    
    with open(filename, 'rb') as f:
        world_data = pickle.load(f)
    
    for pos, col in zip(world_data['voxel_positions'], world_data['voxel_colors']):
        voxel = Voxel(position=pos)
        voxel.color = col
        voxels.append(voxel)
    
    player.position = world_data['player_position']
    app.has_gravity = world_data['has_gravity']
    player.gravity = 1 if app.has_gravity else 0
    
    print(f"World loaded from {filename}")

for z in range(20):
    for x in range(20):
        voxel = Voxel(position=(x,0,z))
        voxels.append(voxel)

def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            new_voxel = Voxel(position=hit_info.entity.position + hit_info.normal)
            voxels.append(new_voxel)
    if key == 'right mouse down' and mouse.hovered_entity:
        if mouse.hovered_entity in voxels:
            voxels.remove(mouse.hovered_entity)
        destroy(mouse.hovered_entity)
    if key == 'escape':
        quit()
    if key == 'r':
        (x,y,z) = player.position
        player.position = (x,y + 0.55 ,z)
    if key == 'f':
        (x,y,z) = player.position
        player.position = (x,y - 0.55 ,z)

    if key == 'g':
        app.has_gravity = not app.has_gravity
        if app.has_gravity:
            player.gravity = 1
        else:
            player.gravity = 0
    
    if key == 'k':
        save_world()
    
    if key == 'l':
        load_world()

app.run()


