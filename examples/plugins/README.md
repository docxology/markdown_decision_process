# MDP Plugins

This directory contains example plugins for the Markdown Decision Process (MDP) framework.

## Formatting Plugin

The `FormattingPlugin` demonstrates how to create a plugin that provides formatting transformations and reward functions for Markdown documents.

### Features

- **Heading Standardization**: Convert between ATX style (`#`) and underline style (`===` / `---`) headings
- **List Marker Standardization**: Ensure consistent list markers (`-`, `*`, or `+`)
- **Link Style Standardization**: Convert between inline links and reference links
- **Consistency Scoring**: Calculate a document's formatting consistency score

### Usage

```python
from mdp.core import MarkdownProcessor
from formatting_plugin import FormattingPlugin

# Create a processor and register the plugin
processor = MarkdownProcessor()
plugin = FormattingPlugin()
processor.register_plugin(plugin)

# Configure the plugin with preferred formatting styles
plugin.configure({
    "heading_style": "#",       # Use "#" for ATX style or "underline" for underline style
    "list_style": "-",          # Use "-", "*", or "+" for list markers
    "link_style": "inline"      # Use "inline" or "reference" for link style
})

# Process a Markdown document
input_md = """# Title
## Subtitle
* Item 1
+ Item 2
Here is a [link](https://example.com)."""

# Apply transformations
output_md = processor.apply_transformation("fix_headings", input_md)
output_md = processor.apply_transformation("fix_lists", output_md)
output_md = processor.apply_transformation("standardize_links", output_md)

# Calculate consistency score
score = processor.calculate_reward("consistency_score", output_md)
print(f"Consistency score: {score}")
```

### Creating Your Own Plugin

To create your own plugin:

1. Subclass the `MDPPlugin` base class
2. Implement the required methods:
   - `get_metadata()`: Return plugin metadata
   - `get_transformations()`: Return a dictionary of transformation functions
   - `get_reward_functions()`: Return a dictionary of reward functions
3. Add any configuration methods needed for your plugin
4. Implement your transformation and reward functions

See the `FormattingPlugin` for a complete example implementation.

## Other Examples

- More example plugins coming soon! 