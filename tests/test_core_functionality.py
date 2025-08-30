"""Tests for core functionality that doesn't require Ursina initialization"""

import unittest
import tempfile
import os
import pickle
from unittest.mock import Mock, patch

from grahamcraft.world_manager import save_world, load_world


class TestCoreFunctionality(unittest.TestCase):
    """Test core business logic without GUI dependencies"""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pkl')
        self.temp_filename = self.temp_file.name
        self.temp_file.close()

    def tearDown(self) -> None:
        """Clean up."""
        try:
            os.unlink(self.temp_filename)
        except FileNotFoundError:
            pass

    def test_save_world_data_structure(self):
        """Test that save_world creates correct data structure"""
        # Create mock objects
        mock_voxel1 = Mock()
        mock_voxel1.position = (1, 2, 3)
        mock_voxel1.color = "red"
        
        mock_voxel2 = Mock()
        mock_voxel2.position = (4, 5, 6)
        mock_voxel2.color = "blue"
        
        voxels = [mock_voxel1, mock_voxel2]
        
        mock_player = Mock()
        mock_player.position = (10, 11, 12)
        
        mock_app = Mock()
        mock_app.has_gravity = True

        # Save world
        with patch('builtins.print'):
            save_world(voxels, mock_player, mock_app, self.temp_filename)

        # Load and verify data structure
        with open(self.temp_filename, 'rb') as f:
            data = pickle.load(f)

        expected_data = {
            "voxel_positions": [(1, 2, 3), (4, 5, 6)],
            "voxel_colors": ["red", "blue"],
            "player_position": (10, 11, 12),
            "has_gravity": True,
        }
        
        self.assertEqual(data, expected_data)

    def test_save_world_empty_voxels(self):
        """Test saving world with no voxels"""
        voxels = []
        mock_player = Mock()
        mock_player.position = (0, 0, 0)
        mock_app = Mock()
        mock_app.has_gravity = False

        with patch('builtins.print'):
            save_world(voxels, mock_player, mock_app, self.temp_filename)

        with open(self.temp_filename, 'rb') as f:
            data = pickle.load(f)

        expected_data = {
            "voxel_positions": [],
            "voxel_colors": [],
            "player_position": (0, 0, 0),
            "has_gravity": False,
        }
        
        self.assertEqual(data, expected_data)

    def test_load_world_file_not_found(self):
        """Test loading non-existent file"""
        voxels = []
        mock_player = Mock()
        mock_app = Mock()
        
        with patch('builtins.print') as mock_print:
            load_world(voxels, mock_player, mock_app, "nonexistent.pkl")
        
        mock_print.assert_called_once_with("Save file nonexistent.pkl not found")

    @patch('grahamcraft.world_manager.Voxel')
    @patch('grahamcraft.world_manager.destroy')
    def test_load_world_success(self, mock_destroy, mock_voxel_class):
        """Test successful world loading"""
        # First save a world
        test_data = {
            "voxel_positions": [(1, 2, 3)],
            "voxel_colors": ["green"],
            "player_position": (7, 8, 9),
            "has_gravity": False,
        }
        
        with open(self.temp_filename, 'wb') as f:
            pickle.dump(test_data, f)

        # Now test loading
        existing_voxel = Mock()
        voxels = [existing_voxel]
        mock_player = Mock()
        mock_app = Mock()
        
        mock_new_voxel = Mock()
        mock_voxel_class.return_value = mock_new_voxel

        with patch('builtins.print'):
            load_world(voxels, mock_player, mock_app, self.temp_filename)

        # Verify old voxel was destroyed
        mock_destroy.assert_called_once_with(existing_voxel)
        
        # Verify new voxel was created
        mock_voxel_class.assert_called_once_with(position=(1, 2, 3))
        self.assertEqual(mock_new_voxel.color, "green")
        
        # Verify player and app state
        self.assertEqual(mock_player.position, (7, 8, 9))
        self.assertEqual(mock_app.has_gravity, False)
        self.assertEqual(mock_player.gravity, 0)

    @patch('grahamcraft.world_manager.Voxel')
    @patch('grahamcraft.world_manager.destroy')
    def test_load_world_with_gravity(self, mock_destroy, mock_voxel_class):
        """Test loading world with gravity enabled"""
        test_data = {
            "voxel_positions": [],
            "voxel_colors": [],
            "player_position": (0, 0, 0),
            "has_gravity": True,
        }
        
        with open(self.temp_filename, 'wb') as f:
            pickle.dump(test_data, f)

        voxels = []
        mock_player = Mock()
        mock_app = Mock()

        with patch('builtins.print'):
            load_world(voxels, mock_player, mock_app, self.temp_filename)

        self.assertEqual(mock_app.has_gravity, True)
        self.assertEqual(mock_player.gravity, 1)

    def test_round_trip_save_load(self):
        """Test complete save/load cycle"""
        # Create test data
        mock_voxel1 = Mock()
        mock_voxel1.position = (10, 20, 30)
        mock_voxel1.color = "purple"
        
        original_voxels = [mock_voxel1]
        mock_player = Mock()
        mock_player.position = (100, 200, 300)
        mock_app = Mock()
        mock_app.has_gravity = True

        # Save
        with patch('builtins.print'):
            save_world(original_voxels, mock_player, mock_app, self.temp_filename)

        # Verify file exists and has correct size
        self.assertTrue(os.path.exists(self.temp_filename))
        self.assertGreater(os.path.getsize(self.temp_filename), 0)

        # Load raw data to verify structure
        with open(self.temp_filename, 'rb') as f:
            saved_data = pickle.load(f)

        self.assertEqual(len(saved_data["voxel_positions"]), 1)
        self.assertEqual(saved_data["voxel_positions"][0], (10, 20, 30))
        self.assertEqual(saved_data["voxel_colors"][0], "purple")
        self.assertEqual(saved_data["player_position"], (100, 200, 300))
        self.assertEqual(saved_data["has_gravity"], True)


if __name__ == '__main__':
    unittest.main()