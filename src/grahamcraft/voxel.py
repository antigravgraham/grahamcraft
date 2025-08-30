from typing import Tuple
from ursina import Button, scene, color


class Voxel(Button):
    def __init__(self, position: Tuple[float, float, float] = (0, 0, 0)) -> None:
        super().__init__(
            parent=scene,
            position=position,
            model="cube",
            origin_y=0.5,
            texture="white_cube",
            color=color.random_color(),
            highlight_color=color.lime,
        )