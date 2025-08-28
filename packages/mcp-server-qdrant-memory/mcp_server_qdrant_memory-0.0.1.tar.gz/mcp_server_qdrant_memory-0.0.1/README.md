# MCP Qdrant Memory Server

A Model Context Protocol (MCP) server that provides persistent memory and semantic search capabilities using Qdrant vector database and SentenceTransformer embeddings, built with FastMCP.

## Features

### Memory Operations
- Store and retrieve documents with semantic search
- Support for multiple text sources (text, raw markdown, headers)
- Automatic text embedding using SentenceTransformer models
- Metadata-based filtering and search capabilities

### Collection Management
- Dynamic collection creation and recreation
- Named vector support with configurable dimensions
- Payload indexing for efficient metadata queries
- Automatic schema validation and compatibility checking

### Search Capabilities
- **Vector Search**: Semantic similarity search using text embeddings
- **Hybrid Search**: Combined vector and metadata filtering
- **Filter-Only Search**: Pure metadata-based queries without vector search
- **Batch Operations**: Efficient bulk upsert and deletion

### Transport Protocols
- **STDIO** (default) - For local tools and Claude Desktop integration
- **SSE** (Server-Sent Events) - For web-based deployments
- **Streamable HTTP** - Modern HTTP-based protocol

## Architecture

The server uses a clean, scalable architecture:

- **FastMCP Integration**: Modern MCP server framework with multi-transport support
- **Qdrant Vector Database**: High-performance vector storage and search
- **SentenceTransformer**: State-of-the-art text embedding generation
- **Stable ID Generation**: UUIDv5-based consistent document identification
- **Flexible Text Sources**: Support for various document formats and structures

## Installation

### Quick Install from PyPI

Once published to PyPI, you can install and run easily:

```bash
# Install with uv (recommended)
uvx mcp-server-qdrant-memory  # Run directly without installation

# Or install with pip
pip install mcp-server-qdrant-memory
```

### Install from Source

#### Prerequisites

Create and activate a virtual environment:

```bash
python -m venv venv

# On Windows
.\venv\Scripts\Activate.ps1

# On Linux/macOS
source venv/bin/activate
```

### Basic Installation

Install the project in editable mode:

#### For Production Use

```bash
pip install -e "."
```

#### For Development

Install with development tools included:

```bash
pip install -e ".[dev]"
```

### Dependencies

**Core dependencies** (automatically installed):
- `mcp>=1.9.4` - Model Context Protocol library
- `fastmcp>=2.3.0` - Modern MCP server framework
- `qdrant_client>=1.14.3` - Qdrant vector database client
- `sentence-transformers>=5.0.0` - Text embedding models

**Development dependencies** (installed with `[dev]`):
- `pylint` - Code linting
- `pylint-plugin-utils` - Pylint utilities
- `pylint-mcp` - MCP-specific linting rules
- `black` - Code formatting

### Installation Examples

#### Quick Start (Production)
```bash
# Clone and install
git clone <repository-url>
cd mcp-server-qdrant-memory
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -e "."
```

#### Developer Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd mcp-server-qdrant-memory
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -e ".[dev]"

# Run development tools
black src/
pylint src/
```

## Configuration

The server is configured through environment variables:

### Required Setup

1. **Qdrant Server**: Start a Qdrant instance
```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant
```

2. **Environment Variables** (optional, with defaults):
```bash
export QDRANT_URL="http://127.0.0.1:6333"           # Qdrant server URL
export QDRANT_API_KEY=""                             # API key (if required)
export QDRANT_COLLECTION_NAME="kakehashi_rag_v2"    # Collection name
export QDRANT_VECTOR_NAME="fast-all-minilm-l6-v2"   # Named vector identifier
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"  # Embedding model
export EMBEDDING_BATCH="64"                         # Batch size for embeddings
export MCP_TRANSPORT="stdio"                        # Transport protocol
```

## Usage

### Command Line Options

```bash
mcp-server-qdrant-memory --help
```

### Development Mode

Use FastMCP's development mode with inspector:
```bash
fastmcp dev src/qdrant_memory_server/main.py
```

### MCP Inspector

You can use the MCP Inspector to test and debug your MCP server interactively:

```bash
# Install and run MCP Inspector
npx @modelcontextprotocol/inspector
```

The MCP Inspector provides a web-based interface to:
- Test all available tools
- View tool schemas and documentation
- Debug server responses
- Monitor server logs

## Integration Examples

### Claude Desktop Integration

Add to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "qdrant-memory": {
      "command": "mcp-server-qdrant-memory",
      "args": [],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION_NAME": "claude_memory"
      }
    }
  }
}
```

Or after PyPI publication, use uvx for automatic installation:

```json
{
  "mcpServers": {
    "qdrant-memory": {
      "command": "uvx",
      "args": ["mcp-server-qdrant-memory"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION_NAME": "claude_memory"
      }
    }
  }
}
```
