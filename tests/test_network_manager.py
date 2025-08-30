"""Tests for the NetworkManager class"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grahamcraft.network_manager import NetworkManager


class TestNetworkManager(unittest.TestCase):
    """Test cases for the NetworkManager class"""

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        with patch('grahamcraft.network_manager.socketio.Client'):
            with patch('grahamcraft.network_manager.logging.getLogger'):
                self.network_manager = NetworkManager()

    @patch('grahamcraft.network_manager.socketio.Client')
    @patch('grahamcraft.network_manager.logging.getLogger')
    def test_init_default_url(self, mock_logger, mock_client):
        """Test NetworkManager initialization with default server URL"""
        nm = NetworkManager()
        
        self.assertEqual(nm.server_url, "http://192.168.1.243:5001")
        self.assertFalse(nm.connected)
        self.assertIsNone(nm.player_id)
        self.assertEqual(nm.remote_players, {})
        self.assertEqual(nm.voxels, [])
        self.assertIsNone(nm.app)
        self.assertIsNone(nm.player)

    @patch('grahamcraft.network_manager.socketio.Client')
    @patch('grahamcraft.network_manager.logging.getLogger')
    def test_init_custom_url(self, mock_logger, mock_client):
        """Test NetworkManager initialization with custom server URL"""
        custom_url = "http://localhost:5000"
        nm = NetworkManager(server_url=custom_url)
        
        self.assertEqual(nm.server_url, custom_url)

    def test_connect_to_server_success(self):
        """Test successful server connection"""
        self.network_manager.sio.connect = Mock()
        self.network_manager.sio.sid = "test_session_id"
        
        result = self.network_manager.connect_to_server()
        
        self.assertTrue(result)
        self.assertEqual(self.network_manager.player_id, "test_session_id")
        self.network_manager.sio.connect.assert_called_once_with("http://192.168.1.243:5001")

    def test_connect_to_server_failure(self):
        """Test failed server connection"""
        self.network_manager.sio.connect = Mock(side_effect=Exception("Connection failed"))
        
        with patch('builtins.print') as mock_print:
            result = self.network_manager.connect_to_server()
        
        self.assertFalse(result)
        mock_print.assert_called_once_with("Failed to connect to server: Connection failed")

    def test_disconnect_from_server_when_connected(self):
        """Test disconnecting when connected"""
        self.network_manager.connected = True
        self.network_manager.sio.disconnect = Mock()
        
        self.network_manager.disconnect_from_server()
        
        self.network_manager.sio.disconnect.assert_called_once()

    def test_disconnect_from_server_when_not_connected(self):
        """Test disconnecting when not connected"""
        self.network_manager.connected = False
        self.network_manager.sio.disconnect = Mock()
        
        self.network_manager.disconnect_from_server()
        
        self.network_manager.sio.disconnect.assert_not_called()

    def test_send_player_move_when_connected(self):
        """Test sending player move when connected"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()
        position = (1.0, 2.0, 3.0)
        
        self.network_manager.send_player_move(position)
        
        self.network_manager.sio.emit.assert_called_once_with('player_move', {"position": [1.0, 2.0, 3.0]})

    def test_send_player_move_when_not_connected(self):
        """Test sending player move when not connected"""
        self.network_manager.connected = False
        self.network_manager.sio.emit = Mock()
        position = (1.0, 2.0, 3.0)
        
        self.network_manager.send_player_move(position)
        
        self.network_manager.sio.emit.assert_not_called()

    @patch('grahamcraft.network_manager.Color')
    def test_send_voxel_place_when_connected(self, mock_color):
        """Test sending voxel place when connected"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()
        
        mock_color_instance = Mock()
        mock_color_instance.r = 1.0
        mock_color_instance.g = 0.5
        mock_color_instance.b = 0.2
        
        position = (1.0, 2.0, 3.0)
        
        self.network_manager.send_voxel_place(position, mock_color_instance)
        
        expected_data = {
            "position": [1.0, 2.0, 3.0],
            "color": [1.0, 0.5, 0.2]
        }
        self.network_manager.sio.emit.assert_called_once_with('voxel_place', expected_data)

    def test_send_voxel_destroy_when_connected(self):
        """Test sending voxel destroy when connected"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()
        position = [1.0, 2.0, 3.0]
        
        self.network_manager.send_voxel_destroy(position)
        
        self.network_manager.sio.emit.assert_called_once_with('voxel_destroy', {"position": position})

    def test_send_world_save(self):
        """Test sending world save command"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()
        
        self.network_manager.send_world_save("test_world.json")
        
        self.network_manager.sio.emit.assert_called_once_with('world_save', {"filename": "test_world.json"})

    def test_send_world_load(self):
        """Test sending world load command"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()
        
        self.network_manager.send_world_load("test_world.json")
        
        self.network_manager.sio.emit.assert_called_once_with('world_load', {"filename": "test_world.json"})

    def test_send_gravity_toggle(self):
        """Test sending gravity toggle command"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()
        
        self.network_manager.send_gravity_toggle()
        
        self.network_manager.sio.emit.assert_called_once_with('gravity_toggle')

    @patch('grahamcraft.network_manager.destroy')
    @patch('grahamcraft.network_manager.Voxel')
    @patch('grahamcraft.network_manager.MultiplayerPlayer')
    @patch('grahamcraft.network_manager.Color')
    def test_load_game_state(self, mock_color, mock_multiplayer_player, mock_voxel, mock_destroy):
        """Test loading game state from server"""
        # Setup existing objects to be cleared
        existing_voxel = Mock()
        existing_player = Mock()
        self.network_manager.voxels = [existing_voxel]
        self.network_manager.remote_players = {"old_player": existing_player}
        self.network_manager.player_id = "current_player"
        
        # Setup mock objects
        mock_app = Mock()
        mock_player = Mock()
        self.network_manager.app = mock_app
        self.network_manager.player = mock_player
        
        # Mock game state data
        game_state = {
            "voxels": [
                {"position": [1, 2, 3], "color": [1.0, 0.0, 0.0]},
                {"position": [4, 5, 6], "color": [0.0, 1.0, 0.0]}
            ],
            "players": {
                "current_player": {"position": [0, 0, 0]},
                "remote_player": {"position": [10, 10, 10]}
            },
            "world_settings": {"has_gravity": False}
        }
        
        mock_voxel_instance1 = Mock()
        mock_voxel_instance2 = Mock()
        mock_voxel.side_effect = [mock_voxel_instance1, mock_voxel_instance2, mock_voxel_instance1, mock_voxel_instance2]
        
        mock_remote_player = Mock()
        mock_multiplayer_player.return_value = mock_remote_player
        
        self.network_manager.load_game_state(game_state)
        
        # Check old objects were destroyed
        mock_destroy.assert_any_call(existing_voxel)
        mock_destroy.assert_any_call(existing_player)
        
        # Check voxels were created (note: there's a bug in the original code that duplicates voxels)
        self.assertEqual(mock_voxel.call_count, 4)  # Due to duplicate append
        
        # Check remote player was added (but not current player)
        mock_multiplayer_player.assert_called_once_with(position=(10, 10, 10), player_id="remote_player")
        self.assertEqual(self.network_manager.remote_players["remote_player"], mock_remote_player)
        
        # Check world settings were applied
        self.assertEqual(mock_app.has_gravity, False)
        self.assertEqual(mock_player.gravity, 0)

    @patch('grahamcraft.network_manager.MultiplayerPlayer')
    def test_add_remote_player(self, mock_multiplayer_player):
        """Test adding a remote player"""
        mock_player = Mock()
        mock_multiplayer_player.return_value = mock_player
        
        player_id = "test_player"
        player_data = {"position": [5, 6, 7]}
        
        self.network_manager.add_remote_player(player_id, player_data)
        
        mock_multiplayer_player.assert_called_once_with(position=(5, 6, 7), player_id=player_id)
        self.assertEqual(self.network_manager.remote_players[player_id], mock_player)

    def test_add_remote_player_already_exists(self):
        """Test adding a remote player that already exists"""
        existing_player = Mock()
        player_id = "existing_player"
        self.network_manager.remote_players[player_id] = existing_player
        
        with patch('grahamcraft.network_manager.MultiplayerPlayer') as mock_multiplayer_player:
            self.network_manager.add_remote_player(player_id, {"position": [1, 2, 3]})
        
        # Should not create new player
        mock_multiplayer_player.assert_not_called()
        self.assertEqual(self.network_manager.remote_players[player_id], existing_player)

    @patch('grahamcraft.network_manager.destroy')
    def test_remove_remote_player(self, mock_destroy):
        """Test removing a remote player"""
        player = Mock()
        player_id = "test_player"
        self.network_manager.remote_players[player_id] = player
        
        self.network_manager.remove_remote_player(player_id)
        
        mock_destroy.assert_called_once_with(player)
        self.assertNotIn(player_id, self.network_manager.remote_players)

    def test_remove_remote_player_not_exists(self):
        """Test removing a remote player that doesn't exist"""
        with patch('grahamcraft.network_manager.destroy') as mock_destroy:
            self.network_manager.remove_remote_player("nonexistent_player")
        
        mock_destroy.assert_not_called()

    def test_set_game_objects(self):
        """Test setting game objects"""
        mock_app = Mock()
        mock_player = Mock()
        mock_voxels = [Mock(), Mock()]
        
        self.network_manager.set_game_objects(mock_app, mock_player, mock_voxels)
        
        self.assertEqual(self.network_manager.app, mock_app)
        self.assertEqual(self.network_manager.player, mock_player)
        self.assertEqual(self.network_manager.voxels, mock_voxels)


if __name__ == '__main__':
    unittest.main()