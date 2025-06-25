# MCP Elicitation Demo: Interactive

A demonstration of the Model Context Protocol (MCP) with intelligent elicitation capabilities for interactive data gathering. This project showcases how an MCP server can dynamically request information from clients when needed.

## Demo Video
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/b4D4BSAHKgg/0.jpg)](https://www.youtube.com/watch?v=b4D4BSAHKgg](https://www.youtube.com/watch?v=b4D4BSAHKgg))


## Overview

This demo implements a restaurant table booking system that demonstrates MCP's elicitation feature. The server can intelligently request missing or invalid data from the client through interactive prompts.

## Features

- **Intelligent Elicitation**: Server requests missing parameters dynamically
- **Input Validation**: Validates dates, party sizes, and other booking details
- **Error Handling**: Graceful handling of user cancellations and errors
- **Multiple Scenarios**: Supports various booking scenarios for testing
- **Type Safety**: Full type hints and Pydantic schema validation

## Project Structure

```
mcp-elicitation-example/
├── .gitignore              # Git ignore patterns
├── .python-version         # Python version specification
├── elicitation-server.py   # MCP server with booking tool
├── elicitation-client.py   # Interactive client for testing
├── pyproject.toml          # Project dependencies and configuration
├── README.md              # This file
└── uv.lock                # Dependency lock file
```

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd mcp-elicitation-example
   ```

2. **Install dependencies using uv**:
   ```bash
   uv sync
   ```
   
   This will automatically:
   - Create a virtual environment with Python 3.11+
   - Install all dependencies from `pyproject.toml`
   - Lock dependencies in `uv.lock` for reproducible builds

   > **Note**: No need to manually create or activate a virtual environment - `uv` handles this automatically!

   **Alternative (using pip)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

## Usage

### Running the Server

Start the MCP server in one terminal:

```bash
uv run python elicitation-server.py
```

The server will start on `http://localhost:8000/mcp` by default.

### Running the Client

In another terminal, run the interactive client:

```bash
uv run python elicitation-client.py
```

> **Tip**: Use `uv run` to automatically use the project's virtual environment without manual activation!

### Demo Scenarios

The client demonstrates three scenarios:

1. **Full Elicitation**: No initial parameters - server requests all data
2. **Partial Data**: Only date provided - server requests party size
3. **Invalid Data**: Past date provided - server validates and requests correction

## How It Works

### Server Implementation (`elicitation-server.py`)

- **FastMCP Server**: Uses the FastMCP framework for easy setup
- **Pydantic Schemas**: Defines validation schemas for different input types
- **Elicitation Handler**: Generic function for requesting data with validation
- **Book Table Tool**: Main tool that orchestrates the booking process

### Client Implementation (`elicitation-client.py`)

- **Smart Callback**: Interprets server requests and prompts user appropriately
- **Input Validation**: Client-side validation with retry logic
- **Multiple Scenarios**: Tests different combinations of initial data
- **Error Handling**: Graceful handling of user cancellations

### Key Components

#### Elicitation Schemas

```python
class GetDate(BaseModel):
    date: str = Field(
        description="Enter the date for your booking (YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
```

#### Server Tool

```python
@mcp.tool()
async def book_table(ctx: Context, date: str = "", party_size: int = 0) -> str:
    """Book a table with intelligent elicitation for missing or invalid data."""
```

#### Client Callback

```python
async def smart_elicitation_callback(
    context: RequestContext["ClientSession", Any],
    params: types.ElicitRequestParams,
) -> types.ElicitResult | types.ErrorData:
```

## Technical Details

### Dependencies

- **mcp[cli]**: Model Context Protocol SDK
- **pydantic**: Data validation and settings management
- **anyio**: Async I/O library
- **asyncio**: Python's built-in async framework

### Validation Rules

- **Date Format**: Must be YYYY-MM-DD and not in the past
- **Party Size**: Must be between 1 and 20 people
- **Confirmation**: Boolean with optional notes field

### Error Handling

- Client disconnection during elicitation
- Invalid input formats
- User cancellations at any step
- Network timeouts and connection errors

## Example Interaction

```
🍽️  Starting table booking process...

--- Testing: No arguments (full elicitation) ---

--- Server Request ---
Message: Please enter the date for your booking:
Enter the date for your booking (YYYY-MM-DD): 2025-07-15

--- Server Request ---
Message: Please enter the party size for your booking:
Enter the number of people (1-20): 4

--- Server Request ---
Message: Please confirm your booking for 4 people on 2025-07-15.
Do you want to confirm this booking? (y/n): y
Any special requests or notes? (optional): Window table please

✅ Result: ✅ Your table for 4 people on 2025-07-15 has been booked. Notes: Window table please
```

## Development

### Code Style

The project follows PEP 8 standards with:
- Maximum line length: 79 characters
- Type hints for all functions
- Docstrings for classes and functions
- Consistent naming conventions

### Testing

Run the client to test different scenarios:

```bash
python elicitation-client.py
```

The client will automatically test three scenarios and prompt for continuation between each.

### Extending the Demo

To add new elicitation types:

1. **Define a schema** in `ElicitationSchema` class
2. **Add handling logic** in the server tool
3. **Update client callback** to handle new request types
4. **Test the new functionality** with the client

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the server is running before starting the client
2. **Port Already in Use**: Check if another process is using port 8000
3. **Import Errors**: Ensure all dependencies are installed with `uv sync`

### Debug Mode

Enable debug logging by modifying the logging level in `elicitation-server.py`:

```python
logging.getLogger("mcp").setLevel(logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper tests
4. Ensure code follows the style guidelines
5. Submit a pull request

## License

This project is provided as a demonstration of MCP capabilities. Please refer to the MCP SDK license for usage terms.

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

*This demo showcases the power of MCP's elicitation feature for building interactive, intelligent tools that can gather information dynamically from users.*