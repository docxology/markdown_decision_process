#!/usr/bin/env python3
"""
Documentation build script for the Markdown Decision Process project.
This script automates the process of building the documentation using Sphinx.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse
from datetime import datetime

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

def generate_api_docs(output_dir, src_dir):
    """Generate API documentation using sphinx-apidoc."""
    ensure_directory(output_dir)
    modules = [
        "mdp", 
        "mdp.markchain", 
        "mdp.document", 
        "mdp.state_space",
        "mdp.policy_optimizer", 
        "mdp.transformations", 
        "mdp.belief_updater",
        "mdp.visualization", 
        "mdp.pandoc", 
        "mdp.markdown_agent"
    ]
    
    for module in modules:
        rst_path = os.path.join(output_dir, f"{module.split('.')[-1]}.rst")
        if not os.path.exists(rst_path):
            # If RST file doesn't exist, create a basic one
            with open(rst_path, 'w') as f:
                module_name = module.split('.')[-1]
                title = module_name.replace('_', ' ').title()
                f.write(f"{title}\n")
                f.write("=" * len(title) + "\n\n")
                f.write(f".. automodule:: {module}\n")
                f.write("   :members:\n")
                f.write("   :undoc-members:\n")
                f.write("   :show-inheritance:\n")

def copy_markdown_files(docs_dir, output_dir):
    """Copy Markdown files to the documentation directory."""
    # Map of source files to destination files
    files_to_copy = {
        "README.md": "index.md",
        "CONTRIBUTING.md": "dev/contributing.md",
        "docs/ROADMAP.md": "dev/roadmap.md",
        "docs/technical/markchain.md": "technical/markchain.md",
        "docs/technical/policy_optimization.md": "technical/policy_optimization.md",
    }
    
    for src, dest in files_to_copy.items():
        src_path = os.path.join(os.path.dirname(docs_dir), src)
        dest_path = os.path.join(output_dir, dest)
        
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        if os.path.exists(src_path):
            shutil.copy2(src_path, dest_path)
            print(f"Copied {src_path} to {dest_path}")
        else:
            print(f"Warning: Source file {src_path} does not exist")

def build_docs(docs_dir, output_dir, builder="html"):
    """Build documentation using Sphinx."""
    # Create necessary directories
    build_dir = os.path.join(docs_dir, "_build", builder)
    ensure_directory(build_dir)
    
    # Generate API documentation
    generate_api_docs(os.path.join(docs_dir, "api"), os.path.join(os.path.dirname(docs_dir), "src"))
    
    # Copy markdown files
    copy_markdown_files(docs_dir, docs_dir)
    
    # Build the documentation
    cmd = [
        "sphinx-build",
        "-b", builder,
        "-d", os.path.join(docs_dir, "_build", "doctrees"),
        docs_dir,
        build_dir
    ]
    
    run_command(cmd)
    
    # Copy built documentation to output directory if specified
    if output_dir and output_dir != build_dir:
        ensure_directory(output_dir)
        for item in os.listdir(build_dir):
            s = os.path.join(build_dir, item)
            d = os.path.join(output_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    
    print(f"\nDocumentation built successfully in {output_dir or build_dir}")
    return build_dir

def clean_docs(docs_dir):
    """Clean documentation build files."""
    build_dir = os.path.join(docs_dir, "_build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"Cleaned {build_dir}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build MDP documentation")
    parser.add_argument("--clean", action="store_true", help="Clean documentation before building")
    parser.add_argument("--builder", default="html", help="Sphinx builder to use (html, latex, etc.)")
    parser.add_argument("--output", help="Output directory for documentation")
    return parser.parse_args()

def main():
    """Main function to build documentation."""
    args = parse_args()
    
    # Get the docs directory (where this script is located)
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.clean:
        clean_docs(docs_dir)
    
    output_dir = args.output or os.path.join(docs_dir, "_build", args.builder)
    build_docs(docs_dir, output_dir, args.builder)

if __name__ == "__main__":
    main() 