# Snowlgobe Connect SDK

The Snowglobe Connect SDK helps you connect your AI agents to Snowglobe. It sends simulated user messages to your LLM-based application during experiments. Your application should process these messages and return a response, enabling simulated conversations and custom code based risk assessment.

## Installation

```
# Install client
pip install snowglobe
```

If using uv, set the `--prerelease=allow` flag
```
uv pip install --prerelease=allow snowglobe
```


## `snowglobe-connect` commands

```bash
snowglobe-connect auth  # Sets up your API key
snowglobe-connect init  # Initializes a new agent connection and creates an agent wrapper file
snowglobe-connect test  # Tests your agent connection
snowglobe-connect start  # Starts the process of processing simulated user messages
snowglobe-connect --help
```

When using one of our specific preview environments in .snowgloberc one can override our server's URL with:

```bash
CONTROL_PLANE_URL=
```

## Sample custom llm usage in agent wrapper file

Each agent wrapper file resides in the root directory of your project, and is named after the agent (e.g. `My Agent Name` becomes `my_agent_name.py`).

```python
from snowglobe.client import CompletionRequest, CompletionFunctionOutputs
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("SNOWGLOBE_API_KEY"))

def process_scenario(request: CompletionRequest) -> CompletionFunctionOutputs:
    """
    Process a scenario request from Snowglobe.
    
    This function is called by the Snowglobe client to process requests. It should return a
    CompletionFunctionOutputs object with the response content.

    Example CompletionRequest:
    CompletionRequest(
        messages=[
            SnowglobeMessage(role="user", content="Hello, how are you?", snowglobe_data=None),
        ]
    )

    Example CompletionFunctionOutputs:
    CompletionFunctionOutputs(response="This is a string response from your application")
    
    Args:
        request (CompletionRequest): The request object containing the messages.

    Returns:
        CompletionFunctionOutputs: The response object with the generated content.
    """

    # Process the request using the messages. Example:
    messages = request.to_openai_messages()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return CompletionFunctionOutputs(response=response.choices[0].message.content)
```
