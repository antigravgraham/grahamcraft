from typing import Tuple

from ursina import Entity, Text, color, scene, Vec3


class MultiplayerPlayer(Entity):
    def __init__(
        self, position: Tuple[float, float, float] = (0, 1, 0), player_id: str = ""
    ) -> None:
        super().__init__(
            parent=scene, position=Vec3(position), model="cube", color=color.blue, scale=Vec3(0.8, 1.8, 0.8)
        )
        self.player_id: str = player_id

        self.name_tag: Text = Text(
            text=f"Player {player_id[:8]}",
            parent=self,
            position=(0, 1.2, 0),
            scale=2,
            color=color.white,
            billboard=True,
        )
