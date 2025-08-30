from ursina import held_keys, time
from ursina.prefabs.first_person_controller import FirstPersonController


class ArrowKeyController(FirstPersonController):
    def __init__(self, network_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.network_manager = network_manager
        self.last_position = self.position
    
    def update(self):
        speed = self.speed * time.dt
        moved = False
        
        if held_keys["up arrow"]:
            self.position += self.forward * speed
            moved = True
        if held_keys["down arrow"]:
            self.position -= self.forward * speed
            moved = True
        if held_keys["left arrow"]:
            self.position -= self.right * speed
            moved = True
        if held_keys["right arrow"]:
            self.position += self.right * speed
            moved = True
        
        if moved and self.network_manager and self.network_manager.connected:
            if abs(self.position.x - self.last_position.x) > 0.01 or \
               abs(self.position.y - self.last_position.y) > 0.01 or \
               abs(self.position.z - self.last_position.z) > 0.01:
                self.network_manager.send_player_move(self.position)
                self.last_position = self.position
        
        super().update()