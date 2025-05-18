StateSpace API
============

.. automodule:: mdp.state_space
   :members:
   :undoc-members:
   :show-inheritance:

State Visualization
------------------

The ``StateSpace`` class provides tools for visualizing the structure of markdown documents as directed graphs.

.. code-block:: python

   from mdp import StateSpace
   
   # Create a state space analyzer
   state_space = StateSpace()
   
   # Analyze a markdown file
   state_space.analyze("document.md")
   
   # Visualize the state space
   state_space.visualize("state_space.png", title="Document Structure")
   
   # Print statistics about the document structure
   state_space.print_statistics()

Features
--------

- Analysis of markdown documents to extract state transitions
- Visualization of document structure as a directed graph
- Calculation of transition probabilities between states
- Extraction of features from states for machine learning
- Graph algorithms for analyzing document structure 