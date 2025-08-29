# AI Sentinel 

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


AI Sentinel is a Python package designed to help developers integrate toxicity analysis into their applications with ease. It provides a simple, unified interface to leverage powerful AI models for detecting and categorizing harmful content in text.

### Key Features
- **Advanced Toxicity Detection**: Comprehensive toxicity detection and classification.
- **Multiple LLM Providers**: Designed to support various AI model providers (currently Azure OpenAI, and Gemini, with more models being supported in the future).
- **Structured Output**: Type-safe responses with Pydantic validation.

## Getting Started

### Installation
ai-sentinel is avalible on [PyPI][pypi-link]

```bash
pip install ai-sentinel
```

### Usage

AI Sentinel is designed to be straightforward to use. You'll primarily interact with the `ToxicityGuard` and a client specific to your chosen AI model (e.g., `AzureOpenAIClient`).

```python
from ai_sentinel import AzureOpenAIClient, ToxicityGuard

# Initialize LLM client
client = AzureOpenAIClient(
    api_key="your-api-key",
    model="gpt-4o-mini",
    api_version="2024-02-01",
    azure_endpoint="https://your-resource.openai.azure.com/"
)

# Create toxicity guard
guard = ToxicityGuard(client)

# Analyze text
result = guard.analyze("This is a normal message")

print(f"Is toxic: {result.is_toxic}")
print(f"Confidence: {result.confidence}")
print(f"Categories: {result.categories}")
print(f"Reason: {result.reason}")
print(f"Severity: {result.score}")
```

### Async Usage

Simply call the async analyze function `analyze_async` and use await with each API call:

```python
import asyncio
from ai_sentinel import AzureOpenAIClient, ToxicityGuard

client = AzureOpenAIClient(
    api_key="your-api-key",
    model="gpt-4o-mini",
    api_version="2024-02-01",
    azure_endpoint="https://your-resource.openai.azure.com/"
)

async def main() -> None:
    guard = ToxicityGuard(client)
    response = await guard.analyze_async("Text to analyze")

    print(f"Is toxic: {result.is_toxic}")
    print(f"Confidence: {result.confidence}")
    print(f"Categories: {result.categories}")
    print(f"Reason: {result.reason}")
    print(f"Severity: {result.score}")

asyncio.run(main())
```

### Supported LLM API Services

ai-sentinel is model agnostic, with support for the following LLM API services:

| Provider                             | Models                           | Details                           |
|--------------------------------------|----------------------------------|-----------------------------------|
| [Azure OpenAI][azure-openai]         | GPT-4, GPT-4o, GPT-3.5-turbo     | Industry-leading models           |
| [Google Gemini][gemini]              | Gemini 2.0 Flash, Gemini 2.5 Pro | Latest Google technology          |
| [Open Source LLMs][open-source-list] | Qwen3, GPT-oss, Meta Llama              | Uses [OpenAI Compatible Server's][os-explaination], so check if the server hosting the LLM implements the OpenAI API specifications for endpoints |
| [Anthropic][anthropic]               | *To Be Implemented*              | Will be implemented in the future |


#### Gemini Usage
```python
from ai_sentinel import GeminiClient, ToxicityGuard

# Initialize Gemini client
client = GeminiClient(
    api_key="your-gemini-api-key",
    model="gemini-2.0-flash"
)

# Create and use toxicity guard
guard = ToxicityGuard(client)
result = guard.analyze("Your text here")
```

#### Open Source using OpenAI Usage
```python
from ai_sentinel import OpenAIClient, ToxicityGuard

# Initialize an Open Source LLM Client
client = OpenAIClient(
    base_url="http://localhost:8000/v1",
    model="Qwen/Qwen3-8B"
)

# Create and use toxicity guard
guard = ToxicityGuard(client)
result = guard.analyze("Your text here")
```


## Output

In AI Sentinel's `ToxicityGuard` class, both `analyze` and `analyze_async` methods return a `ToxicityResult` object.

## Response Format

```python
class ToxicityResult:
    is_toxic: bool                          # Whether content is toxic
    confidence: float                       # Confidence score that the content is toxic (0.0-1.0)
    categories: List[ToxicityCategories]    # Detected toxicity categories
    reason: str                             # Explanation of the assessment
    score: ToxicityScore                    # Simplified confidence score: "low", "medium", "high"
```

### Example

```python
{
    "is_toxic": True,
    "confidence": 0.90,
    "categories": [
        <ToxicityCategories.THREATS: 'threats'>, 
        <ToxicityCategories.VIOLENCE: 'violence'>
    ],
    "reason": "The phrase 'I will punch you' is a clear and direct threat of physical violence. It expresses an intention to harm another person, categorizing it under threats and violence.",
    "score": <ToxicityScore.HIGH: 'high'>
}
```

The `ToxicityCategories` and `ToxicityScore` enums are available from `ai_sentinel.models`.

### Toxicity Categories

AI Sentinel detects the following toxicity categories:

- **Hate Speech**: Content attacking individuals/groups based on protected characteristics
- **Harassment**: Hostile behavior targeting specific individuals
- **Threats**: Direct or implied threats of violence or harm
- **Sexual Content**: Inappropriate sexual material
- **Self Harm**: Content promoting self-injury or suicide
- **Violence**: Content glorifying or promoting violence
- **Bullying**: Intimidation or aggressive behavior
- **Discrimination**: Unfair treatment of specific groups

## Configuration

### Environment Variables
Tip: Add enviormental variables to a `.env` file 

```bash
# Azure OpenAI
AZURE_API_KEY=your-azure-api-key
AZURE_API_VERSION=2024-02-01
AZURE_API_BASE=https://your-resource.openai.azure.com/

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key
```

### Using python-dotenv

```python
from dotenv import load_dotenv
import os

load_dotenv()

client = AzureOpenAIClient(
    api_key=os.getenv("AZURE_API_KEY"),
    model="gpt-4o-mini",
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_BASE")
)
```


## License

This project is licensed under the MIT License - see the [LICENSE][license] file for details.

## Changelog
    v0.0.8: Update documentation
    v0.0.7: Add Open Source LLM integration
    v0.0.6: Change authorship
    v0.0.2: Adjust authorship and maintainers
    v0.0.1: Initial release


<!-- REFERENCE LINKS -->
<!-- AI-SENTINEL RESOURCES -->
[license]: ai-sentinel\LICENSE
<!-- LLM API PROVIDERS -->
[gemini]: https://ai.google.dev/tutorials/python_quickstart
[azure-openai]: https://ai.azure.com/?tid=a8eec281-aaa3-4dae-ac9b-9a398b9215e7
[anthropic]: https://www.anthropic.com/
[open-source-list]: https://huggingface.co/
[os-explaination]: https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html
<!-- THIRD-PARTY RESOURCES -->
[pypi-link]: https://pypi.org/project/ai-sentinel/

