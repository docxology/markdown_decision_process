"""
Plugin system for the Markdown Decision Process.

This module provides the plugin interface for the Markdown Decision Process.
It includes the base plugin class and utility functions for plugin management.
"""

from typing import Dict, Callable, Any, Optional, List, Union
from .plugin_interface import BasePlugin, PluginInterface


class MDPPlugin(BasePlugin):
    """
    Base class for Markdown Decision Process plugins.
    
    This class extends the BasePlugin to provide additional functionality
    specific to the Markdown Decision Process. Plugins should inherit from
    this class to ensure compatibility with the MDP framework.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self.config = {}
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the plugin.
        
        Returns:
            Dict: Dictionary containing metadata about the plugin
        """
        return {
            "name": self.__class__.__name__,
            "version": getattr(self, "VERSION", "0.1.0"),
            "author": getattr(self, "AUTHOR", "Unknown"),
            "description": getattr(self, "DESCRIPTION", "No description provided"),
            "requires": getattr(self, "REQUIRES", {})
        }
    
    def get_transformations(self) -> Dict[str, Callable]:
        """
        Get transformations provided by this plugin.
        
        Returns:
            Dict[str, Callable]: Dictionary mapping transformation names to functions
        """
        return self._transformations
    
    def get_reward_functions(self) -> Dict[str, Callable]:
        """
        Get reward functions provided by this plugin.
        
        Returns:
            Dict[str, Callable]: Dictionary mapping reward function names to functions
        """
        return self._reward_functions
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        Configure the plugin with user-defined settings.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config.update(config)
    
    def initialize(self) -> None:
        """Initialize plugin resources."""
        pass
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass


# Plugin registry to store loaded plugins
_plugin_registry: Dict[str, MDPPlugin] = {}


def register_plugin(name: str, plugin: MDPPlugin) -> None:
    """
    Register a plugin with the given name.
    
    Args:
        name (str): Name of the plugin
        plugin (MDPPlugin): Plugin instance
    """
    _plugin_registry[name] = plugin


def get_plugin(name: str) -> Optional[MDPPlugin]:
    """
    Get a plugin by name.
    
    Args:
        name (str): Name of the plugin
        
    Returns:
        Optional[MDPPlugin]: Plugin instance if found, None otherwise
    """
    return _plugin_registry.get(name)


def list_plugins() -> List[str]:
    """
    List all registered plugins.
    
    Returns:
        List[str]: List of plugin names
    """
    return list(_plugin_registry.keys())


def unregister_plugin(name: str) -> bool:
    """
    Unregister a plugin.
    
    Args:
        name (str): Name of the plugin
        
    Returns:
        bool: True if the plugin was unregistered, False otherwise
    """
    if name in _plugin_registry:
        plugin = _plugin_registry[name]
        plugin.cleanup()
        del _plugin_registry[name]
        return True
    return False 