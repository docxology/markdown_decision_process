BeliefUpdater API
===============

.. automodule:: mdp.belief_updater
   :members:
   :undoc-members:
   :show-inheritance:

Semantic Analysis
---------------

The ``BeliefUpdater`` class handles uncertainty in interpreting markdown semantics using a belief state model inspired by POMDPs.

.. code-block:: python

   from mdp import BeliefUpdater
   
   # Create a belief updater with custom semantic classes
   updater = BeliefUpdater(
       semantic_classes=["instruction", "explanation", "warning", "note"],
       noise_factor=0.1
   )
   
   # Analyze a document
   analysis = updater.analyze_document_file("document.md")
   
   # Extract the most likely semantic class
   semantic_class, probability = updater.get_most_likely_semantics()
   print(f"Document type: {semantic_class} (confidence: {probability:.2f})")

Belief Management
--------------

You can directly manage beliefs about document semantics:

.. code-block:: python

   # Update specific beliefs
   updater.update_belief("instruction", 0.8)
   updater.update_belief("warning", 0.2)
   
   # Get current beliefs
   beliefs = updater.get_all_beliefs()
   
   # Update from observations
   updater.update_from_observation({
       "structure": 0.7,
       "readability": 0.9
   })
   
   # Calculate belief entropy (uncertainty measure)
   entropy = updater.calculate_entropy()

Custom Domain Adaptation
--------------------

You can adapt the belief updater for different document domains:

.. code-block:: python

   # Define prior beliefs for technical documentation
   tech_doc_priors = {
       "structure": 0.8,
       "complexity": 0.7,
       "reference": 0.6
   }
   
   # Create a domain-specific updater
   tech_updater = BeliefUpdater(
       semantic_classes=["api", "tutorial", "reference"],
       prior_beliefs=tech_doc_priors
   ) 