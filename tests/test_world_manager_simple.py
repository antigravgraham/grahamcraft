"""Simple tests for world_manager functions"""

import os
import pickle
import tempfile
import unittest
from unittest.mock import Mock, mock_open, patch

# Import after dependencies are available
from grahamcraft.world_manager import load_world, save_world


class TestWorldManagerSimple(unittest.TestCase):
    """Simple test cases for world_manager functions"""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pkl")
        self.temp_filename = self.temp_file.name
        self.temp_file.close()

    def tearDown(self) -> None:
        """Clean up."""
        try:
            os.unlink(self.temp_filename)
        except FileNotFoundError:
            pass

    def test_save_world_creates_file(self):
        """Test that save_world creates a file"""
        mock_voxels = []
        mock_player = Mock()
        mock_player.position = (1, 2, 3)
        mock_app = Mock()
        mock_app.has_gravity = True

        with patch("builtins.print"):
            save_world(mock_voxels, mock_player, mock_app, self.temp_filename)

        # Check file was created
        self.assertTrue(os.path.exists(self.temp_filename))

        # Check file contents
        with open(self.temp_filename, "rb") as f:
            data = pickle.load(f)

        self.assertIn("voxel_positions", data)
        self.assertIn("voxel_colors", data)
        self.assertIn("player_position", data)
        self.assertIn("has_gravity", data)
        self.assertEqual(data["player_position"], (1, 2, 3))
        self.assertEqual(data["has_gravity"], True)

    def test_load_world_nonexistent_file(self):
        """Test loading a file that doesn't exist"""
        mock_voxels = []
        mock_player = Mock()
        mock_app = Mock()

        with patch("builtins.print") as mock_print:
            load_world(mock_voxels, mock_player, mock_app, "nonexistent.pkl")

        mock_print.assert_called_once_with("Save file nonexistent.pkl not found")


if __name__ == "__main__":
    unittest.main()
