import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import socketio
from ursina import Color, Vec3, destroy

from .multiplayer_player import MultiplayerPlayer
from .voxel import Voxel


class NetworkManager:
    def __init__(self, server_url: str = "http://192.168.1.243:5001", position_setter: Optional[Callable[[Vec3], None]] = None) -> None:
        self.sio: socketio.Client = socketio.Client()
        self.server_url: str = server_url
        self.connected: bool = False
        self.player_id: Optional[str] = None
        self.remote_players: Dict[str, MultiplayerPlayer] = {}
        self.voxels: List[Voxel] = []
        self.app: Any = None
        self.player: Any = None
        self.position_setter: Optional[Callable[[Vec3], None]] = position_setter

        # Get a logger instance
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.setup_events()

    def set_position_setter(self, position_setter: Callable[[Vec3], None]) -> None:
        self.position_setter = position_setter

    def setup_events(self) -> None:
        @self.sio.event
        def connect() -> None:
            self.logger.info("Connected to server")
            self.connected = True

        @self.sio.event
        def disconnect() -> None:
            self.logger.info("Disconnected from server")
            self.connected = False

        @self.sio.event
        def game_state(data: Dict[str, Any]) -> None:
            self.logger.info("Received initial game state:")
            print(data)
            self.load_game_state(data)

        @self.sio.event
        def player_joined(data: Dict[str, Any]) -> None:
            self.logger.info("player_joined")
            player_id = data["player_id"]
            player_data = data["player"]
            if player_id != self.player_id:
                self.add_remote_player(player_id, player_data)

        @self.sio.event
        def player_left(data: Dict[str, Any]) -> None:
            self.logger.info("player left")
            player_id = data["player_id"]
            self.remove_remote_player(player_id)

        @self.sio.event
        def player_moved(data: Dict[str, Any]) -> None:
            player_id = data["player_id"]
            position = data["position"]
            if player_id in self.remote_players:
                self.remote_players[player_id].position = tuple(position)

        @self.sio.event
        def player_teleported(data: Dict[str, Any]) -> None:
            position = data["position"]
            if self.position_setter:
                self.position_setter(position)

        @self.sio.event
        def voxel_placed(data: Dict[str, Any]) -> None:
            position = tuple(data["position"])
            self.logger.info(f"voxel placed: {position}")
            color = data["color"]
            voxel = Voxel(position=position)
            voxel.color = Color(color[0], color[1], color[2], 1)
            self.voxels.append(voxel)

        @self.sio.event
        def voxel_destroyed(data: Dict[str, Any]) -> None:
            position = Vec3(tuple(data["position"]))
            for idx, voxel in enumerate(self.voxels):
                try:
                    if voxel.position == position:
                        self.voxels.pop(idx)
                        self.logger.info(f"voxel popped: {position}")
                        destroy(voxel)
                except Exception as e:
                    self.logger.warning(f"Exception while destroying voxel: {e}")

        @self.sio.event
        def world_loaded(data: Dict[str, Any]) -> None:
            if data["success"]:
                self.load_game_state(data["game_state"])

        @self.sio.event
        def gravity_changed(data: Dict[str, Any]) -> None:
            self.player.gravity = 1 if data["has_gravity"] else 0

    def connect_to_server(self) -> bool:
        try:
            self.sio.connect(self.server_url)
            self.player_id = self.sio.sid
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def disconnect_from_server(self) -> None:
        if self.connected:
            self.sio.disconnect()

    def send_teleport(self, position: Tuple[float, float, float]) -> None:
        if self.connected:
            self.sio.emit("player_teleport", {"position": list(position)})

    def send_player_move(self, position: Tuple[float, float, float]) -> None:
        if self.connected:
            self.sio.emit("player_move", {"position": list(position)})

    def send_voxel_place(self, position: Tuple[float, float, float], color: Color) -> None:
        if self.connected:
            self.sio.emit(
                "voxel_place", {"position": list(position), "color": [color.r, color.g, color.b]}
            )

    def send_voxel_destroy(self, position: Tuple[float, float, float]) -> None:
        if self.connected:
            self.sio.emit("voxel_destroy", {"position": list(position)})

    def send_world_save(self, filename: str = "multiplayer_world.json") -> None:
        if self.connected:
            self.sio.emit("world_save", {"filename": filename})

    def send_world_load(self, filename: str = "multiplayer_world.json") -> None:
        if self.connected:
            self.sio.emit("world_load", {"filename": filename})

    def send_gravity_toggle(self) -> None:
        if self.connected:
            self.sio.emit("gravity_toggle")

    def load_game_state(self, game_state: Dict[str, Any]) -> None:
        for voxel in self.voxels[:]:
            destroy(voxel)
        self.voxels.clear()

        for remote_player in self.remote_players.values():
            destroy(remote_player)
        self.remote_players.clear()

        for voxel_data in game_state.get("voxels", []):
            position = tuple(voxel_data["position"])
            color = voxel_data["color"]
            voxel = Voxel(position=position)
            voxel.color = Color(color[0], color[1], color[2], 1)
            self.voxels.append(voxel)

        for player_id, player_data in game_state.get("players", {}).items():
            if player_id != self.player_id:
                self.add_remote_player(player_id, player_data)

        world_settings = game_state.get("world_settings", {})
        if self.app and self.player:
            self.app.has_gravity = world_settings.get("has_gravity", True)
            self.player.gravity = 1 if self.app.has_gravity else 0

    def add_remote_player(self, player_id: str, player_data: Dict[str, Any]) -> None:
        if player_id not in self.remote_players:
            position = tuple(player_data["position"])
            remote_player = MultiplayerPlayer(position=position, player_id=player_id)
            self.remote_players[player_id] = remote_player

    def remove_remote_player(self, player_id: str) -> None:
        if player_id in self.remote_players:
            destroy(self.remote_players[player_id])
            del self.remote_players[player_id]

    def set_game_objects(self, app: Any, player: Any, voxels: List[Voxel]) -> None:
        self.app = app
        self.player = player
        self.voxels = voxels
