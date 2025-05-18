Document API
===========

.. automodule:: mdp.document
   :members:
   :undoc-members:
   :show-inheritance:

Document Management
-----------------

The ``MarkdownDocument`` class provides a structured way to work with markdown documents.

.. code-block:: python

   from mdp import MarkdownDocument
   
   # Create a document from a file
   doc = MarkdownDocument(file_path="document.md")
   
   # Or create a document from content
   doc = MarkdownDocument(content="# Title\n\nContent goes here.")
   
   # Access document content
   content = doc.get_content()
   
   # Access document structure
   structure = doc.get_structure()
   
   # Access specific elements
   headings = doc.get_headings()
   paragraphs = doc.get_paragraphs()
   lists = doc.get_lists()
   code_blocks = doc.get_code_blocks()
   
   # Modify and save the document
   doc.set_content("# Modified Title\n\nModified content.")
   doc.save("modified_document.md")

Document Analysis
--------------

The document class integrates with other MDP components for analysis:

.. code-block:: python

   from mdp import MarkdownDocument, DocumentQuality
   
   # Create a document
   doc = MarkdownDocument(file_path="document.md")
   
   # Analyze document quality
   quality = DocumentQuality()
   metrics = quality.analyze_document(doc)
   
   # Print readability metrics
   for metric, value in metrics.get("readability", {}).items():
       print(f"{metric}: {value:.2f}")
       
   # Get overall quality score
   overall_score = metrics.get("overall_score", 0.0)
   print(f"Overall quality score: {overall_score:.2f}") 