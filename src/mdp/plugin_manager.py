"""
Plugin manager for the Markdown Decision Process.

This module provides plugin support for extending MDP functionality with custom
transformations, reward functions, and other components.
"""

import importlib
import json
import inspect
import logging
import os
import pkgutil
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

logger = logging.getLogger(__name__)

class PluginManager:
    """
    Plugin manager for the Markdown Decision Process.
    
    This class manages the discovery, loading, and lifecycle of plugins that extend
    the functionality of the Markdown Decision Process. Plugins can provide custom
    transformations, reward functions, and other components.
    """
    
    def __init__(self, plugin_dir: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the plugin manager.
        
        Args:
            plugin_dir: Optional directory to search for plugins. If None, uses default locations.
            config_path: Optional path to the plugin configuration file. If None, uses default.
        """
        self.plugins = {}  # Dictionary of registered plugins
        self.transformations = {}  # Dictionary of registered transformations
        self.reward_functions = {}  # Dictionary of registered reward functions
        
        # Set default plugin directory if not provided
        if plugin_dir is None:
            # Look for plugins in the user's home directory and in the package directory
            self.plugin_dirs = [
                os.path.join(os.path.expanduser("~"), ".mdp", "plugins"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "plugins")
            ]
        else:
            self.plugin_dirs = [plugin_dir]
        
        # Set default config path if not provided
        if config_path is None:
            self.config_path = os.path.join(os.path.expanduser("~"), ".mdp", "config", "plugins.json")
        else:
            self.config_path = config_path
    
    def load_plugins(self) -> None:
        """
        Discover and load all available plugins.
        """
        # Discover plugins from the plugin directories
        discovered_plugins = self.discover_plugins()
        
        # Register discovered plugins
        for name, plugin in discovered_plugins.items():
            self.register_plugin(name, plugin)
        
        # Initialize plugins
        self.initialize_plugins()
        
        # Configure plugins
        self.configure_plugins()
        
        logger.info(f"Loaded {len(discovered_plugins)} plugins")
    
    def discover_plugins(self) -> Dict[str, Any]:
        """
        Discover plugins in the plugin directories.
        
        Returns:
            Dictionary mapping plugin names to plugin instances.
        """
        discovered_plugins = {}
        
        # Create plugin directories if they don't exist
        for plugin_dir in self.plugin_dirs:
            os.makedirs(plugin_dir, exist_ok=True)
        
        # Search for plugins in the plugin directories
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            # Look for Python modules in the plugin directory
            for _, name, is_pkg in pkgutil.iter_modules([plugin_dir]):
                if not is_pkg:
                    continue
                
                try:
                    # Add the plugin directory to the Python path
                    if plugin_dir not in sys.path:
                        sys.path.insert(0, plugin_dir)
                    
                    # Import the plugin module
                    plugin_module = importlib.import_module(name)
                    
                    # Look for a Plugin class in the module
                    for attr_name in dir(plugin_module):
                        attr = getattr(plugin_module, attr_name)
                        
                        # Check if it's a class and has the required plugin interface
                        if (inspect.isclass(attr) and 
                            hasattr(attr, "get_transformations") and 
                            hasattr(attr, "get_reward_functions")):
                            
                            # Create an instance of the plugin
                            plugin_instance = attr()
                            discovered_plugins[name] = plugin_instance
                            logger.info(f"Discovered plugin: {name}")
                            break
                    
                except Exception as e:
                    logger.error(f"Error loading plugin {name}: {e}")
        
        return discovered_plugins
    
    def register_plugin(self, name: str, plugin: Any) -> None:
        """
        Register a plugin with the plugin manager.
        
        Args:
            name: Name of the plugin.
            plugin: Plugin instance.
        """
        # Register the plugin
        self.plugins[name] = plugin
        
        # Register the plugin's transformations
        transformations = plugin.get_transformations()
        for transform_name, transform in transformations.items():
            qualified_name = f"{name}.{transform_name}"
            self.transformations[qualified_name] = transform
        
        # Register the plugin's reward functions
        reward_functions = plugin.get_reward_functions()
        for reward_name, reward_function in reward_functions.items():
            qualified_name = f"{name}.{reward_name}"
            self.reward_functions[qualified_name] = reward_function
        
        logger.info(f"Registered plugin: {name} with {len(transformations)} transformations "
                    f"and {len(reward_functions)} reward functions")
    
    def unregister_plugin(self, name: str) -> None:
        """
        Unregister a plugin from the plugin manager.
        
        Args:
            name: Name of the plugin to unregister.
        """
        if name not in self.plugins:
            logger.warning(f"Plugin {name} is not registered")
            return
        
        # Call cleanup method if it exists
        plugin = self.plugins[name]
        if hasattr(plugin, "cleanup"):
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin {name}: {e}")
        
        # Remove the plugin's transformations
        transform_prefixes = [f"{name}."]
        for transform_name in list(self.transformations.keys()):
            if any(transform_name.startswith(prefix) for prefix in transform_prefixes):
                del self.transformations[transform_name]
        
        # Remove the plugin's reward functions
        for reward_name in list(self.reward_functions.keys()):
            if any(reward_name.startswith(prefix) for prefix in transform_prefixes):
                del self.reward_functions[reward_name]
        
        # Remove the plugin
        del self.plugins[name]
        
        logger.info(f"Unregistered plugin: {name}")
    
    def get_transformation(self, name: str) -> Optional[Callable]:
        """
        Get a transformation by name.
        
        Args:
            name: Name of the transformation.
        
        Returns:
            The transformation callable, or None if not found.
        """
        return self.transformations.get(name)
    
    def get_all_transformations(self) -> Dict[str, Callable]:
        """
        Get all registered transformations.
        
        Returns:
            Dictionary mapping transformation names to transformation callables.
        """
        return self.transformations
    
    def get_reward_function(self, name: str) -> Optional[Callable]:
        """
        Get a reward function by name.
        
        Args:
            name: Name of the reward function.
        
        Returns:
            The reward function callable, or None if not found.
        """
        return self.reward_functions.get(name)
    
    def get_all_reward_functions(self) -> Dict[str, Callable]:
        """
        Get all registered reward functions.
        
        Returns:
            Dictionary mapping reward function names to reward function callables.
        """
        return self.reward_functions
    
    def initialize_plugins(self) -> None:
        """
        Initialize all registered plugins.
        """
        for name, plugin in self.plugins.items():
            if hasattr(plugin, "initialize"):
                try:
                    plugin.initialize()
                    logger.info(f"Initialized plugin: {name}")
                except Exception as e:
                    logger.error(f"Error initializing plugin {name}: {e}")
    
    def cleanup_plugins(self) -> None:
        """
        Clean up all registered plugins.
        """
        for name, plugin in self.plugins.items():
            if hasattr(plugin, "cleanup"):
                try:
                    plugin.cleanup()
                    logger.info(f"Cleaned up plugin: {name}")
                except Exception as e:
                    logger.error(f"Error cleaning up plugin {name}: {e}")
    
    def load_configuration(self) -> Dict[str, Any]:
        """
        Load plugin configuration from the configuration file.
        
        Returns:
            Dictionary containing plugin configuration.
        """
        config = {"plugins": {}}
        
        # Check if the configuration file exists
        if not os.path.exists(self.config_path):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Create a default configuration file
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"Created default plugin configuration at {self.config_path}")
            return config
        
        # Load the configuration file
        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            
            logger.info(f"Loaded plugin configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading plugin configuration: {e}")
        
        return config
    
    def configure_plugins(self) -> None:
        """
        Configure all registered plugins based on the configuration file.
        """
        # Load the configuration
        config = self.load_configuration()
        
        # Configure each plugin
        for name, plugin in self.plugins.items():
            if hasattr(plugin, "configure"):
                # Get plugin-specific configuration
                plugin_config = config.get("plugins", {}).get(name, {})
                
                # Check if the plugin is enabled
                if not plugin_config.get("enabled", True):
                    logger.info(f"Plugin {name} is disabled, skipping configuration")
                    continue
                
                # Get plugin settings
                settings = plugin_config.get("settings", {})
                
                try:
                    # Configure the plugin
                    plugin.configure(settings)
                    logger.info(f"Configured plugin: {name}")
                except Exception as e:
                    logger.error(f"Error configuring plugin {name}: {e}")
    
    def trigger_event(self, event_name: str, **kwargs) -> None:
        """
        Trigger an event for all plugins that have a handler for it.
        
        Args:
            event_name: Name of the event to trigger.
            **kwargs: Arguments to pass to the event handler.
        """
        # Convert event_name to handler method name
        handler_name = f"on_{event_name}"
        
        # Call the handler for each plugin that has it
        for name, plugin in self.plugins.items():
            if hasattr(plugin, handler_name):
                try:
                    handler = getattr(plugin, handler_name)
                    handler(**kwargs)
                except Exception as e:
                    logger.error(f"Error in plugin {name} handling event {event_name}: {e}")

# Global plugin manager instance
_plugin_manager = None

def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager instance.
    
    Returns:
        The global plugin manager instance.
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager 