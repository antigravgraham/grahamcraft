import random
from typing import Tuple, List
from ursina import Entity, scene, color, invoke


class Character(Entity):
    def __init__(self, position: Tuple[float, float, float] = (0, 1, 0)) -> None:
        super().__init__(
            parent=scene,
            position=position,
            model="cube",
            color=color.red,
            scale=(0.8, 0.8, 0.8)
        )
        self.move_timer: float = 0
        invoke(self.random_move, delay=1)
    
    def random_move(self) -> None:
        directions: List[Tuple[int, int, int]] = [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
        direction = random.choice(directions)
        new_x = self.position[0] + direction[0]
        new_z = self.position[2] + direction[2]
        
        if 0 <= new_x < 20 and 0 <= new_z < 20:
            self.position = (new_x, 1, new_z)
        
        invoke(self.random_move, delay=1)