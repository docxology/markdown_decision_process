"""
Plugin interface for the Markdown Decision Process.

This module defines the interface that plugins must implement to extend the
Markdown Decision Process.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional


class PluginInterface(ABC):
    """
    Interface for Markdown Decision Process plugins.
    
    Plugins extend the functionality of the Markdown Decision Process by providing
    custom transformations, reward functions, and other components. This class
    defines the interface that plugins must implement.
    """
    
    @abstractmethod
    def get_transformations(self) -> Dict[str, Callable]:
        """
        Get the transformations provided by this plugin.
        
        Returns:
            Dictionary mapping transformation names to transformation callables.
            Each transformation should take a document string and return a transformed
            document string.
        """
        pass
    
    @abstractmethod
    def get_reward_functions(self) -> Dict[str, Callable]:
        """
        Get the reward functions provided by this plugin.
        
        Returns:
            Dictionary mapping reward function names to reward function callables.
            Each reward function should take a document string and return a numeric reward.
        """
        pass
    
    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called when the plugin is first loaded. Plugins can override
        this method to perform any initialization tasks.
        """
        pass
    
    def cleanup(self) -> None:
        """
        Clean up the plugin.
        
        This method is called when the plugin is being unloaded. Plugins can override
        this method to perform any cleanup tasks.
        """
        pass
    
    def configure(self, settings: Dict[str, Any]) -> None:
        """
        Configure the plugin with the provided settings.
        
        Args:
            settings: Dictionary containing plugin settings.
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the plugin.
        
        Returns:
            Dictionary containing metadata about the plugin, such as name,
            version, author, and description.
        """
        return {
            "name": self.__class__.__name__,
            "version": "0.1.0",
            "author": "Unknown",
            "description": "No description provided",
            "requires": {}
        }


class BasePlugin(PluginInterface):
    """
    Base class for Markdown Decision Process plugins.
    
    This class provides default implementations of the plugin interface methods.
    Plugins can inherit from this class instead of implementing the interface
    directly.
    """
    
    def __init__(self):
        """
        Initialize the plugin.
        """
        self._transformations = {}
        self._reward_functions = {}
    
    def get_transformations(self) -> Dict[str, Callable]:
        """
        Get the transformations provided by this plugin.
        
        Returns:
            Dictionary mapping transformation names to transformation callables.
        """
        return self._transformations
    
    def get_reward_functions(self) -> Dict[str, Callable]:
        """
        Get the reward functions provided by this plugin.
        
        Returns:
            Dictionary mapping reward function names to reward function callables.
        """
        return self._reward_functions
    
    def register_transformation(self, name: str, transformation: Callable) -> None:
        """
        Register a transformation with the plugin.
        
        Args:
            name: Name of the transformation.
            transformation: Transformation callable.
        """
        self._transformations[name] = transformation
    
    def register_reward_function(self, name: str, reward_function: Callable) -> None:
        """
        Register a reward function with the plugin.
        
        Args:
            name: Name of the reward function.
            reward_function: Reward function callable.
        """
        self._reward_functions[name] = reward_function
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the plugin.
        
        Returns:
            Dictionary containing metadata about the plugin.
        """
        return {
            "name": self.__class__.__name__,
            "version": getattr(self, "VERSION", "0.1.0"),
            "author": getattr(self, "AUTHOR", "Unknown"),
            "description": getattr(self, "DESCRIPTION", "No description provided"),
            "requires": getattr(self, "REQUIRES", {})
        } 