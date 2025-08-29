# llmfastdev

A Python client for interacting with llamafile local LLM instances.

## Installation

```bash
pip install llmfastdev
```

## Usage

```python
from llmfastdev import LlamafileClient

# Initialize the client
client = LlamafileClient("http://localhost:8080")

# Check if server is running
if client.health_check():
    print("Server is running!")

# Generate a completion
response = client.complete("Hello, how are you?", max_tokens=50)
print(response)

# Use chat format
messages = [
    {"role": "user", "content": "What is the capital of France?"}
]
response = client.chat(messages, max_tokens=50)
print(response)

# Stream completion
for token in client.stream_completion("Tell me a story", max_tokens=100):
    print(token, end="", flush=True)
```

## Features

- Simple HTTP client for llamafile servers
- Support for completion and chat endpoints
- Streaming support
- Context manager support
- Health check functionality
- Model information retrieval

## Requirements

- Python >= 3.7
- requests >= 2.25.0

## License

MIT