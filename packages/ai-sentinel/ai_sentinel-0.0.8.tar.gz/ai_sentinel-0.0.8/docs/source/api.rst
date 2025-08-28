
API Reference
=============

Welcome to the AI Sentinel API reference documentation. This page provides detailed information about 
the public classes, methods, and functions available in the package. The API is organized into three 
main modules: core components, guard systems, and LLM clients.

.. note::
   All examples assume you have already installed AI Sentinel.

Core Components
---------------
.. _core_api:

The core module provides fundamental data structures and utilities used throughout AI Sentinel.

.. autosummary::
   :toctree: _autosummary
   :recursive:

   ai_sentinel.core.LLMResponse

**Example Usage**::

    from ai_sentinel.core import LLMResponse
    
    # Create a response object
    response = LLMResponse(
        content="Sample response",
        model="gpt-4"
    )

Guard Systems
-------------
.. _guards_api:

The guards module contains the toxicity detection and analysis components, which are the primary 
tools for content moderation.

.. autosummary::
   :toctree: _autosummary
   :recursive:

   ai_sentinel.guards.toxicity_guard.ToxicityResult
   ai_sentinel.guards.toxicity_guard.ToxicityCategories
   ai_sentinel.guards.toxicity_guard.ToxicityScore

**Example Usage**::

    from ai_sentinel.guards import ToxicityGuard
    from ai_sentinel.guards.toxicity_guard import ToxicityCategories
    
    # Initialize the guard
    sample_client = "your_client_here"  # Replace with actual client
    guard = ToxicityGuard(client=sample_client)
    
    # Analyze text
    result = guard.analyze("Your text here")
    
    # Access results
    print(result.is_toxic)
    print(result.categories)
    print(result.scores)

LLM Clients
-----------
.. _llm_api:

The LLM module provides interfaces to various Language Model providers. Each client implements 
a common interface while handling provider-specific requirements.

.. autosummary::
   :toctree: _autosummary
   :recursive:

   ai_sentinel.llm.BaseLLMClient
   ai_sentinel.llm.AzureOpenAIClient
   ai_sentinel.llm.GeminiClient
   ai_sentinel.llm.OpenAIClient

**Example Usage**

    .. toctree::
        :maxdepth: 1

        example_notebooks/api_examples/llm/azure_openai
        example_notebooks/api_examples/llm/gemini
        example_notebooks/api_examples/llm/open_source_openai

See Also
--------
- :doc:`usage` - For more detailed usage examples
- :doc:`overviews` - For high-level package concepts

