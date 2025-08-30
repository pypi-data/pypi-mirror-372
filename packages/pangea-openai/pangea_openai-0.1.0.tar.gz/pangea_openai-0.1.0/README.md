# Pangea + OpenAI Python API library

A wrapper around the OpenAI Python library that wraps the [Responses API](https://platform.openai.com/docs/api-reference/responses)
with Pangea AI Guard. Supports Python v3.10 and greater.

## Installation

```bash
pip install -U pangea-openai
```

## Usage

```python
import os
from pangea_openai import PangeaOpenAI

client = PangeaOpenAI(
    pangea_api_key=os.environ.get("PANGEA_API_KEY"),
    pangea_input_recipe="pangea_prompt_guard",
    pangea_output_recipe="pangea_llm_response_guard",
    api_key=os.environ.get("OPENAI_API_KEY"),
)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a coding assistant that talks like a pirate.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
```
