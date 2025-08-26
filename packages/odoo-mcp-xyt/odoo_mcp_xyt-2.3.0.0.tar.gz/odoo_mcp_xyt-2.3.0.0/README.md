# UVX 方式安装 odoo mcp 服务

```
{
    "mcpServers": {
        "odoo-mcp-xyt": {
            "command": "uvx",
            "args": [
                "odoo-mcp-xyt==2.1.0.0"
            ],
            "env": {
                "ODOO_URL": "",
                "ODOO_DB": "",
                "ODOO_USERNAME": "",
                "ODOO_PASSWORD": ""
            }
        }
    }
}
```

# Odoo MCP Server

An MCP server implementation that integrates with Odoo ERP systems, enabling AI assistants to interact with Odoo data and functionality through the Model Context Protocol.

**[中文文档 / Chinese Documentation](README_zh.md)**

## Quick Start

1. **Install Python 3.10+** and create a virtual environment
2. **Clone and install** the project:
   ```bash
   git clone <repository-url>
   cd odoo-mcp-xyt
   pip install -e .
   ```
3. **Configure Odoo connection** in `odoo_config.json`:
   ```json
   {
     "url": "https://your-odoo-instance.com",
     "db": "your-database-name",
     "username": "your-username",
     "password": "your-password-or-api-key"
   }
   ```
4. **Run the server**:
   ```bash
   python -m odoo_mcp
   ```
5. **Test with MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector
   ```

## Features

- **Comprehensive Odoo Integration**: Full access to Odoo models, records, and methods
- **XML-RPC Communication**: Secure connection to Odoo instances via XML-RPC
- **Flexible Configuration**: Support for config files and environment variables
- **Resource Pattern System**: URI-based access to Odoo data structures
- **Error Handling**: Clear error messages for common Odoo API issues
- **Stateless Operations**: Clean request/response cycle for reliable integration

## Tools

- **execute_method**

  - Execute a custom method on an Odoo model
  - Inputs:
    - `model` (string): The model name (e.g., 'res.partner')
    - `method` (string): Method name to execute
    - `args` (optional array): Positional arguments
    - `kwargs` (optional object): Keyword arguments
  - Returns: Dictionary with the method result and success indicator

- **search_employee**

  - Search for employees by name
  - Inputs:
    - `name` (string): The name (or part of the name) to search for
    - `limit` (optional number): The maximum number of results to return (default 20)
  - Returns: Object containing success indicator, list of matching employee names and IDs, and any error message

- **search_holidays**

  - Searches for holidays within a specified date range
  - Inputs:
    - `start_date` (string): Start date in YYYY-MM-DD format
    - `end_date` (string): End date in YYYY-MM-DD format
    - `employee_id` (optional number): Optional employee ID to filter holidays
  - Returns: Object containing success indicator, list of holidays found, and any error message

## Resources

- **odoo://models**

  - Lists all available models in the Odoo system
  - Returns: JSON array of model information

- **odoo://model/{model_name}**

  - Get information about a specific model including fields
  - Example: `odoo://model/res.partner`
  - Returns: JSON object with model metadata and field definitions

- **odoo://record/{model_name}/{record_id}**

  - Get a specific record by ID
  - Example: `odoo://record/res.partner/1`
  - Returns: JSON object with record data

- **odoo://search/{model_name}/{domain}**

  - Search for records that match a domain
  - Example: `odoo://search/res.partner/[["is_company","=",true]]`
  - Returns: JSON array of matching records (limited to 10 by default)

## Configuration

### Odoo Connection Setup

1. Create a configuration file named `odoo_config.json`:

```json
{
  "url": "https://your-odoo-instance.com",
  "db": "your-database-name",
  "username": "your-username",
  "password": "your-password-or-api-key"
}
```

2. Alternatively, use environment variables:
   - `ODOO_URL`: Your Odoo server URL
   - `ODOO_DB`: Database name
   - `ODOO_USERNAME`: Login username
   - `ODOO_PASSWORD`: Password or API key
   - `ODOO_TIMEOUT`: Connection timeout in seconds (default: 30)
   - `ODOO_VERIFY_SSL`: Whether to verify SSL certificates (default: true)
   - `HTTP_PROXY`: Force the ODOO connection to use an HTTP proxy

### Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "python",
      "args": ["-m", "odoo_mcp"],
      "env": {
        "ODOO_URL": "https://your-odoo-instance.com",
        "ODOO_DB": "your-database-name",
        "ODOO_USERNAME": "your-username",
        "ODOO_PASSWORD": "your-password-or-api-key"
      }
    }
  }
}
```

### Docker

```json
{
  "mcpServers": {
    "odoo": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "ODOO_URL",
        "-e",
        "ODOO_DB",
        "-e",
        "ODOO_USERNAME",
        "-e",
        "ODOO_PASSWORD",
        "mcp/odoo"
      ],
      "env": {
        "ODOO_URL": "https://your-odoo-instance.com",
        "ODOO_DB": "your-database-name",
        "ODOO_USERNAME": "your-username",
        "ODOO_PASSWORD": "your-password-or-api-key"
      }
    }
  }
}
```

## Installation and Setup

### Prerequisites

- Python 3.10+ (required for MCP compatibility)
- Node.js (for MCP Inspector)

### 1. Environment Setup

Create a Python 3.10+ environment:

```bash
# Using conda
conda create -n odoo-mcp python=3.10 -y
conda activate odoo-mcp

# Or using venv
python3.10 -m venv odoo-mcp
source odoo-mcp/bin/activate  # On Windows: odoo-mcp\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install the project in development mode
pip install -e .

# Install MCP CLI tools for debugging
pip install 'mcp[cli]'
```

### 3. Configuration

Create `odoo_config.json` with your Odoo connection details:

```json
{
  "url": "https://your-odoo-instance.com",
  "db": "your-database-name",
  "username": "your-username",
  "password": "your-password-or-api-key"
}
```

## Running and Debugging

### Method 1: Direct Python Execution (Recommended)

```bash
# Using the installed package command
/path/to/your/python/bin/odoo-mcp-xyt

# Using Python module
/path/to/your/python/bin/python -m odoo_mcp

# Using the detailed logging script
/path/to/your/python/bin/python run_server.py
```

### Method 2: MCP Inspector for Development and Testing

#### Step 1: Start MCP Inspector

```bash
# Start the inspector
npx @modelcontextprotocol/inspector
```

This will output something like:

```
⚙️ Proxy server listening on 127.0.0.1:6277
🔑 Session token: your-session-token-here
🔗 Open inspector with token pre-filled:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=your-session-token-here
🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀
```

#### Step 2: Configure Server in Inspector

1. Open the Inspector URL in your browser
2. Enter the session token if prompted
3. Click "Add Server" and use this configuration:

```json
{
  "name": "Odoo MCP Server",
  "command": "/path/to/your/python/bin/python",
  "args": ["/path/to/your/project/start_for_inspector.py"],
  "env": {}
}
```

**Example with actual paths:**

```json
{
  "name": "Odoo MCP Server",
  "command": "/Users/username/miniconda3/envs/odoo-mcp/bin/python",
  "args": ["/Users/username/code/odoo-mcp-xyt/start_for_inspector.py"],
  "env": {}
}
```

### Method 3: Using MCP Development Tools (Alternative)

```bash
# Basic usage
mcp dev src/odoo_mcp/server.py

# With additional dependencies
mcp dev src/odoo_mcp/server.py --with pandas --with numpy

# Mount local code for development
mcp dev src/odoo_mcp/server.py --with-editable .
```

**Note:** If you encounter `uv` related errors, use Method 1 or 2 instead.

## Troubleshooting

### Common Issues

1. **Python Version Error**: Ensure you're using Python 3.10+

   ```bash
   python --version  # Should show 3.10 or higher
   ```

2. **Connection Errors**: Test your Odoo connection

   ```bash
   python diagnose_connection.py
   ```

3. **MCP Inspector JSON Errors**: Use Method 2 (manual Inspector setup) instead of `mcp dev`

4. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -e .
   pip install 'mcp[cli]'
   ```

### Debugging Tools

- **Connection Diagnostics**: `python diagnose_connection.py`
- **Detailed Logging**: `python run_server.py` (creates logs in `logs/` directory)
- **MCP Inspector**: Use for interactive testing and debugging

## Usage Examples

Once your server is running, you can test it using the MCP Inspector or integrate it with Claude Desktop. Here are some example operations:

### Testing Tools in MCP Inspector

1. **Search for employees**:

   ```json
   {
     "name": "search_employee",
     "arguments": {
       "name": "John",
       "limit": 10
     }
   }
   ```

2. **Execute custom methods**:

   ```json
   {
     "name": "execute_method",
     "arguments": {
       "model": "res.partner",
       "method": "search_read",
       "args": [[["is_company", "=", true]], ["name", "email"]]
     }
   }
   ```

3. **Search holidays**:
   ```json
   {
     "name": "search_holidays",
     "arguments": {
       "start_date": "2024-01-01",
       "end_date": "2024-12-31",
       "employee_id": 1
     }
   }
   ```

### Testing Resources in MCP Inspector

1. **List all models**: `odoo://models`
2. **Get partner model info**: `odoo://model/res.partner`
3. **Get specific partner**: `odoo://record/res.partner/1`
4. **Search companies**: `odoo://search/res.partner/[["is_company","=",true]]`

## Build

Docker build:

```bash
docker build -t mcp/odoo:latest -f Dockerfile .
```

## Parameter Formatting Guidelines

When using the MCP tools for Odoo, pay attention to these parameter formatting guidelines:

1. **Domain Parameter**:

   - The following domain formats are supported:
     - List format: `[["field", "operator", value], ...]`
     - Object format: `{"conditions": [{"field": "...", "operator": "...", "value": "..."}]}`
     - JSON string of either format
   - Examples:
     - List format: `[["is_company", "=", true]]`
     - Object format: `{"conditions": [{"field": "date_order", "operator": ">=", "value": "2025-03-01"}]}`
     - Multiple conditions: `[["date_order", ">=", "2025-03-01"], ["date_order", "<=", "2025-03-31"]]`

2. **Fields Parameter**:

   - Should be an array of field names: `["name", "email", "phone"]`
   - The server will try to parse string inputs as JSON

## License

This MCP server is licensed under the MIT License.
