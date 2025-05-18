#!/usr/bin/env python3
"""
Notebook conversion script for the Markdown Decision Process project.
This script converts Jupyter notebooks into Sphinx-friendly documentation.
"""

import os
import sys
import re
import glob
import shutil
import argparse
from pathlib import Path
import subprocess
import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor

def ensure_directory(path):
    """Ensure directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)

def run_command(cmd, cwd=None):
    """Run a shell command and return the output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def find_notebooks(examples_dir, pattern="*.ipynb"):
    """Find all Jupyter notebooks in the examples directory."""
    return glob.glob(os.path.join(examples_dir, "**", pattern), recursive=True)

def convert_notebook(notebook_path, output_dir, execute=True, timeout=600):
    """Convert a Jupyter notebook to Markdown format."""
    print(f"Converting notebook: {notebook_path}")
    
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Execute the notebook if requested
    if execute:
        print(f"Executing notebook...")
        execute_processor = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
        try:
            execute_processor.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
        except Exception as e:
            print(f"Error executing notebook: {e}")
    
    # Convert to markdown
    md_exporter = MarkdownExporter()
    (body, resources) = md_exporter.from_notebook_node(nb)
    
    # Fix image paths
    img_pattern = r'!\[.*?\]\((.*?)\)'
    def fix_image_path(match):
        img_path = match.group(1)
        if not img_path.startswith(('http://', 'https://', '/')):
            # Extract filename
            img_name = os.path.basename(img_path)
            return f'![image](../_images/{img_name})'
        return match.group(0)
    
    body = re.sub(img_pattern, fix_image_path, body)
    
    # Get relative paths for file naming
    rel_path = os.path.relpath(notebook_path, start=os.path.dirname(examples_dir))
    output_path = os.path.join(output_dir, f"{os.path.splitext(rel_path)[0]}.md")
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Add front matter with title
    notebook_name = os.path.splitext(os.path.basename(notebook_path))[0]
    title = notebook_name.replace('_', ' ').title()
    front_matter = f"""# {title}

```{{toctree}}
:maxdepth: 2
```

"""
    body = front_matter + body
    
    # Write the markdown file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(body)
    
    # Extract and save images
    images_dir = os.path.join(os.path.dirname(output_dir), "_images")
    ensure_directory(images_dir)
    
    if 'outputs' in resources:
        for filename, data in resources['outputs'].items():
            image_path = os.path.join(images_dir, filename)
            with open(image_path, 'wb') as f:
                f.write(data)
    
    print(f"Converted notebook saved to {output_path}")
    return output_path

def create_index_page(output_dir, notebooks):
    """Create an index page listing all converted notebooks."""
    index_path = os.path.join(output_dir, "index.md")
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# Example Notebooks\n\n")
        f.write("These examples demonstrate how to use the Markdown Decision Process framework.\n\n")
        f.write("```{toctree}\n")
        f.write(":maxdepth: 1\n\n")
        
        for notebook in notebooks:
            # Get relative path from output directory to notebook without extension
            rel_path = os.path.relpath(notebook, start=output_dir)
            rel_path = os.path.splitext(rel_path)[0]
            
            # Handle special case for index.md
            if rel_path == "index":
                continue
                
            f.write(f"{rel_path}\n")
        
        f.write("```\n")
    
    print(f"Created index page at {index_path}")
    return index_path

def update_sphinx_config(docs_dir):
    """Update Sphinx configuration to properly handle notebooks."""
    config_file = os.path.join(docs_dir, "conf.py")
    with open(config_file, 'r') as f:
        config_content = f.read()
    
    # Add nbsphinx if not already present
    if "nbsphinx" not in config_content:
        print("Adding nbsphinx extension to Sphinx configuration")
        with open(config_file, 'a') as f:
            f.write("""

# Notebook integration
extensions.append('nbsphinx')
nbsphinx_execute = 'never'  # We execute notebooks separately
nbsphinx_allow_errors = True  # Continue building even if a notebook has errors

# Add notebooks to the HTML static path
html_static_path = html_static_path + ['_images']
""")

def process_notebooks(examples_dir, output_dir, execute=True, timeout=600):
    """Process all notebooks in the examples directory."""
    # Find all notebooks
    notebooks = find_notebooks(examples_dir)
    print(f"Found {len(notebooks)} notebooks")
    
    if not notebooks:
        print(f"No notebooks found in {examples_dir}")
        return
    
    # Convert each notebook
    converted_notebooks = []
    for notebook in notebooks:
        converted = convert_notebook(notebook, output_dir, execute, timeout)
        converted_notebooks.append(converted)
    
    # Create index page
    create_index_page(output_dir, converted_notebooks)
    
    return converted_notebooks

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert Jupyter notebooks to documentation")
    parser.add_argument("--examples-dir", default="examples", help="Directory containing example notebooks")
    parser.add_argument("--output-dir", default="docs/user/examples", help="Output directory for converted notebooks")
    parser.add_argument("--docs-dir", default="docs", help="Documentation directory")
    parser.add_argument("--execute", action="store_true", help="Execute notebooks before conversion")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout for notebook execution in seconds")
    return parser.parse_args()

def main():
    """Main function to convert notebooks to documentation."""
    args = parse_args()
    
    global examples_dir
    examples_dir = args.examples_dir
    
    # Set up output directory
    output_dir = args.output_dir
    ensure_directory(output_dir)
    
    # Create images directory
    images_dir = os.path.join(os.path.dirname(output_dir), "_images")
    ensure_directory(images_dir)
    
    # Process notebooks
    process_notebooks(args.examples_dir, output_dir, args.execute, args.timeout)
    
    # Update Sphinx configuration
    update_sphinx_config(args.docs_dir)
    
    print(f"Notebook conversion completed")
    print(f"View the examples in your documentation by building with 'python build_docs.py'")

if __name__ == "__main__":
    main() 