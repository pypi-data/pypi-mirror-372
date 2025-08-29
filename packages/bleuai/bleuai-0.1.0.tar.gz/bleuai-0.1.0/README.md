# Bleu AI Python SDK

A Python client library for interacting with Bleu AI workflows.

## Installation

```bash
pip install bleuai
```

## Quick Start

```python
import asyncio
from bleuai import BleuAI

async def main():
    # Initialize the client with your API key
    client = BleuAI(api_key="your-api-key-here")
    
    # Run a workflow and wait for completion
    result = await client.run_workflow(
        workflow_id="your-workflow-uuid",
        inputs={
            "prompt": "Generate an image of a sunset over mountains"
        }
    )
    
    # Check if successful
    if result.is_completed:
        print("Workflow completed successfully!")
        print(f"Outputs: {result.outputs}")
    else:
        print(f"Workflow failed: {result.error}")
    
    # Close the client
    await client.close()

# Run the async function
asyncio.run(main())
```

## Example

See `example.py` for a complete working example:

```bash
export BLEU_API_KEY="your-api-key"
python example.py
```

## Usage

### Basic Usage

The SDK provides a simple interface to run Bleu AI workflows:

```python
from bleuai import BleuAI

# Create client
client = BleuAI(api_key="your-api-key")

# Run workflow (async)
result = await client.run_workflow(
    workflow_id="workflow-uuid",
    inputs={"key": "value"}
)
```

### Synchronous Usage

For non-async environments, use the synchronous wrapper:

```python
from bleuai import BleuAI

client = BleuAI(api_key="your-api-key")

# This creates an event loop internally
result = client.run_workflow_sync(
    workflow_id="workflow-uuid",
    inputs={"key": "value"}
)
```

### Context Manager

The client can be used as an async context manager:

```python
async with BleuAI(api_key="your-api-key") as client:
    result = await client.run_workflow(
        workflow_id="workflow-uuid",
        inputs={"prompt": "Hello, world!"}
    )
```

### Handling Results

The `WorkflowResult` object provides convenient access to outputs:

```python
result = await client.run_workflow(workflow_id="...", inputs={...})

# Check status
if result.is_completed:
    # Get all outputs
    all_outputs = result.outputs
    
    # Get output from specific node
    node_output = result.get_output(node_id="node-123")
    
    # Get outputs by type
    images = result.get_output(output_type="image")
    
elif result.is_failed:
    print(f"Error: {result.error}")
```

### Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from bleuai import (
    BleuAI,
    AuthenticationError,
    WorkflowNotFoundError,
    InsufficientCreditsError,
    WorkflowExecutionError
)

try:
    client = BleuAI(api_key="your-api-key")
    result = await client.run_workflow(
        workflow_id="workflow-uuid",
        inputs={"prompt": "Generate something"}
    )
except AuthenticationError:
    print("Invalid API key")
except WorkflowNotFoundError:
    print("Workflow not found or no access")
except InsufficientCreditsError:
    print("Not enough credits to run workflow")
except WorkflowExecutionError as e:
    print(f"Workflow execution failed: {e}")
```

### Timeout Configuration

You can configure the timeout for workflow execution:

```python
# Wait up to 10 minutes for completion
result = await client.run_workflow(
    workflow_id="workflow-uuid",
    inputs={...},
    timeout=600.0  # seconds
)
```

### Fire and Forget

To start a workflow without waiting for completion:

```python
# Start workflow and return immediately
result = await client.run_workflow(
    workflow_id="workflow-uuid",
    inputs={...},
    wait_for_completion=False
)

print(f"Workflow started with job ID: {result.job_id}")
```

## API Reference

### BleuAI

Main client class for interacting with Bleu AI.

#### Constructor

```python
BleuAI(
    api_key: str,
    base_url: str = "https://api.buildbleu.com",
    supabase_url: str = "...",
    supabase_anon_key: str = "..."
)
```

#### Methods

- `async run_workflow(workflow_id, inputs, wait_for_completion, timeout)` - Run a workflow
- `run_workflow_sync(workflow_id, inputs, timeout)` - Synchronous workflow execution
- `async close()` - Close the client connection

### WorkflowResult

Result object returned from workflow execution.

#### Attributes

- `job_id: str` - Unique job identifier
- `status: WorkflowStatus` - Current status (PENDING, RUNNING, COMPLETED, FAILED)
- `outputs: Optional[Dict]` - Workflow outputs (when completed)
- `error: Optional[str]` - Error message (when failed)

#### Methods

- `is_completed: bool` - Check if workflow completed successfully
- `is_failed: bool` - Check if workflow failed
- `get_output(node_id, output_type)` - Get specific outputs

## Requirements

- Python 3.7+
- httpx
- supabase
- realtime

## License

MIT

## Support

For support, please contact contact@buildbleu.com or visit [https://buildbleu.com](https://buildbleu.com)
