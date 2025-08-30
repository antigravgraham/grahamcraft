import socketio
import threading
from typing import Union, Tuple, Any
from ursina import destroy, Vec3, Color
from .voxel import Voxel
from .multiplayer_player import MultiplayerPlayer
import logging

class NetworkManager:
    def __init__(self, server_url="http://192.168.1.243:5001"):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.connected = False
        self.player_id = None
        self.remote_players = {}
        self.voxels = []
        self.app = None
        self.player = None

# Get a logger instance
        self.logger = logging.getLogger(__name__)
        self.setup_events()
    
    def setup_events(self):
        @self.sio.event
        def connect():
            self.logger.info("Connected to server")
            self.connected = True
        
        @self.sio.event
        def disconnect():
            self.logger.info("Disconnected from server")
            self.connected = False
        
        @self.sio.event
        def game_state(data):
            self.logger.info("Received initial game state:")
            print(data)
            self.load_game_state(data)
        
        @self.sio.event
        def player_joined(data):
            self.logger.info("player_joined")
            player_id = data["player_id"]
            player_data = data["player"]
            if player_id != self.player_id:
                self.add_remote_player(player_id, player_data)
        
        @self.sio.event
        def player_left(data):
            self.logger.info("player left")
            player_id = data["player_id"]
            self.remove_remote_player(player_id)
        
        @self.sio.event
        def player_moved(data):
            player_id = data["player_id"]
            position = data["position"]
            if player_id in self.remote_players:
                self.remote_players[player_id].position = tuple(position)
        
        @self.sio.event
        def voxel_placed(data):
            position = tuple(data["position"])
            self.logger.info(f"voxel placed: {position}")
            color = data["color"]
            voxel = Voxel(position=position)
            voxel.color = Color(color[0],color[1],color[2],1)
            self.voxels.append(voxel)
        
        @self.sio.event
        def voxel_destroyed(data):
            position = Vec3(tuple(data["position"]))
            for idx, voxel in enumerate(self.voxels):
                try:
                    if voxel.position == position:
                            self.voxels.pop(idx)
                            # destroy(voxel)
                            self.logger.info(f"voxel popped: {position}")
                except:
                    self.logger.info("already destroyed")

        
        @self.sio.event
        def world_loaded(data):
            if data["success"]:
                self.load_game_state(data["game_state"])
        
        @self.sio.event
        def gravity_changed(data):
            if self.app and self.player:
                self.app.has_gravity = data["has_gravity"]
                self.player.gravity = 1 if data["has_gravity"] else 0
    
    def connect_to_server(self):
        try:
            self.sio.connect(self.server_url)
            self.player_id = self.sio.sid
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def disconnect_from_server(self):
        if self.connected:
            self.sio.disconnect()
    
    def send_player_move(self, position):
        if self.connected:
            self.sio.emit('player_move', {"position": list(position)})
    
    def send_voxel_place(self, position: Tuple[float, float, float], color: Color) -> None:
        if self.connected:
            self.sio.emit('voxel_place', {
                "position": list(position),
                "color": [color.r, color.g, color.b]
            })
    
    def send_voxel_destroy(self, position: list[int]):
        if self.connected:
            self.sio.emit('voxel_destroy', {"position": position})
    
    def send_world_save(self, filename="multiplayer_world.json"):
        if self.connected:
            self.sio.emit('world_save', {"filename": filename})
    
    def send_world_load(self, filename="multiplayer_world.json"):
        if self.connected:
            self.sio.emit('world_load', {"filename": filename})
    
    def send_gravity_toggle(self):
        if self.connected:
            self.sio.emit('gravity_toggle')
    
    def load_game_state(self, game_state):
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
            voxel.color = Color(color[0],color[1],color[2],1)
            self.voxels.append(voxel)
            self.voxels.append(voxel)
        
        for player_id, player_data in game_state.get("players", {}).items():
            if player_id != self.player_id:
                self.add_remote_player(player_id, player_data)
        
        world_settings = game_state.get("world_settings", {})
        if self.app and self.player:
            self.app.has_gravity = world_settings.get("has_gravity", True)
            self.player.gravity = 1 if self.app.has_gravity else 0
    
    def add_remote_player(self, player_id, player_data):
        if player_id not in self.remote_players:
            position = tuple(player_data["position"])
            remote_player = MultiplayerPlayer(position=position, player_id=player_id)
            self.remote_players[player_id] = remote_player
    
    def remove_remote_player(self, player_id):
        if player_id in self.remote_players:
            destroy(self.remote_players[player_id])
            del self.remote_players[player_id]
    
    def set_game_objects(self, app, player, voxels):
        self.app = app
        self.player = player
        self.voxels = voxels