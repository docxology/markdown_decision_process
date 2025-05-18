=========================
Markdown Decision Process
=========================

A framework reimagining Markdown documents as Markov Decision Processes

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT

Overview
========

The Markdown Decision Process (MDP) framework provides a novel approach to understanding, analyzing, and transforming Markdown documents through the lens of Markov Decision Processes. By viewing markdown elements as states and transformations between elements as state transitions, MDP offers powerful tools for optimizing document quality and structure.

Key Concepts
-----------

* **Markdown Elements as States**: Document components (headings, paragraphs, etc.) are modeled as states in a state space
* **Transformations as State Transitions**: Document modifications follow transition probabilities between states
* **Document Quality as Rewards**: Quality metrics like readability and coherence form reward functions
* **Generation Strategies as Policies**: Document transformation strategies optimize against these reward functions
* **Semantic Interpretation as Belief States**: Handling uncertainty about meaning through belief updates

Installation
===========

.. code-block:: bash

   pip install markdown-decision-process

Getting Started
=============

.. code-block:: python

   import mdp
   
   # Load a document
   doc = mdp.MarkdownDocument.from_file("example.md")
   
   # Analyze the document structure
   state_space = mdp.StateSpace()
   state_space.analyze(doc)
   
   # Visualize the document state space
   state_space.visualize("example_structure.png")
   
   # Apply a transformation with the policy optimizer
   optimizer = mdp.PolicyOptimizer(
       reward_weights={"readability": 0.7, "information_density": 0.3}
   )
   optimized_doc = optimizer.transform(doc)
   optimized_doc.save("optimized_example.md")

Contents
========

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   
   user/installation
   user/quickstart
   user/concepts
   user/examples
   
.. toctree::
   :maxdepth: 2
   :caption: Technical Documentation
   
   technical/markchain
   technical/policy_optimization
   technical/state_space
   technical/belief_updater
   technical/document
   technical/transformations
   
.. toctree::
   :maxdepth: 2
   :caption: API Reference
   
   api/mdp
   api/markchain
   api/document
   api/state_space
   api/policy_optimizer
   api/belief_updater
   api/transformations
   api/visualization
   api/pandoc
   
.. toctree::
   :maxdepth: 1
   :caption: Development
   
   dev/contributing
   dev/roadmap
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 