Usage Guide
===========

This guide will help you get started with AI Sentinel and show you how to use its main features effectively.

Getting Started
---------------
Learn the fundamentals of AI Sentinel with step-by-step examples:

.. toctree::
    :maxdepth: 2

    example_notebooks/api_examples/guards/basic_usage
    
Provider-Specific Guides
------------------------
Examples of using different LLM providers:

.. toctree::
    :maxdepth: 1

    example_notebooks/api_examples/llm/azure_openai
    example_notebooks/api_examples/llm/gemini
    example_notebooks/api_examples/llm/open_source_openai


Common Issues
~~~~~~~~~~~~~

1. **Authentication Errors**
   
   - Verify your API keys are set correctly
   - Check environment variables
   - Ensure proper permissions

2. **Performance Issues**
   
   - Use batch processing for multiple items
   - Enable caching when appropriate
   - Optimize threshold settings

3. **Accuracy Concerns**

   - Adjust confidence thresholds
   - Try different LLM providers
   - Consider model fine-tuning

Getting Help
~~~~~~~~~~~~

- Check our :doc:`API Reference <api>` for detailed documentation
- Visit our `GitHub Issues <https://github.com/reeturajharsh1/ai-sentinel/issues>`_ page
