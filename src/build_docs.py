"""
Documentation builder for the Markdown Decision Process.

This module provides utilities for generating documentation from the codebase
including API references, guides, and examples.
"""

import os
import re
import inspect
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional, Set, Tuple, Union
import importlib
import sys
import shutil
import datetime

# Add the source directory to the path so we can import modules
SRC_DIR = Path(__file__).parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import the modules we want to document
import mdp


def get_module_docstring(module_path: str) -> str:
    """
    Extract the module-level docstring from a module.
    
    Args:
        module_path: Import path to the module
        
    Returns:
        The module's docstring, or an empty string if none is found
    """
    try:
        module = importlib.import_module(module_path)
        return inspect.getdoc(module) or ""
    except ImportError:
        return ""


def get_class_info(cls: type) -> Dict[str, Any]:
    """
    Extract information about a class.
    
    Args:
        cls: The class to document
        
    Returns:
        Dictionary with class information
    """
    methods = {}
    
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        if not name.startswith('_') or name == '__init__':
            methods[name] = {
                'name': name,
                'signature': str(inspect.signature(method)),
                'docstring': inspect.getdoc(method) or "",
                'is_async': inspect.iscoroutinefunction(method),
                'source_line': inspect.getsourcelines(method)[1]
            }
    
    return {
        'name': cls.__name__,
        'docstring': inspect.getdoc(cls) or "",
        'methods': methods,
        'source_line': inspect.getsourcelines(cls)[1]
    }


def get_function_info(func: Callable) -> Dict[str, Any]:
    """
    Extract information about a function.
    
    Args:
        func: The function to document
        
    Returns:
        Dictionary with function information
    """
    return {
        'name': func.__name__,
        'signature': str(inspect.signature(func)),
        'docstring': inspect.getdoc(func) or "",
        'is_async': inspect.iscoroutinefunction(func),
        'source_line': inspect.getsourcelines(func)[1]
    }


def get_module_info(module_path: str) -> Dict[str, Any]:
    """
    Extract information about a module.
    
    Args:
        module_path: Import path to the module
        
    Returns:
        Dictionary with module information
    """
    try:
        module = importlib.import_module(module_path)
        
        classes = {}
        functions = {}
        
        for name, obj in inspect.getmembers(module):
            # Skip private members
            if name.startswith('_'):
                continue
                
            # Document classes
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                classes[name] = get_class_info(obj)
                
            # Document functions
            elif inspect.isfunction(obj) and obj.__module__ == module.__name__:
                functions[name] = get_function_info(obj)
        
        return {
            'name': module.__name__,
            'docstring': inspect.getdoc(module) or "",
            'classes': classes,
            'functions': functions
        }
    except ImportError:
        return {
            'name': module_path,
            'docstring': "",
            'classes': {},
            'functions': {}
        }


def generate_markdown_api_docs(output_dir: Union[str, Path]) -> None:
    """
    Generate markdown API documentation for the MDP package.
    
    Args:
        output_dir: Directory to write the documentation to
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Define the modules to document
    modules = [
        'mdp.document',
        'mdp.transformations',
        'mdp.state_space',
        'mdp.policy_optimizer',
        'mdp.quality',
        'mdp.visualization',
        'mdp.export',
        'mdp.plugin_interface',
        'mdp.plugins',
        'mdp.markdown_agent',
        'mdp.markchain',
        'mdp.pandoc',
        'mdp.belief_updater'
    ]
    
    # Generate index.md
    with open(output_dir / 'index.md', 'w') as f:
        f.write("# Markdown Decision Process API Reference\n\n")
        f.write("## Modules\n\n")
        
        for module_path in modules:
            module_name = module_path.split('.')[-1]
            f.write(f"* [{module_name}]({module_name}.md)\n")
    
    # Generate a page for each module
    for module_path in modules:
        module_name = module_path.split('.')[-1]
        info = get_module_info(module_path)
        
        with open(output_dir / f"{module_name}.md", 'w') as f:
            f.write(f"# {module_name}\n\n")
            
            if info['docstring']:
                f.write(f"{info['docstring']}\n\n")
                
            if info['classes']:
                f.write("## Classes\n\n")
                
                for class_name, class_info in sorted(info['classes'].items()):
                    f.write(f"### {class_name}\n\n")
                    
                    if class_info['docstring']:
                        f.write(f"{class_info['docstring']}\n\n")
                        
                    f.write("#### Methods\n\n")
                    
                    for method_name, method_info in sorted(class_info['methods'].items()):
                        f.write(f"##### `{method_name}{method_info['signature']}`\n\n")
                        
                        if method_info['docstring']:
                            f.write(f"{method_info['docstring']}\n\n")
            
            if info['functions']:
                f.write("## Functions\n\n")
                
                for func_name, func_info in sorted(info['functions'].items()):
                    f.write(f"### `{func_name}{func_info['signature']}`\n\n")
                    
                    if func_info['docstring']:
                        f.write(f"{func_info['docstring']}\n\n")


def generate_technical_docs(output_dir: Union[str, Path]) -> None:
    """
    Generate technical documentation for the MDP package.
    
    Args:
        output_dir: Directory to write the documentation to
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate technical overviews
    with open(output_dir / 'architecture.md', 'w') as f:
        f.write("# Markdown Decision Process Architecture\n\n")
        f.write("## Overview\n\n")
        f.write("The Markdown Decision Process (MDP) package is structured around the concept of Markov Decision Processes applied to Markdown documents. The architecture consists of several key components:\n\n")
        f.write("1. **Document Model**: Representation of Markdown documents as states\n")
        f.write("2. **Transformations**: Actions that transition between document states\n")
        f.write("3. **Quality Metrics**: Reward functions for evaluating document quality\n")
        f.write("4. **Policy Optimization**: Strategies for finding optimal document transformations\n")
        f.write("5. **Plugin System**: Extensibility through custom transformations and rewards\n\n")
        
        f.write("## Component Interactions\n\n")
        f.write("The components interact according to the MDP framework:\n\n")
        f.write("1. The document state space represents possible Markdown documents\n")
        f.write("2. Transformations are actions that transition between states\n")
        f.write("3. Quality metrics provide rewards for each state\n")
        f.write("4. Policy optimization finds sequences of transformations to maximize quality\n\n")
        
        f.write("## Implementation Details\n\n")
        f.write("See the API documentation for implementation details of each component.")
    
    # Generate design decisions document
    with open(output_dir / 'design_decisions.md', 'w') as f:
        f.write("# Design Decisions\n\n")
        f.write("## Markdown Representation\n\n")
        f.write("The package represents Markdown documents as structured objects with components like headings, paragraphs, lists, and code blocks. This facilitates complex transformations while preserving document semantics.\n\n")
        
        f.write("## Quality Metrics\n\n")
        f.write("Quality metrics are implemented as reward functions that evaluate document properties such as readability, structure, and consistency. These metrics guide the optimization process toward higher-quality documents.\n\n")
        
        f.write("## Plugin Architecture\n\n")
        f.write("The plugin system allows for extensibility through custom transformations and reward functions. Plugins can be developed independently and integrated into the MDP framework to add domain-specific functionality.")


def build_docs(output_dir: Union[str, Path] = None) -> None:
    """
    Build all documentation for the MDP package.
    
    Args:
        output_dir: Directory to write the documentation to, defaults to 'docs'
    """
    if output_dir is None:
        output_dir = Path('docs')
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate API docs
    api_dir = output_dir / 'api'
    generate_markdown_api_docs(api_dir)
    
    # Generate technical docs
    tech_dir = output_dir / 'technical'
    generate_technical_docs(tech_dir)
    
    # Generate main index
    with open(output_dir / 'index.md', 'w') as f:
        f.write("# Markdown Decision Process Documentation\n\n")
        f.write("## Contents\n\n")
        f.write("* [API Reference](api/index.md): Reference documentation for the MDP API\n")
        f.write("* [Technical Documentation](technical/architecture.md): Technical overview and design decisions\n")
        
        # Add timestamp
        f.write(f"\n\nGenerated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    # If run as a script, build the docs
    build_docs() 