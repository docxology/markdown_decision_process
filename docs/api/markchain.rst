=========
MarkChain
=========

.. automodule:: mdp.markchain
   :members:
   :undoc-members:
   :show-inheritance:
   
Class Diagram
============

.. code-block:: text

   +------------------------+
   |      MarkChain         |
   +------------------------+
   | - transitions: dict    |
   | - order: int           |
   | - states: set          |
   +------------------------+
   | + train(document)      |
   | + generate(start, len) |
   | + transition_prob(...) |
   | + save/load_model(...) |
   +------------------------+
         ^
         |
         |
   +------------------------+
   | VariableOrderMarkChain |
   +------------------------+
   | - max_order: int       |
   | - backoff: bool        |
   +------------------------+
   | + context_match(...)   |
   | + predict_next(...)    |
   +------------------------+ 