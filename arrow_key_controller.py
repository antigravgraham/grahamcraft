from ursina import held_keys, time
from ursina.prefabs.first_person_controller import FirstPersonController


class ArrowKeyController(FirstPersonController):
    def update(self):
        speed = self.speed * time.dt
        if held_keys["up arrow"]:
            self.position += self.forward * speed
        if held_keys["down arrow"]:
            self.position -= self.forward * speed
        if held_keys["left arrow"]:
            self.position -= self.right * speed
        if held_keys["right arrow"]:
            self.position += self.right * speed
        super().update()