"""Pytest configuration and shared fixtures for GrahamCraft tests"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


# Create comprehensive Ursina mocks
class MockUrsinaApp:
    """Mock Ursina application"""
    def __init__(self):
        self.has_gravity = True
        
class MockUrsinaEntity:
    """Mock Ursina Entity that doesn't require initialization"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if 'position' not in kwargs:
            self.position = (0, 0, 0)

class MockUrsinaButton(MockUrsinaEntity):
    """Mock Ursina Button"""
    pass

class MockUrsinaText(MockUrsinaEntity):
    """Mock Ursina Text"""
    pass
    
class MockFirstPersonController:
    """Mock FirstPersonController"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.position = (0, 0, 0)
        self.gravity = 1
        self.speed = 5.0
        self.forward = Mock()
        self.right = Mock()
        self.cursor = Mock()
        self.cursor.scale = 1.0
        
    def update(self):
        pass

@pytest.fixture(autouse=True)
def mock_ursina_imports():
    """Automatically mock Ursina imports for all tests"""
    mock_ursina = Mock()
    mock_scene = Mock()
    mock_color = Mock()
    mock_color.random_color.return_value = "random_color"
    mock_color.lime = "lime"
    mock_color.red = "red"
    mock_color.blue = "blue"
    mock_color.white = "white"
    
    mock_held_keys = Mock()
    mock_held_keys.__getitem__ = Mock(return_value=False)
    
    mock_time = Mock()
    mock_time.dt = 0.016
    
    mock_vec3 = Mock()
    mock_vec3.return_value = Mock()
    
    with patch.dict('sys.modules', {
        'ursina': mock_ursina,
        'ursina.scene': mock_scene, 
        'ursina.color': mock_color,
        'ursina.Button': MockUrsinaButton,
        'ursina.Entity': MockUrsinaEntity,
        'ursina.Text': MockUrsinaText,
        'ursina.Vec3': mock_vec3,
        'ursina.Color': Mock,
        'ursina.held_keys': mock_held_keys,
        'ursina.time': mock_time,
        'ursina.destroy': Mock(),
        'ursina.invoke': Mock(),
        'ursina.prefabs': Mock(),
        'ursina.prefabs.first_person_controller': Mock(),
        'ursina.prefabs.first_person_controller.FirstPersonController': MockFirstPersonController,
    }):
        # Also patch at the ursina module level
        with patch('ursina.scene', mock_scene), \
             patch('ursina.color', mock_color), \
             patch('ursina.Button', MockUrsinaButton), \
             patch('ursina.Entity', MockUrsinaEntity), \
             patch('ursina.Text', MockUrsinaText), \
             patch('ursina.held_keys', mock_held_keys), \
             patch('ursina.time', mock_time), \
             patch('ursina.destroy', Mock()), \
             patch('ursina.invoke', Mock()):
            yield


@pytest.fixture
def mock_ursina_app():
    """Provide a mock Ursina app for tests"""
    return MockUrsinaApp()

@pytest.fixture
def mock_network_manager():
    """Provide a mock network manager for tests"""
    mock_nm = Mock()
    mock_nm.connected = True
    mock_nm.player_id = "test_player_id"
    mock_nm.remote_players = {}
    mock_nm.voxels = []
    return mock_nm


@pytest.fixture
def mock_voxel():
    """Provide a mock voxel for tests"""
    mock_voxel = Mock()
    mock_voxel.position = (1, 2, 3)
    mock_voxel.color = "red"
    return mock_voxel


@pytest.fixture
def mock_player():
    """Provide a mock player for tests"""
    mock_player = Mock()
    mock_player.position = (10, 11, 12)
    mock_player.gravity = 1
    return mock_player


@pytest.fixture
def mock_app():
    """Provide a mock app for tests"""
    mock_app = Mock()
    mock_app.has_gravity = True
    return mock_app


@pytest.fixture
def sample_game_state():
    """Provide a sample game state for tests"""
    return {
        "players": {
            "player1": {"position": [1, 2, 3], "color": [1.0, 0.0, 0.0, 1.0]},
            "player2": {"position": [4, 5, 6], "color": [0.0, 1.0, 0.0, 1.0]}
        },
        "voxels": [
            {"position": [0, 0, 0], "color": [1.0, 1.0, 1.0]},
            {"position": [1, 0, 1], "color": [0.5, 0.5, 0.5]}
        ],
        "world_settings": {
            "has_gravity": True
        }
    }


@pytest.fixture
def mock_flask_app():
    """Provide a mock Flask app for server tests"""
    mock_app = Mock()
    mock_app.test_request_context.return_value.__enter__ = Mock()
    mock_app.test_request_context.return_value.__exit__ = Mock()
    return mock_app

# Pytest markers for test categories
pytest_markers = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for component interactions", 
    "slow": "Tests that take longer to run",
    "network": "Tests involving network operations",
    "file_io": "Tests involving file operations"
}