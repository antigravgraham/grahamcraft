from ursina import scene, raycast, camera, mouse, destroy, color, Button, Ursina, held_keys, time
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()

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
app.has_gravity = True

class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        super().__init__(parent=scene,
            position=position,
            model='cube',
            origin_y=.5,
            texture='white_cube',
            color=color.hsv(0, 0, random.uniform(.9, 1.0)),
            highlight_color=color.lime,
        )

for z in range(8):
    for x in range(8):
        voxel = Voxel(position=(x,0,z))

def input(key):
    if key == 'left mouse down':
        hit_info = raycast(camera.world_position, camera.forward, distance=5)
        if hit_info.hit:
            Voxel(position=hit_info.entity.position + hit_info.normal)
    if key == 'right mouse down' and mouse.hovered_entity:
        destroy(mouse.hovered_entity)
    if key == 'escape':
        quit()
    if key == 'g':
        app.has_gravity = not app.has_gravity
        if app.has_gravity:
            player.gravity = 1
        else:
            player.gravity = 0

app.run()


