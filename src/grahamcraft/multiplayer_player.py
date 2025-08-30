from ursina import Entity, scene, color, Text

class MultiplayerPlayer(Entity):
    def __init__(self, position=(0, 1, 0), player_id=""):
        super().__init__(
            parent=scene,
            position=position,
            model="cube",
            color=color.blue,
            scale=(0.8, 1.8, 0.8)
        )
        self.player_id = player_id
        
        self.name_tag = Text(
            text=f"Player {player_id[:8]}",
            parent=self,
            position=(0, 1.2, 0),
            scale=2,
            color=color.white,
            billboard=True
        )