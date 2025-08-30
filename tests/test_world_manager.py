"""Tests for the world_manager module"""

import os
import pickle
import sys
import tempfile
import unittest
from unittest.mock import Mock, mock_open, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from grahamcraft.world_manager import load_world, save_world


class TestWorldManager(unittest.TestCase):
    """Test cases for world_manager functions"""

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        self.mock_voxel1 = Mock()
        self.mock_voxel1.position = (1, 2, 3)
        self.mock_voxel1.color = "red"

        self.mock_voxel2 = Mock()
        self.mock_voxel2.position = (4, 5, 6)
        self.mock_voxel2.color = "blue"

        self.voxels = [self.mock_voxel1, self.mock_voxel2]

        self.mock_player = Mock()
        self.mock_player.position = (10, 11, 12)

        self.mock_app = Mock()
        self.mock_app.has_gravity = True

    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    @patch("builtins.print")
    def test_save_world_default_filename(self, mock_print, mock_pickle_dump, mock_file):
        """Test saving world with default filename"""
        save_world(self.voxels, self.mock_player, self.mock_app)

        # Check file was opened with correct filename
        mock_file.assert_called_once_with("world.pkl", "wb")

        # Check pickle.dump was called with correct data
        expected_data = {
            "voxel_positions": [(1, 2, 3), (4, 5, 6)],
            "voxel_colors": ["red", "blue"],
            "player_position": (10, 11, 12),
            "has_gravity": True,
        }
        mock_pickle_dump.assert_called_once_with(
            expected_data, mock_file.return_value.__enter__.return_value
        )

        # Check print was called
        mock_print.assert_called_once_with("World saved to world.pkl")

    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    @patch("builtins.print")
    def test_save_world_custom_filename(self, mock_print, mock_pickle_dump, mock_file):
        """Test saving world with custom filename"""
        custom_filename = "custom_world.pkl"
        save_world(self.voxels, self.mock_player, self.mock_app, custom_filename)

        mock_file.assert_called_once_with(custom_filename, "wb")
        mock_print.assert_called_once_with(f"World saved to {custom_filename}")

    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    def test_save_world_no_gravity(self, mock_pickle_dump, mock_file):
        """Test saving world with gravity disabled"""
        self.mock_app.has_gravity = False

        save_world(self.voxels, self.mock_player, self.mock_app)

        expected_data = {
            "voxel_positions": [(1, 2, 3), (4, 5, 6)],
            "voxel_colors": ["red", "blue"],
            "player_position": (10, 11, 12),
            "has_gravity": False,
        }
        mock_pickle_dump.assert_called_once_with(
            expected_data, mock_file.return_value.__enter__.return_value
        )

    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.dump")
    def test_save_world_empty_voxels(self, mock_pickle_dump, mock_file):
        """Test saving world with no voxels"""
        empty_voxels = []

        save_world(empty_voxels, self.mock_player, self.mock_app)

        expected_data = {
            "voxel_positions": [],
            "voxel_colors": [],
            "player_position": (10, 11, 12),
            "has_gravity": True,
        }
        mock_pickle_dump.assert_called_once_with(
            expected_data, mock_file.return_value.__enter__.return_value
        )

    @patch("os.path.exists")
    @patch("builtins.print")
    def test_load_world_file_not_found(self, mock_print, mock_exists):
        """Test loading world when file doesn't exist"""
        mock_exists.return_value = False

        load_world(self.voxels, self.mock_player, self.mock_app)

        mock_print.assert_called_once_with("Save file world.pkl not found")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("grahamcraft.world_manager.destroy")
    @patch("grahamcraft.world_manager.Voxel")
    @patch("builtins.print")
    def test_load_world_success(
        self, mock_print, mock_voxel_class, mock_destroy, mock_pickle_load, mock_file, mock_exists
    ):
        """Test successfully loading a world"""
        mock_exists.return_value = True

        # Mock the loaded data
        mock_world_data = {
            "voxel_positions": [(1, 2, 3), (4, 5, 6)],
            "voxel_colors": ["red", "blue"],
            "player_position": (7, 8, 9),
            "has_gravity": False,
        }
        mock_pickle_load.return_value = mock_world_data

        # Mock voxel instances
        mock_voxel_instance1 = Mock()
        mock_voxel_instance2 = Mock()
        mock_voxel_class.side_effect = [mock_voxel_instance1, mock_voxel_instance2]

        # Create a mock voxel list that supports clear()
        voxels_list = [Mock(), Mock()]  # Existing voxels to be cleared

        load_world(voxels_list, self.mock_player, self.mock_app)

        # Check file operations
        mock_exists.assert_called_once_with("world.pkl")
        mock_file.assert_called_once_with("world.pkl", "rb")

        # Check old voxels were destroyed
        self.assertEqual(mock_destroy.call_count, 2)

        # Check new voxels were created
        self.assertEqual(mock_voxel_class.call_count, 2)
        mock_voxel_class.assert_any_call(position=(1, 2, 3))
        mock_voxel_class.assert_any_call(position=(4, 5, 6))

        # Check voxel colors were set
        mock_voxel_instance1.color = "red"
        mock_voxel_instance2.color = "blue"

        # Check player position was updated
        self.assertEqual(self.mock_player.position, (7, 8, 9))

        # Check app gravity was updated
        self.assertEqual(self.mock_app.has_gravity, False)
        self.assertEqual(self.mock_player.gravity, 0)

        mock_print.assert_called_once_with("World loaded from world.pkl")

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("grahamcraft.world_manager.destroy")
    @patch("grahamcraft.world_manager.Voxel")
    def test_load_world_with_gravity(
        self, mock_voxel_class, mock_destroy, mock_pickle_load, mock_file, mock_exists
    ):
        """Test loading world with gravity enabled"""
        mock_exists.return_value = True

        mock_world_data = {
            "voxel_positions": [],
            "voxel_colors": [],
            "player_position": (0, 0, 0),
            "has_gravity": True,
        }
        mock_pickle_load.return_value = mock_world_data

        load_world([], self.mock_player, self.mock_app)

        self.assertEqual(self.mock_app.has_gravity, True)
        self.assertEqual(self.mock_player.gravity, 1)

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=mock_open)
    @patch("pickle.load")
    @patch("grahamcraft.world_manager.destroy")
    @patch("grahamcraft.world_manager.Voxel")
    @patch("builtins.print")
    def test_load_world_custom_filename(
        self, mock_print, mock_voxel_class, mock_destroy, mock_pickle_load, mock_file, mock_exists
    ):
        """Test loading world with custom filename"""
        mock_exists.return_value = True
        custom_filename = "custom_world.pkl"

        mock_world_data = {
            "voxel_positions": [],
            "voxel_colors": [],
            "player_position": (0, 0, 0),
            "has_gravity": True,
        }
        mock_pickle_load.return_value = mock_world_data

        load_world([], self.mock_player, self.mock_app, custom_filename)

        mock_exists.assert_called_once_with(custom_filename)
        mock_file.assert_called_once_with(custom_filename, "rb")
        mock_print.assert_called_once_with(f"World loaded from {custom_filename}")


if __name__ == "__main__":
    unittest.main()
