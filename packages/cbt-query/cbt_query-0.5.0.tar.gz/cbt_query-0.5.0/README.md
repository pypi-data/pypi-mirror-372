# CBT Query MCP Server

A simple Model Context Protocol (MCP) server for querying TensorRT test coverage and case mapping data.

## Features

- Query all test cases and files
- Get coverage mapping by case name
- Query cases by files and/or functions
- Simple HTTP client with proper error handling
- Minimal logging and clean code structure

## Installation

### Prerequisites

- Python 3.10 or later
- pip package manager

### Installation

#### installed from pypi
```bash
pip install cbt_query

```
### Configuration for Cursor

Add the following configuration to your `~/.cursor/mcp.json` file:
```
# ~/.cursor/mcp.json
{
  "mcpServers": {
    "trt_query": {
      "command": "python",
      "args": [
        "-m",
        "cbt_query"
      ],
      "env": {
        "CBT_SERVER_URL": "http://your_server_name:12345/"
      }
    }
  }
}
```

## Available Tools

The MCP server provides the following tools:

- `query_all_cases`: Get all test cases from the server
- `query_all_files`: Get all files from the server  
- `query_by_case`: Get coverage mapping by case name
- `query`: Query cases by files and/or functions
- `query_test_similarity`: Compare test coverage similarity between two test lists

## API Examples

```python
# Get all cases
await query_all_cases()

# Get all files
await query_all_files()

# Get coverage by case
await query_by_case("test_case_name")

# Query by file
await query(file_name="example.cpp")

# Query by function
await query(funcs="example_function")

# Query by file and function
await query(file_name="example.cpp", funcs="example_function")

# Compare test coverage similarity
await query_test_similarity("L0", "L1")
await query_test_similarity(["test1", "test2"], ["test3", "test4"])
await query_test_similarity("trt_mod_test", "infer_test", filter_test_list=True)
await query_test_similarity("turtle_test1", "turtle_test2", use_turtle_names=True)
```

## Development

uv init new_project
cd new_project

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

# Install dependencies
uv add "mcp[cli]" httpx requests pip


## Environment Setup

Make sure to set the `CBT_SERVER_URL` environment variable:

```bash
export CBT_SERVER_URL="http://your-server:12345"
```

### Debug Mode

To enable debug mode with detailed logging, set the `CBT_DEBUG` environment variable:

```bash
export CBT_DEBUG=1
# or
export CBT_DEBUG=true
```

## Troubleshooting

### Common Issues

1. **CBT_SERVER_URL not set**: Make sure the environment variable is set
2. **Import errors**: Verify all dependencies are installed in the active environment
3. **Connection errors**: Check that the CBT server is running and accessible

### Logging

The server logs to stderr with INFO level by default.
