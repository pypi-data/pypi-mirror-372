# Development Guide

This guide explains how to extend the Nosto Email Widgets MCP Server with new tools.

## Project Structure

```
nosto_email_widgets_mcp/
├── src/
│   ├── tools/           # All MCP tools go here
│   │   ├── __init__.py  # Tool imports
│   │   └── *.py         # Individual tool files
│   ├── server.py        # Main server configuration
│   └── __init__.py      # Package initialization
├── main.py              # Server entry point
├── requirements.txt      # Dependencies
└── test_tools.py        # Tool testing
```

## Adding a New Tool

### 1. Create the Tool File

Create a new file in `src/tools/` following this pattern:

```python
"""
Your Tool Name

Description of what the tool does.
"""

from typing import Optional
from mcp import Tool
from pydantic import BaseModel, Field


class YourToolRequest(BaseModel):
    """Request model for your tool."""
    
    required_field: str = Field(
        description="Description of the required field"
    )
    
    optional_field: Optional[str] = Field(
        default=None,
        description="Description of the optional field"
    )


class YourTool(Tool):
    """Your tool implementation."""
    
    name: str = "your_tool_name"
    description: str = "Description of what your tool does"
    input_schema: type[YourToolRequest] = YourToolRequest
    
    def __call__(self, request: YourToolRequest) -> str:
        """Main tool logic goes here."""
        
        # Your tool implementation
        result = self._process_request(request)
        
        return result
    
    def _process_request(self, request: YourToolRequest) -> str:
        """Process the request and return result."""
        # Implementation details
        pass
```

### 2. Register the Tool

Add your tool to `src/tools/__init__.py`:

```python
from .your_tool import YourTool

__all__ = ["EmailTemplateGenerator", "EmailAnalyticsDashboard", "YourTool"]
```

### 3. Add to Server

Register your tool in `src/server.py`:

```python
from .tools import EmailTemplateGenerator, EmailAnalyticsDashboard, YourTool

def create_server() -> Server:
    server = Server("nosto-email-widgets")
    
    # Register tools
    server.register_tool(EmailTemplateGenerator())
    server.register_tool(EmailAnalyticsDashboard())
    server.register_tool(YourTool())  # Add your tool here
    
    return server
```

### 4. Test Your Tool

Add tests to `test_tools.py`:

```python
def test_your_tool():
    """Test your new tool."""
    
    print("Testing Your Tool...")
    
    tool = YourTool()
    request = YourToolRequest(required_field="test value")
    result = tool(request)
    
    print(f"✅ Tool executed successfully!")
    print(f"Result: {result}")
    
    return result
```

## Tool Best Practices

### 1. Input Validation
- Use Pydantic models for request validation
- Provide clear field descriptions
- Use appropriate field types and constraints

### 2. Error Handling
- Handle errors gracefully
- Return meaningful error messages
- Log errors for debugging

### 3. Documentation
- Write clear docstrings
- Include examples in comments
- Document any external dependencies

### 4. Testing
- Test with various input combinations
- Test edge cases and error conditions
- Ensure consistent output format

## Example: Simple Text Tool

Here's a complete example of a simple text processing tool:

```python
"""
Text Processor Tool

Processes text input with various transformations.
"""

from typing import Literal
from mcp import Tool
from pydantic import BaseModel, Field


class TextProcessRequest(BaseModel):
    """Request model for text processing."""
    
    text: str = Field(
        description="The text to process"
    )
    
    operation: Literal["uppercase", "lowercase", "reverse", "word_count"] = Field(
        description="The operation to perform on the text"
    )


class TextProcessor(Tool):
    """Tool for processing text."""
    
    name: str = "text_processor"
    description: str = "Process text with various transformations like uppercase, lowercase, reverse, and word count"
    input_schema: type[TextProcessRequest] = TextProcessRequest
    
    def __call__(self, request: TextProcessRequest) -> str:
        """Process the text according to the specified operation."""
        
        if request.operation == "uppercase":
            return request.text.upper()
        elif request.operation == "lowercase":
            return request.text.lower()
        elif request.operation == "reverse":
            return request.text[::-1]
        elif request.operation == "word_count":
            return str(len(request.text.split()))
        else:
            return f"Unknown operation: {request.operation}"
```

## Running in Development

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Test individual tools:**
   ```bash
   python test_tools.py
   ```

3. **Check server health:**
   ```bash
   curl http://localhost:8000/health
   ```

4. **Test MCP endpoint:**
   ```bash
   curl -X POST http://localhost:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
   ```

## Debugging

- Enable debug logging in `config.py`
- Use `print()` statements for quick debugging
- Check server logs for errors
- Test tools independently with `test_tools.py`

## Deployment

For production deployment:

1. Set `DEBUG = False` in `config.py`
2. Set `RELOAD = False` in `main.py`
3. Use a production WSGI server like Gunicorn
4. Set up proper logging and monitoring
5. Configure CORS appropriately
6. Use environment variables for configuration
