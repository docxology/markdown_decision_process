Transformations API
=================

.. automodule:: mdp.transformations
   :members:
   :undoc-members:
   :show-inheritance:

Document Transformations
---------------------

The transformations module provides classes for modifying markdown documents in specific ways.

.. code-block:: python

   from mdp import (
       MarkdownDocument,
       HeadingLevelTransformation,
       ListFormatTransformation,
       CodeBlockFormatTransformation,
       TransformationPipeline
   )
   
   # Create a document
   doc = MarkdownDocument(file_path="document.md")
   
   # Create transformations
   heading_transform = HeadingLevelTransformation(min_level=1, increment=0)
   list_transform = ListFormatTransformation(target_type="unordered", bullet_style="-")
   code_transform = CodeBlockFormatTransformation(target_language="python")
   
   # Apply individual transformations
   heading_transform.apply(doc)
   list_transform.apply(doc)
   
   # Or create a pipeline of transformations
   pipeline = TransformationPipeline([
       heading_transform,
       list_transform,
       code_transform
   ])
   
   # Apply the entire pipeline to a document
   pipeline.apply(doc, "transformed_document.md")

Available Transformations
---------------------

The following transformation classes are available:

- **HeadingLevelTransformation**: Adjusts heading levels
- **ListFormatTransformation**: Converts between ordered and unordered lists
- **CodeBlockFormatTransformation**: Changes code block language specifiers
- **LinkFormatTransformation**: Converts between inline and reference links
- **TableFormatTransformation**: Formats and normalizes tables
- **TextStyleTransformation**: Standardizes text emphasis styles
- **TransformationPipeline**: Combines multiple transformations

Custom Transformations
-------------------

You can create custom transformations by extending the base `Transformation` class:

.. code-block:: python

   from mdp.transformations import Transformation
   
   class CustomTransformation(Transformation):
       """A custom transformation that does something specific."""
       
       def __init__(self, custom_param):
           self.custom_param = custom_param
           
       def apply(self, document, output_path=None):
           # Get document content
           content = document.get_content()
           
           # Apply transformation
           transformed_content = self._transform(content)
           
           # Update document
           document.set_content(transformed_content)
           
           # Save if output_path is provided
           if output_path:
               document.save(output_path)
               
       def _transform(self, content):
           # Custom transformation logic
           return content  # Replace with actual transformation
   
   # Use your custom transformation
   custom_transform = CustomTransformation(custom_param="value")
   custom_transform.apply(doc) 