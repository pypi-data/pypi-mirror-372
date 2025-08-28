# Valuator

A lightweight Python library to fetch AI model pricing data and perform searches to retrieve input and output costs per token for matching models.

## Installation

```bash
pip install valuator
```

## Usage

```python
import asyncio
from valuator import Valuator

async def main():
    valuator = Valuator()
    try:
        # Initialize with default force_refresh=True to fetch latest data
        await valuator.initialize()
        print(valuator.get_model_costs("claude.*haiku"))
        print(valuator.get_model_costs("gpt-4"))
        # Use force_refresh=False to prefer cache if unchanged
        await valuator.initialize(force_refresh=False)
        print(valuator.get_model_costs("gpt.*"))
    finally:
        await valuator.close()

asyncio.run(main())
```

## Example

```python
import asyncio
from valuator import Valuator

async def main():
    valuator = Valuator()
    try:
        await valuator.initialize()
        data = valuator.get_model_costs("us.anthropic.claude-3-5-sonnet-20240620-v1:0")
        if data:
            # Extract first matched model and its costs
            model_names = list(data.keys())
            selected_model = model_names[0]
            selected_model_costs = data[selected_model]

            print("Matched Model:")
            print(f"  Name: {selected_model}")
            print(f"  Input cost per token: {selected_model_costs['input_cost_per_token']}")
            print(f"  Output cost per token: {selected_model_costs['output_cost_per_token']}")
        else:
            print("No models found.")
    finally:
        await valuator.close()

asyncio.run(main())
```

Output:
```bash
Matched Model:
  Name: us.anthropic.claude-3-5-sonnet-20240620-v1:0
  Input cost per token: 3e-06
  Output cost per token: 1.5e-05
```

## Features

- Fetches model pricing data.
- Automatically checks if the remote JSON has changed using ETag headers.
- Defaults to fetching the latest data (`force_refresh=True`) to ensure up-to-date model prices.
- Performs regex-based searches on model names for flexible matching.
- Returns only `input_cost_per_token` and `output_cost_per_token` for matched models.
- Optimized for low memory usage with efficient data structures (sets, cached regex).
- Asynchronous HTTP requests for fast data retrieval.

## Requirements

- Python 3.8+
- `aiohttp>=3.8.0`

## License

MIT License