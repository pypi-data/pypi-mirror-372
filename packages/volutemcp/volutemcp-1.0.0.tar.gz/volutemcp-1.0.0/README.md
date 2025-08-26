# VoluteMCP Server

A FastMCP 2.0-based Model Context Protocol (MCP) server providing various tools, resources, and prompts for AI model interaction.

## Features

- 🔧 **Tools**: Mathematical calculations, text processing, JSON manipulation, hashing, encoding/decoding
- 📊 **PowerPoint Tools**: Comprehensive PowerPoint analysis, metadata extraction, and content processing
- 📁 **Resources**: System status, user data, configuration sections, simulated logs
- 📝 **Prompts**: Data analysis prompts, code review templates
- 🌐 **HTTP Endpoints**: Health checks and server information
- 🏷️ **Tag-based Filtering**: Organize components with flexible tag system
- ⚙️ **Configuration**: Environment-based configuration with Pydantic models

## Quick Start

### 1. Setup Environment

```bash
# Clone or create the project
cd volutemcp

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# SERVER_NAME=VoluteMCP
# SERVER_HOST=127.0.0.1
# SERVER_PORT=8000
```

### 3. Run the Server

#### HTTP Transport (Web Service)
```bash
python server.py
```
Server will be available at: http://127.0.0.1:8000

#### STDIO Transport (Local Tool)
```bash
python server.py stdio
```

## Server Components

### Tools

| Tool | Description | Tags |
|------|-------------|------|
| `echo` | Echo back messages for testing | utility, public |
| `calculate` | Safely evaluate math expressions | math, utility |
| `get_server_info` | Get server environment info | system, info |
| `format_text` | Format text (upper, lower, title, reverse) | utility, text |
| `process_json` | Process JSON (pretty, minify, keys, validate) | data, json |
| `get_timestamp` | Get timestamps in various formats | system, time |
| `list_operations` | Perform operations on string lists | data, list |
| `hash_text` | Generate text hashes (SHA256, SHA1, MD5) | security, hash |
| `encode_decode` | Encode/decode text (base64, URL, hex) | development, base64 |

### PowerPoint Tools

Advanced PowerPoint analysis and processing capabilities:

| Tool | Description |
|------|-------------|
| `extract_powerpoint_metadata` | Extract comprehensive metadata from PowerPoint presentations |
| `analyze_powerpoint_content` | Analyze content of specific slides or entire presentations |
| `get_powerpoint_summary` | Get high-level summary of a PowerPoint presentation |
| `validate_powerpoint_file` | Validate PowerPoint files and check for common issues |

#### PowerPoint Features

- **Comprehensive Metadata Extraction**: Core properties, slide dimensions, layout information
- **Shape Analysis**: Position, size, formatting, and content of all shapes
- **Text Content**: Fonts, colors, alignment, paragraph and run-level formatting
- **Multimedia Elements**: Images with crop information, tables with cell data
- **Formatting Details**: Fill, line, shadow formatting for all objects
- **Slide Structure**: Master slides, layouts, notes, and comments
- **Content Summarization**: Automatic extraction of slide titles and content
- **File Validation**: Format checking, corruption detection, structural integrity

### Resources

#### Static Resources
- `config://server` - Server configuration
- `data://environment` - Environment information  
- `system://status` - System status
- `data://sample-users` - Sample user data
- `config://features` - Available features

#### Resource Templates
- `users://{user_id}` - Get user by ID
- `config://{section}` - Get config section
- `data://{data_type}/summary` - Get data summaries
- `logs://{log_level}` - Get simulated logs
- `file://{file_path}` - Read file contents (with safety checks)

### Prompts

- `analyze_data` - Generate data analysis prompts
- `code_review_prompt` - Generate code review prompts

### Custom HTTP Routes

- `GET /health` - Health check endpoint
- `GET /info` - Server information

## Usage Examples

### Using with MCP Clients

The server can be used with any MCP-compatible client. Here are some examples:

#### Call a Tool
```python
# Using an MCP client library
result = client.call_tool("calculate", {"expression": "2 + 3 * 4"})
print(result)  # 14.0
```

#### Access a Resource
```python
# Get server config
config = client.read_resource("config://server")
print(config)

# Get specific user
user = client.read_resource("users://1")
print(user)
```

#### Use a Prompt
```python
# Generate analysis prompt
prompt = client.get_prompt("analyze_data", {
    "data_description": "Sales data for Q1 2024",
    "analysis_type": "trends"
})
```

#### PowerPoint Analysis
```python
# Extract comprehensive metadata from a presentation
result = client.call_tool("extract_powerpoint_metadata", {
    "presentation_path": "./presentation.pptx",
    "include_slide_content": True,
    "output_format": "json"
})

# Get a quick summary of the presentation
summary = client.call_tool("get_powerpoint_summary", {
    "presentation_path": "./presentation.pptx"
})

# Analyze specific slides only
content = client.call_tool("analyze_powerpoint_content", {
    "presentation_path": "./presentation.pptx",
    "slide_numbers": [1, 3, 5],
    "extract_text_only": True
})

# Validate a PowerPoint file
validation = client.call_tool("validate_powerpoint_file", {
    "presentation_path": "./presentation.pptx"
})
```

## Testing

The project includes a comprehensive test suite to validate all functionality:

### Running Tests

```bash
# Run all tests using the test runner
python run_tests.py

# Or run tests directly
python tests/test_powerpoint_tools.py

# Using pytest (if installed)
pytest tests/
```

### Test Coverage

The test suite validates:
- ✅ All module imports work correctly
- ✅ Pydantic data models function properly
- ✅ PowerPoint tools register and integrate correctly
- ✅ Server startup and configuration
- ✅ Error handling for edge cases
- ✅ FastMCP 2.0 async/await patterns

### Test Results

- **4 PowerPoint tools** properly registered
- **11 total tools** available (including core tools)
- **3 resources** configured
- **100% test pass rate**

## Development

### Project Structure

```
volutemcp/
├── server.py                    # Main server entry point
├── server_modular.py           # Modular server implementation
├── config.py                   # Configuration management
├── tools.py                    # Core tool implementations
├── resources.py                # Resource implementations
├── powerpoint_metadata.py      # PowerPoint metadata extraction
├── powerpoint_tools.py         # PowerPoint tool implementations
├── tests/                      # Test directory
│   ├── __init__.py            # Test package initialization
│   ├── test_powerpoint_tools.py # PowerPoint tools test suite
│   └── README.md              # Test documentation
├── run_tests.py               # Test runner script
├── pytest.ini                # Pytest configuration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

### Adding New Components

#### Add a Tool
```python
# In tools.py
@mcp.tool(tags={"custom", "utility"})
def my_custom_tool(input_data: str) -> str:
    """My custom tool description."""
    return f"Processed: {input_data}"
```

#### Add a Resource
```python
# In resources.py
@mcp.resource("custom://my-data")
def my_custom_resource() -> dict:
    """My custom resource description."""
    return {"data": "value"}
```

#### Add a Resource Template
```python
# In resources.py
@mcp.resource("items://{item_id}")
def get_item(item_id: int) -> dict:
    """Get item by ID."""
    return {"id": item_id, "name": f"Item {item_id}"}
```

### Configuration

The server uses Pydantic for configuration management. Settings can be provided via:

1. Environment variables (prefixed with `VOLUTE_`)
2. `.env` file
3. Default values in `config.py`

#### Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `VOLUTE_NAME` | VoluteMCP | Server name |
| `VOLUTE_HOST` | 127.0.0.1 | Server host |
| `VOLUTE_PORT` | 8000 | Server port |
| `VOLUTE_LOG_LEVEL` | INFO | Logging level |
| `VOLUTE_API_KEY` | None | Optional API key |

### Tag-Based Filtering

Filter components by tags when creating the server:

```python
# Only expose utility tools
mcp = FastMCP(include_tags={"utility"})

# Hide internal tools
mcp = FastMCP(exclude_tags={"internal"})

# Combine filters
mcp = FastMCP(include_tags={"public"}, exclude_tags={"deprecated"})
```

## Advanced Usage

### Server Composition

```python
from fastmcp import FastMCP
from tools import register_tools

# Create modular servers
tools_server = FastMCP("ToolsOnly")
register_tools(tools_server)

# Mount into main server
main_server = FastMCP("Main")
main_server.mount(tools_server, prefix="tools")
```

### Custom Serialization

```python
import yaml

def yaml_serializer(data):
    return yaml.dump(data, sort_keys=False)

mcp = FastMCP(tool_serializer=yaml_serializer)
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "server.py"]
```

### systemd Service

```ini
[Unit]
Description=VoluteMCP Server
After=network.target

[Service]
Type=simple
User=volute
WorkingDirectory=/opt/volutemcp
ExecStart=/opt/volutemcp/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes with tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Specification](https://spec.modelcontextprotocol.io)
