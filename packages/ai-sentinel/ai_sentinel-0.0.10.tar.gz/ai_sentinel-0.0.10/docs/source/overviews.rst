Module Overview
===============

AI Sentinel is designed as a modular system for content validation and security checking using Large Language Models (LLMs). Here's how the components work together:

1. **Guard System**
   
   - Content validation engine
   - Configurable rule sets
   - Extensible plugin architecture

2. **LLM Integration Layer**
   
   - Multi-provider support
   - Standardized API interface
   - Automatic failover capabilities

Environment Setup
-----------------
.. toctree::
   :maxdepth: 1

   example_notebooks/environment/env_setup

Required Environment Variables:

.. code-block:: bash

    # Open Source OpenAI Configuration
    OPENAI_API_BASE=your_base_url_here

    # Azure OpenAI Configuration
    AZURE_API_KEY=your_azure_key_here
    AZURE_API_BASE=your_endpoint_here
    AZURE_API_VERSION=your_version_here
    
    # Google Gemini AI Configuration
    GEMINI_API_KEY=your_gemini_key_here

Supported LLM Services
----------------------

AI Sentinel supports multiple LLM API services through a unified interface.
It is Model-agnostic, meaning you can switch between different LLM providers
with minimal code changes. Currently, the following LLM services are supported:

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 40

   * - Provider
     - Models (Examples)
     - Authentication
     - Notes
   * - OpenAI Compatible Server
     - Qwen, Meta Llama, etc.
     - Base URL
     - Used for open-source models using OpenAI's compatibility server
   * - Azure OpenAI
     - gpt-4o-mini
     - API Key + Endpoint + Version
     - Closed source, requires Azure subscription
   * - Google Gemini AI
     - gemini-2.5-flash
     - API Key
     - Closed source, requires Google Cloud subscription

Security Considerations
~~~~~~~~~~~~~~~~~~~~~~~

1. **API Key Management**
   - Use environment variables
   - Rotate keys regularly
   - Never commit keys to source control

2. **Rate Limiting**
   - Implement exponential backoff
   - Monitor usage quotas
   - Set up alerts for unusual activity