PolicyOptimizer API
================

.. automodule:: mdp.policy_optimizer
   :members:
   :undoc-members:
   :show-inheritance:

Document Optimization
--------------------

The ``PolicyOptimizer`` class transforms markdown documents to optimize for specific quality metrics.

.. code-block:: python

   from mdp import PolicyOptimizer
   
   # Create an optimizer with custom reward weights
   optimizer = PolicyOptimizer(
       reward_weights={
           "readability": 0.6,
           "information_density": 0.3,
           "structure_clarity": 0.1,
       }
   )
   
   # Transform a document
   optimized_content = optimizer.transform("document.md")
   
   # Save the optimized document
   with open("optimized_document.md", "w") as f:
       f.write(optimized_content)

Custom Reward Functions
----------------------

You can define custom reward functions to guide the optimization process:

.. code-block:: python

   def image_density_reward(document_structure):
       """Reward documents with a good ratio of images to text."""
       image_count = sum(1 for e in document_structure 
                        if e['type'] == 'paragraph' and '![' in e['content'])
       text_blocks = sum(1 for e in document_structure if e['type'] == 'paragraph')
       
       if text_blocks == 0:
           return 0
       
       ratio = image_count / text_blocks
       # Optimal ratio is around 0.2-0.3 images per text block
       return 10 * (1 - abs(0.25 - ratio) * 2)

   optimizer = PolicyOptimizer(
       custom_rewards={"image_density": image_density_reward},
       reward_weights={"readability": 0.5, "image_density": 0.5}
   ) 