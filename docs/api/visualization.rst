Visualization API
================

.. automodule:: mdp.visualization
   :members:
   :undoc-members:
   :show-inheritance:

Document Visualization
-------------------

The visualization module provides tools for creating visual representations of markdown documents and their properties.

.. code-block:: python

   from mdp import StateSpace, VisualizationExporter
   
   # Create and analyze a state space
   state_space = StateSpace()
   state_space.analyze("document.md")
   
   # Create a visualization exporter
   exporter = VisualizationExporter(output_dir="outputs")
   
   # Export state space visualization in different formats
   exporter.export_state_space(state_space, "state_space.png")
   exporter.export_state_space(state_space, "state_space.pdf")
   exporter.export_state_space(state_space, "state_space.svg")

Document Metrics Visualization
--------------------------

You can create visualizations of document quality metrics:

.. code-block:: python

   from mdp import MarkdownDocument, DocumentQuality, VisualizationExporter
   
   # Create and analyze a document
   doc = MarkdownDocument(file_path="document.md")
   quality = DocumentQuality()
   metrics = quality.analyze_document(doc)
   
   # Create a visualization exporter
   exporter = VisualizationExporter(output_dir="outputs")
   
   # Export metrics visualizations
   exporter.export_metrics_visualization(metrics, "document_metrics.png")
   
   # Compare multiple documents
   doc1 = MarkdownDocument(file_path="document1.md")
   doc2 = MarkdownDocument(file_path="document2.md")
   
   metrics1 = quality.analyze_document(doc1)
   metrics2 = quality.analyze_document(doc2)
   
   exporter.export_metrics_comparison(
       [metrics1, metrics2],
       ["Document 1", "Document 2"],
       "comparison.png"
   )

Enhanced Document Export
---------------------

The visualization module also allows exporting enhanced documents with embedded visualizations:

.. code-block:: python

   from mdp import MarkdownDocument, StateSpace, VisualizationExporter
   
   # Create and analyze document
   doc = MarkdownDocument(file_path="document.md")
   state_space = StateSpace()
   state_space.parse_markdown(doc.get_content())
   
   # Create state space visualization
   import matplotlib.pyplot as plt
   fig, ax = plt.subplots(figsize=(10, 8))
   # ... create visualization using state_space data ...
   
   # Export document with embedded visualization
   exporter = VisualizationExporter(output_dir="outputs")
   exporter.export_document_with_visualizations(
       document=doc,
       output_path="enhanced_document.pdf",
       visualizations=[
           ("<!-- VISUALIZATION: STATE_SPACE -->", fig, {"format": "png"}),
       ],
       to_format="pdf"
   ) 