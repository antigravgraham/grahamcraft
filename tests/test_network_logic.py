"""Tests for NetworkManager core logic"""

import unittest
from unittest.mock import Mock, patch

# We can import NetworkManager since socketio is now available
from grahamcraft.network_manager import NetworkManager


class TestNetworkLogic(unittest.TestCase):
    """Test NetworkManager core logic without actual network connections"""

    def setUp(self) -> None:
        """Set up test fixtures."""
        with patch('socketio.Client'):
            with patch('logging.getLogger'):
                self.network_manager = NetworkManager("http://test:5000")

    def test_init_sets_properties(self):
        """Test NetworkManager initialization"""
        self.assertEqual(self.network_manager.server_url, "http://test:5000")
        self.assertFalse(self.network_manager.connected)
        self.assertIsNone(self.network_manager.player_id)
        self.assertEqual(self.network_manager.remote_players, {})
        self.assertEqual(self.network_manager.voxels, [])

    def test_init_default_url(self):
        """Test NetworkManager with default URL"""
        with patch('socketio.Client'):
            with patch('logging.getLogger'):
                nm = NetworkManager()
        
        self.assertEqual(nm.server_url, "http://192.168.1.243:5001")

    def test_connect_success(self):
        """Test successful connection"""
        self.network_manager.sio.connect = Mock()
        self.network_manager.sio.sid = "test_session_id"

        result = self.network_manager.connect_to_server()

        self.assertTrue(result)
        self.assertEqual(self.network_manager.player_id, "test_session_id")
        self.network_manager.sio.connect.assert_called_once_with("http://test:5000")

    def test_connect_failure(self):
        """Test failed connection"""
        self.network_manager.sio.connect = Mock(side_effect=Exception("Connection refused"))

        with patch('builtins.print') as mock_print:
            result = self.network_manager.connect_to_server()

        self.assertFalse(result)
        mock_print.assert_called_once_with("Failed to connect to server: Connection refused")

    def test_disconnect_when_connected(self):
        """Test disconnect when connected"""
        self.network_manager.connected = True
        self.network_manager.sio.disconnect = Mock()

        self.network_manager.disconnect_from_server()

        self.network_manager.sio.disconnect.assert_called_once()

    def test_disconnect_when_not_connected(self):
        """Test disconnect when not connected"""
        self.network_manager.connected = False
        self.network_manager.sio.disconnect = Mock()

        self.network_manager.disconnect_from_server()

        self.network_manager.sio.disconnect.assert_not_called()

    def test_send_player_move_connected(self):
        """Test sending player move when connected"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()

        self.network_manager.send_player_move((1.0, 2.0, 3.0))

        self.network_manager.sio.emit.assert_called_once_with(
            'player_move', {"position": [1.0, 2.0, 3.0]}
        )

    def test_send_player_move_disconnected(self):
        """Test sending player move when disconnected"""
        self.network_manager.connected = False
        self.network_manager.sio.emit = Mock()

        self.network_manager.send_player_move((1.0, 2.0, 3.0))

        self.network_manager.sio.emit.assert_not_called()

    def test_send_voxel_place_connected(self):
        """Test sending voxel place when connected"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()

        mock_color = Mock()
        mock_color.r = 1.0
        mock_color.g = 0.5
        mock_color.b = 0.2

        self.network_manager.send_voxel_place((10, 20, 30), mock_color)

        expected_data = {
            "position": [10, 20, 30],
            "color": [1.0, 0.5, 0.2]
        }
        self.network_manager.sio.emit.assert_called_once_with('voxel_place', expected_data)

    def test_send_voxel_destroy(self):
        """Test sending voxel destroy command"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()

        self.network_manager.send_voxel_destroy([5, 6, 7])

        self.network_manager.sio.emit.assert_called_once_with(
            'voxel_destroy', {"position": [5, 6, 7]}
        )

    def test_send_world_save(self):
        """Test sending world save command"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()

        self.network_manager.send_world_save("my_world.json")

        self.network_manager.sio.emit.assert_called_once_with(
            'world_save', {"filename": "my_world.json"}
        )

    def test_send_world_load(self):
        """Test sending world load command"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()

        self.network_manager.send_world_load("my_world.json")

        self.network_manager.sio.emit.assert_called_once_with(
            'world_load', {"filename": "my_world.json"}
        )

    def test_send_gravity_toggle(self):
        """Test sending gravity toggle command"""
        self.network_manager.connected = True
        self.network_manager.sio.emit = Mock()

        self.network_manager.send_gravity_toggle()

        self.network_manager.sio.emit.assert_called_once_with('gravity_toggle')

    def test_set_game_objects(self):
        """Test setting game objects"""
        mock_app = Mock()
        mock_player = Mock()
        mock_voxels = [Mock(), Mock()]

        self.network_manager.set_game_objects(mock_app, mock_player, mock_voxels)

        self.assertEqual(self.network_manager.app, mock_app)
        self.assertEqual(self.network_manager.player, mock_player)
        self.assertEqual(self.network_manager.voxels, mock_voxels)

    @patch('grahamcraft.network_manager.MultiplayerPlayer')
    def test_add_remote_player(self, mock_mp_class):
        """Test adding a remote player"""
        mock_player = Mock()
        mock_mp_class.return_value = mock_player

        player_data = {"position": [1, 2, 3]}
        self.network_manager.add_remote_player("test_player", player_data)

        mock_mp_class.assert_called_once_with(position=(1, 2, 3), player_id="test_player")
        self.assertEqual(self.network_manager.remote_players["test_player"], mock_player)

    def test_add_remote_player_already_exists(self):
        """Test adding remote player that already exists"""
        existing_player = Mock()
        self.network_manager.remote_players["existing"] = existing_player

        with patch('grahamcraft.network_manager.MultiplayerPlayer') as mock_mp_class:
            self.network_manager.add_remote_player("existing", {"position": [1, 2, 3]})

        # Should not create new player
        mock_mp_class.assert_not_called()
        self.assertEqual(self.network_manager.remote_players["existing"], existing_player)

    @patch('grahamcraft.network_manager.destroy')
    def test_remove_remote_player(self, mock_destroy):
        """Test removing a remote player"""
        mock_player = Mock()
        self.network_manager.remote_players["test_player"] = mock_player

        self.network_manager.remove_remote_player("test_player")

        mock_destroy.assert_called_once_with(mock_player)
        self.assertNotIn("test_player", self.network_manager.remote_players)

    def test_remove_remote_player_not_exists(self):
        """Test removing non-existent remote player"""
        with patch('grahamcraft.network_manager.destroy') as mock_destroy:
            self.network_manager.remove_remote_player("nonexistent")

        mock_destroy.assert_not_called()


if __name__ == '__main__':
    unittest.main()