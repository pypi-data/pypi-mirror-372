# Aisberg Python SDK

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Private-informational)

Aisberg SDK for Python is a robust and easy-to-use library for interacting with the Aisberg API.  
It provides **synchronous** and **asynchronous** clients, advanced module abstractions, and built-in support for
conversational LLM workflows, collections, embeddings, and more.

---

## Features

- **Sync & Async clients**: Use with regular scripts or async frameworks
- **Auto tool execution** for LLM flows (tool calls, results integration)
- **Modular architecture**: Collections, chat, models, workflows, embeddings, and more
- **Strong typing** via Pydantic models
- **Environment-based configuration** (supports `.env` files and system environment variables)
- **Context manager support** for easy resource management
- **Custom tool registration**: Easily extend LLM capabilities with your own functions
- **Document Parsing**: Parse documents into structured data (e.g., JSON, CSV, PNG, PDF, etc.)

---

## Installation

```sh
pip install aisberg
````

Or, for local development:

```sh
git clone https://your.git.repo/aisberg.git
cd aisberg
pip install -e .
```

---

## Quickstart

### 1. **Configure your API key and base URL**

You can set them as environment variables, or in a `.env` file:

```env
AISBERG_API_KEY=...
AISBERG_BASE_URL=https://url
AISBERG_TIMEOUT=...  # Optional, default is 180 seconds (3 minutes)
```

In order to use the Document Parsing feature, you also need to set the `S3` credentials - ask the FreePro team for
these:

```env
S3_ACCESS_KEY_ID=...
S3_SECRET_ACCESS_KEY=...
S3_ENDPOINT=https://s3.endpoint
```

### 2. **Synchronous Usage**

```python
from aisberg import AisbergClient

with AisbergClient() as client:
    me = client.me.info()
    print(me)

    chat_response = client.chat.complete(
        input="Bonjour, qui es-tu ?",
        model="llm-aisberg",
    )
    print(chat_response.choices[0].message.content)
```

### 3. **Asynchronous Usage**

```python
import asyncio
from aisberg import AisbergAsyncClient


async def main():
    async with AisbergAsyncClient() as client:
        await client.initialize()
        me = await client.me.info()
        print(me)

        chat_response = await client.chat.complete(
            input="Hello, who are you?",
            model="llm-aisberg",
        )
        print(chat_response.choices[0].message.content)


asyncio.run(main())
```

---

## Modules

* `client.me` — User/account info
* `client.chat` — Conversational LLM completions and streaming
* `client.collections` — Manage data collections
* `client.embeddings` — Encode texts to embeddings
* `client.models` — Model discovery & info
* `client.workflows` — Workflow management & execution
* `client.tools` — Register and execute tools for LLM tool calls
* `client.documents` — Document parsing and management

Each module is available both in the sync and async clients with similar APIs.

---

## Tool Calls and Automatic Execution

The SDK supports **tool-augmented LLM workflows**.
Register your own functions for use in chat:

```python
def my_tool(args):
    # Custom business logic
    return {"result": "tool output"}


client.tools.register("my_tool", my_tool)
response = client.chat.complete(
    input="Use the tool please.",
    model="llm-aisberg",
    tools=[{"name": "my_tool", ...}],
    auto_execute_tools=True,
)
```

---

## Advanced Usage

### **Custom Configuration**

You can override configuration when instantiating the client:

```python
client = AisbergClient(
    api_key="...",
    base_url="https://url",
    timeout=60,
)
```

### **Environment Variables Supported**

* `AISBERG_API_KEY`
* `AISBERG_BASE_URL`
* `AISBERG_TIMEOUT` (optional)
* `S3_ACCESS_KEY_ID` (for document parsing)(optional)
* `S3_SECRET_ACCESS_KEY` (for document parsing)(optional)
* `S3_ENDPOINT` (for document parsing)(optional)

### **Using in a Context Manager**

Both clients are context manager compatible:

```python
with AisbergClient() as client:
    # Sync usage
    ...

async with AisbergAsyncClient() as client:
    # Async usage
    ...
```

---

## License

**Private License — Not for public distribution or resale.**

For enterprise/commercial use, please contact [Mathis Lambert](mailto:mathis.lambert@freepro.com) or Free Pro.

---

## Authors

* Mathis Lambert
* Free Pro

---

## Support

For support, bug reports, or feature requests, please contact your technical representative.
