"""
Tests for the plugin architecture of the Markdown Decision Process.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Union

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from mdp.plugin_manager import PluginManager
from mdp.document import Document
from mdp.transformations import Transformation, TransformationPipeline

class MockTransformation(Transformation):
    """A mock transformation for testing."""
    
    def __init__(self, name="mock_transform"):
        self.name = name
    
    def __call__(self, document, **kwargs):
        # Create a modified document with a signal that this plugin was called
        new_content = document.get_content() + f"\n\n<!-- Processed by {self.name} -->\n"
        return Document(content=new_content)

    def apply(self, document: Document, output_path: Union[str, Path]) -> None:
        """Apply the mock transformation and save to output_path."""
        # This is required by the Transformation abstract class.
        # For testing TransformationPipeline, this method needs to be implemented.
        transformed_doc = self.__call__(document)
        transformed_doc.save(output_path)

class MockRewardFunction:
    """A mock reward function for testing."""
    
    def __init__(self, name="mock_reward", value=1.0):
        self.name = name
        self.value = value
    
    def __call__(self, document, transformation=None, params=None):
        return self.value

class MockPlugin:
    """A mock plugin for testing the plugin system."""
    
    def __init__(self, name="mock_plugin"):
        self.name = name
        self.transformations = {
            "mock_transform": MockTransformation(name),
            "another_transform": MockTransformation(f"{name}_another")
        }
        self.reward_functions = {
            "mock_reward": MockRewardFunction(name, 1.0),
            "negative_reward": MockRewardFunction(f"{name}_negative", -1.0)
        }
    
    def get_transformations(self):
        """Return the plugin's transformations."""
        return self.transformations
    
    def get_reward_functions(self):
        """Return the plugin's reward functions."""
        return self.reward_functions
    
    def initialize(self):
        """Initialize the plugin."""
        # This method would normally set up resources
        pass
    
    def cleanup(self):
        """Clean up the plugin resources."""
        # This method would normally clean up resources
        pass

class TestPluginManager(unittest.TestCase):
    """Tests for the PluginManager class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a sample document
        self.sample_content = "# Test Document\n\nThis is a test document for plugin testing.\n"
        self.document = Document(self.sample_content)
        
        # Create a plugin manager
        self.plugin_manager = PluginManager()
    
    def test_plugin_registration(self):
        """Test registering plugins."""
        # Create two mock plugins
        plugin1 = MockPlugin("plugin1")
        plugin2 = MockPlugin("plugin2")
        
        # Register the plugins
        self.plugin_manager.register_plugin("plugin1", plugin1)
        self.plugin_manager.register_plugin("plugin2", plugin2)
        
        # Check if plugins are registered
        self.assertIn("plugin1", self.plugin_manager.plugins)
        self.assertIn("plugin2", self.plugin_manager.plugins)
        
        # Check if transformations are registered
        transformations = self.plugin_manager.get_all_transformations()
        self.assertIn("plugin1.mock_transform", transformations)
        self.assertIn("plugin1.another_transform", transformations)
        self.assertIn("plugin2.mock_transform", transformations)
        self.assertIn("plugin2.another_transform", transformations)
        
        # Check if reward functions are registered
        reward_functions = self.plugin_manager.get_all_reward_functions()
        self.assertIn("plugin1.mock_reward", reward_functions)
        self.assertIn("plugin1.negative_reward", reward_functions)
        self.assertIn("plugin2.mock_reward", reward_functions)
        self.assertIn("plugin2.negative_reward", reward_functions)
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        # Create a mock plugin with patched initialize method
        plugin = MockPlugin("test_plugin")
        plugin.initialize = MagicMock()
        
        # Register the plugin
        self.plugin_manager.register_plugin("test_plugin", plugin)
        
        # Initialize all plugins
        self.plugin_manager.initialize_plugins()
        
        # Check if the initialize method was called
        plugin.initialize.assert_called_once()
    
    def test_plugin_cleanup(self):
        """Test plugin cleanup."""
        # Create a mock plugin with patched cleanup method
        plugin = MockPlugin("test_plugin")
        plugin.cleanup = MagicMock()
        
        # Register the plugin
        self.plugin_manager.register_plugin("test_plugin", plugin)
        
        # Clean up all plugins
        self.plugin_manager.cleanup_plugins()
        
        # Check if the cleanup method was called
        plugin.cleanup.assert_called_once()
    
    def test_plugin_transformation(self):
        """Test applying a plugin transformation."""
        # Create a mock plugin
        plugin = MockPlugin("test_plugin")
        
        # Register the plugin
        self.plugin_manager.register_plugin("test_plugin", plugin)
        
        # Get a transformation
        transform = self.plugin_manager.get_transformation("test_plugin.mock_transform")
        
        # Apply the transformation
        transformed_doc = transform(self.document)
        
        # Check if the transformation was applied
        self.assertIn("Processed by test_plugin", transformed_doc.content)
        self.assertNotEqual(self.document.content, transformed_doc.content)
    
    def test_plugin_reward_function(self):
        """Test using a plugin reward function."""
        # Create a mock plugin
        plugin = MockPlugin("test_plugin")
        
        # Register the plugin
        self.plugin_manager.register_plugin("test_plugin", plugin)
        
        # Get a reward function
        reward_fn = self.plugin_manager.get_reward_function("test_plugin.mock_reward")
        
        # Apply the reward function
        reward = reward_fn(self.document)
        
        # Check if the reward function returned the expected value
        self.assertEqual(reward, 1.0)
        
        # Get another reward function
        negative_reward_fn = self.plugin_manager.get_reward_function("test_plugin.negative_reward")
        
        # Apply the reward function
        reward = negative_reward_fn(self.document)
        
        # Check if the reward function returned the expected value
        self.assertEqual(reward, -1.0)
    
    def test_plugin_unregistration(self):
        """Test unregistering plugins."""
        # Create a mock plugin
        plugin = MockPlugin("test_plugin")
        
        # Register the plugin
        self.plugin_manager.register_plugin("test_plugin", plugin)
        
        # Check if the plugin is registered
        self.assertIn("test_plugin", self.plugin_manager.plugins)
        
        # Unregister the plugin
        self.plugin_manager.unregister_plugin("test_plugin")
        
        # Check if the plugin is unregistered
        self.assertNotIn("test_plugin", self.plugin_manager.plugins)
        
        # Check if transformations are unregistered
        transformations = self.plugin_manager.get_all_transformations()
        self.assertNotIn("test_plugin.mock_transform", transformations)
        
        # Check if reward functions are unregistered
        reward_functions = self.plugin_manager.get_all_reward_functions()
        self.assertNotIn("test_plugin.mock_reward", reward_functions)
    
    def test_transformation_sequence_with_plugins(self):
        """Test applying a sequence of transformations from plugins."""
        # Create mock plugins
        plugin1 = MockPlugin("plugin1")
        plugin2 = MockPlugin("plugin2")
        
        # Register plugins
        self.plugin_manager.register_plugin("plugin1", plugin1)
        self.plugin_manager.register_plugin("plugin2", plugin2)
        
        # Define a sequence of transformations using their registered names
        # These names should map to actual Transformation instances
        # For TransformationPipeline, we need instances, not names.
        
        # Get the actual transformation instances from the plugin manager
        transform1_instance = self.plugin_manager.get_transformation("plugin1.mock_transform")
        transform2_instance = self.plugin_manager.get_transformation("plugin2.another_transform")

        if not (transform1_instance and transform2_instance):
            self.fail("Could not retrieve mock transformations from plugin manager.")

        # Create a list of transformation instances for the pipeline
        transformation_instances_for_pipeline = [transform1_instance, transform2_instance]
        
        # Apply the transformation sequence using TransformationPipeline
        # This requires a temporary file for the output, as TransformationPipeline.apply writes to a file.
        import tempfile
        temp_output_path = Path(tempfile.gettempdir()) / "plugin_transformed_sequence.md"

        pipeline = TransformationPipeline(transformation_instances_for_pipeline)
        pipeline.apply(self.document, temp_output_path)
        
        transformed_doc = Document(file_path=temp_output_path)
        
        # Check if transformations were applied in order
        self.assertIn("Processed by plugin1", transformed_doc.get_content())
        self.assertIn("Processed by plugin2_another", transformed_doc.get_content())
        self.assertNotEqual(self.document.get_content(), transformed_doc.get_content())

        # Clean up temp file
        if temp_output_path.exists():
            temp_output_path.unlink()
    
    def test_plugin_discovery(self):
        """Test plugin discovery mechanism."""
        # Mock the plugin discovery function
        with patch('mdp.plugin_manager.PluginManager.discover_plugins') as mock_discover:
            # Set up mock plugins
            plugin1 = MockPlugin("discovered1")
            plugin2 = MockPlugin("discovered2")
            
            # Configure the mock to return these plugins
            mock_discover.return_value = {
                "discovered1": plugin1,
                "discovered2": plugin2
            }
            
            # Create a new plugin manager that will use the mocked discovery
            manager = PluginManager()
            
            # Discover plugins
            manager.load_plugins()
            
            # Check if the plugins were loaded
            self.assertIn("discovered1", manager.plugins)
            self.assertIn("discovered2", manager.plugins)
            
            # Verify the discovery function was called
            mock_discover.assert_called_once()

class TestPluginHooks(unittest.TestCase):
    """Tests for plugin hooks and integration points."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a sample document
        self.sample_content = "# Test Document\n\nThis is a test document for plugin testing.\n"
        self.document = Document(self.sample_content)
        
        # Create fixtures directory if it doesn't exist
        self.fixtures_dir = Path(__file__).parent / "fixtures"
        self.fixtures_dir.mkdir(exist_ok=True)
        
        # Path for plugin configurations
        self.config_path = self.fixtures_dir / "plugin_config.json"
    
    def test_plugin_configuration(self):
        """Test plugin configuration loading and application."""
        # Create a plugin manager
        plugin_manager = PluginManager()
        
        # Mock the configuration loading
        with patch('mdp.plugin_manager.PluginManager.load_configuration') as mock_load:
            # Set up mock configuration
            mock_config = {
                "plugins": {
                    "test_plugin": {
                        "enabled": True,
                        "settings": {
                            "param1": "value1",
                            "param2": 42
                        }
                    }
                }
            }
            
            # Configure the mock to return this configuration
            mock_load.return_value = mock_config
            
            # Create a mock plugin with a configuration method
            plugin = MockPlugin("test_plugin")
            plugin.configure = MagicMock()
            
            # Register the plugin
            plugin_manager.register_plugin("test_plugin", plugin)
            
            # Load and apply configuration
            plugin_manager.configure_plugins()
            
            # Check if the plugin's configure method was called with the settings
            plugin.configure.assert_called_once_with({"param1": "value1", "param2": 42})
    
    def test_plugin_event_hooks(self):
        """Test plugin event hook mechanism."""
        # Create a plugin manager with event hooks
        plugin_manager = PluginManager()
        
        # Create a mock plugin with event handlers
        plugin = MockPlugin("test_plugin")
        plugin.on_document_loaded = MagicMock()
        plugin.on_document_transformed = MagicMock()
        plugin.on_document_saved = MagicMock()
        
        # Register the plugin
        plugin_manager.register_plugin("test_plugin", plugin)
        
        # Trigger events
        plugin_manager.trigger_event("document_loaded", document=self.document)
        plugin_manager.trigger_event("document_transformed", document=self.document, 
                                    transformation_name="test")
        plugin_manager.trigger_event("document_saved", document=self.document, 
                                    path="test_path.md")
        
        # Check if the event handlers were called
        plugin.on_document_loaded.assert_called_once_with(document=self.document)
        plugin.on_document_transformed.assert_called_once_with(document=self.document, 
                                                             transformation_name="test")
        plugin.on_document_saved.assert_called_once_with(document=self.document, 
                                                       path="test_path.md")
    
    def test_plugin_lifecycle(self):
        """Test the complete plugin lifecycle."""
        # Create a plugin manager
        plugin_manager = PluginManager()
        
        # Create a mock plugin with lifecycle methods
        plugin = MockPlugin("lifecycle_plugin")
        plugin.initialize = MagicMock()
        plugin.configure = MagicMock()
        plugin.on_document_loaded = MagicMock()
        plugin.cleanup = MagicMock()
        
        # Register the plugin
        plugin_manager.register_plugin("lifecycle_plugin", plugin)
        
        # Mock configuration loading
        with patch('mdp.plugin_manager.PluginManager.load_configuration') as mock_load:
            mock_load.return_value = {
                "plugins": {
                    "lifecycle_plugin": {
                        "enabled": True,
                        "settings": {"param": "value"}
                    }
                }
            }
            
            # Initialize the plugin
            plugin_manager.initialize_plugins()
            plugin.initialize.assert_called_once()
            
            # Configure the plugin
            plugin_manager.configure_plugins()
            plugin.configure.assert_called_once_with({"param": "value"})
            
            # Trigger an event
            plugin_manager.trigger_event("document_loaded", document=self.document)
            plugin.on_document_loaded.assert_called_once_with(document=self.document)
            
            # Clean up
            plugin_manager.cleanup_plugins()
            plugin.cleanup.assert_called_once()

if __name__ == '__main__':
    unittest.main() 