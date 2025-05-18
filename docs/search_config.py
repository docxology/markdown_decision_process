#!/usr/bin/env python3
"""
Search configuration script for the Markdown Decision Process documentation.
This script sets up Algolia DocSearch integration for the documentation site.
"""

import os
import json
import argparse
from pathlib import Path

def ensure_directory(path):
    """Ensure directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)

def create_docsearch_config(output_file, app_id, api_key, index_name, site_url):
    """Create the DocSearch configuration file."""
    config = {
        "index_name": index_name,
        "start_urls": [
            site_url
        ],
        "sitemap_urls": [
            f"{site_url}/sitemap.xml"
        ],
        "sitemap_alternate_links": True,
        "stop_urls": [],
        "selectors": {
            "lvl0": {
                "selector": ".wy-nav-content-wrap h1",
                "global": True,
                "default_value": "Documentation"
            },
            "lvl1": ".wy-nav-content-wrap h2",
            "lvl2": ".wy-nav-content-wrap h3",
            "lvl3": ".wy-nav-content-wrap h4",
            "lvl4": ".wy-nav-content-wrap h5",
            "lvl5": ".wy-nav-content-wrap h6",
            "text": ".wy-nav-content-wrap p, .wy-nav-content-wrap li, .wy-nav-content-wrap td"
        },
        "strip_chars": " .,;:#",
        "custom_settings": {
            "attributesForFaceting": [
                "language",
                "version"
            ]
        },
        "conversation_id": [
            "1234567890"
        ],
        "nb_hits": 0
    }
    
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"DocSearch configuration saved to {output_file}")

def add_docsearch_to_theme(docs_dir, app_id, api_key, index_name):
    """Add DocSearch integration to the Sphinx theme."""
    # Create custom.js for DocSearch initialization
    static_dir = os.path.join(docs_dir, "_static")
    ensure_directory(static_dir)
    
    js_content = f"""
// Initialize Algolia DocSearch
document.addEventListener('DOMContentLoaded', function() {{
    docsearch({{
        appId: '{app_id}',
        apiKey: '{api_key}',
        indexName: '{index_name}',
        container: '#docsearch',
        debug: false
    }});
    
    // Add search box to the navigation
    const search_nav = document.querySelector('.wy-side-nav-search');
    if (search_nav) {{
        const search_div = document.createElement('div');
        search_div.id = 'docsearch';
        search_div.style.margin = '10px 0';
        search_nav.appendChild(search_div);
    }}
}});
"""
    
    with open(os.path.join(static_dir, "docsearch.js"), 'w') as f:
        f.write(js_content)
    
    # Add CSS and JS to Sphinx configuration
    config_file = os.path.join(docs_dir, "conf.py")
    with open(config_file, 'r') as f:
        config_content = f.read()
    
    # Check if DocSearch is already added
    if "docsearch.js" not in config_content:
        # Add DocSearch requirements to conf.py
        with open(config_file, 'a') as f:
            f.write("""

# DocSearch configuration
html_css_files = html_css_files + [
    'https://cdn.jsdelivr.net/npm/@docsearch/css@3',
]

html_js_files = html_js_files + [
    'https://cdn.jsdelivr.net/npm/@docsearch/js@3',
    'docsearch.js',
]
""")

def create_sitemap(docs_dir, site_url):
    """Create a sitemap.xml generator for Sphinx."""
    # Create the sitemap extension
    sitemap_dir = os.path.join(docs_dir, "_ext")
    ensure_directory(sitemap_dir)
    
    with open(os.path.join(sitemap_dir, "__init__.py"), 'w') as f:
        f.write("# Sphinx extensions directory\n")
    
    with open(os.path.join(sitemap_dir, "sitemap.py"), 'w') as f:
        f.write("""
# Sitemap generator extension for Sphinx
# Based on https://github.com/jdillard/sphinx-sitemap

import os
import xml.etree.ElementTree as ET
from datetime import datetime

def setup(app):
    \"\"\"Setup the sitemap extension.\"\"\"
    app.add_config_value('site_url', None, 'html')
    app.add_config_value('sitemap_filename', 'sitemap.xml', 'html')
    app.connect('build-finished', create_sitemap)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

def create_sitemap(app, exception):
    \"\"\"Create sitemap.xml file.\"\"\"
    if exception is not None or not app.config.site_url:
        return
    
    site_url = app.config.site_url
    if site_url.endswith('/'):
        site_url = site_url[:-1]
    
    filename = app.config.sitemap_filename
    path = os.path.join(app.outdir, filename)
    
    root = ET.Element('urlset')
    root.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    
    for root_path, dirs, files in os.walk(app.outdir):
        for file in files:
            if file.endswith('.html'):
                full_path = os.path.join(root_path, file)
                rel_path = os.path.relpath(full_path, app.outdir)
                
                # Convert Windows path separators
                if os.sep == '\\\\':
                    rel_path = rel_path.replace('\\\\', '/')
                
                # Skip certain files
                if rel_path == 'search.html' or rel_path.startswith('_'):
                    continue
                
                # Get last modified time
                last_mod = datetime.fromtimestamp(os.path.getmtime(full_path))
                last_mod_str = last_mod.strftime('%Y-%m-%d')
                
                # Generate URL
                if rel_path == 'index.html':
                    loc = site_url + '/'
                else:
                    loc = site_url + '/' + rel_path
                
                url = ET.SubElement(root, 'url')
                ET.SubElement(url, 'loc').text = loc
                ET.SubElement(url, 'lastmod').text = last_mod_str
                ET.SubElement(url, 'changefreq').text = 'weekly'
    
    tree = ET.ElementTree(root)
    tree.write(path, encoding='utf-8', xml_declaration=True)
    
    print(f'Generated {filename} at {path}')
""")
    
    # Update conf.py to include the sitemap extension
    config_file = os.path.join(docs_dir, "conf.py")
    with open(config_file, 'r') as f:
        config_content = f.read()
    
    # Check if sitemap is already added
    if "sphinx.ext.sitemap" not in config_content and "sitemap" not in config_content:
        # Add sitemap to conf.py
        with open(config_file, 'a') as f:
            f.write(f"""

# Sitemap configuration
sys.path.append(os.path.abspath('_ext'))
extensions.append('sitemap')
site_url = '{site_url}'
sitemap_filename = 'sitemap.xml'
""")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Configure search for MDP documentation")
    parser.add_argument("--docs-dir", default="docs", help="Documentation directory")
    parser.add_argument("--app-id", default="APP_ID", help="Algolia application ID")
    parser.add_argument("--api-key", default="API_KEY", help="Algolia API key")
    parser.add_argument("--index-name", default="markdown_decision_process", help="Algolia index name")
    parser.add_argument("--site-url", default="https://example.com/docs", help="Documentation site URL")
    parser.add_argument("--output", default="docsearch.json", help="Output file for DocSearch configuration")
    return parser.parse_args()

def main():
    """Main function to configure search for the documentation."""
    args = parse_args()
    
    # Create DocsSearch configuration file
    create_docsearch_config(args.output, args.app_id, args.api_key, args.index_name, args.site_url)
    
    # Add DocSearch to theme
    add_docsearch_to_theme(args.docs_dir, args.app_id, args.api_key, args.index_name)
    
    # Create sitemap generator
    create_sitemap(args.docs_dir, args.site_url)
    
    print(f"Search configuration completed.")
    print(f"1. Submit the configuration file {args.output} to Algolia DocSearch")
    print(f"2. Build your documentation with 'python build_docs.py'")
    print(f"3. Deploy to {args.site_url}")

if __name__ == "__main__":
    main() 