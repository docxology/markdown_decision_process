Pandoc Integration API
===================

.. automodule:: mdp.pandoc
   :members:
   :undoc-members:
   :show-inheritance:

Document Conversion
----------------

The Pandoc integration allows for converting markdown documents to various formats.

.. code-block:: python

   from mdp import PandocConverter, MarkdownDocument
   
   # Create a document
   doc = MarkdownDocument(file_path="document.md")
   
   # Create a converter
   converter = PandocConverter()
   
   # Convert to HTML
   html_content = converter.convert_to_html(doc)
   with open("document.html", "w") as f:
       f.write(html_content)
   
   # Convert to PDF
   converter.convert_to_pdf(doc, "document.pdf")
   
   # Convert to other formats
   converter.convert(
       input_path="document.md",
       output_path="document.docx",
       from_format="markdown",
       to_format="docx"
   )

Custom Conversion Options
---------------------

You can customize the conversion process with Pandoc options:

.. code-block:: python

   from mdp import PandocConverter
   
   converter = PandocConverter()
   
   # Convert with custom options
   converter.convert(
       input_path="document.md",
       output_path="document.pdf",
       from_format="markdown",
       to_format="pdf",
       options={
           "pdf-engine": "xelatex",
           "variable": ["geometry:margin=1in", "fontsize=12pt"],
           "toc": None,
           "number-sections": None
       }
   )

Templates and Styling
------------------

You can use custom templates and CSS for document conversion:

.. code-block:: python

   from mdp import PandocConverter
   
   converter = PandocConverter()
   
   # Convert to HTML with custom template and CSS
   converter.convert(
       input_path="document.md",
       output_path="document.html",
       from_format="markdown",
       to_format="html",
       options={
           "template": "custom_template.html",
           "css": ["style.css", "custom.css"],
           "self-contained": None
       }
   )
   
   # Generate a presentation
   converter.convert(
       input_path="slides.md",
       output_path="presentation.pptx",
       from_format="markdown",
       to_format="pptx",
       options={
           "reference-doc": "template.pptx"
       }
   ) 