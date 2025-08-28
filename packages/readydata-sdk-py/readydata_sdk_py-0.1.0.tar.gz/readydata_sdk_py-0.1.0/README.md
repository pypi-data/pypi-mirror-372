# ReadyData Python SDK

Python SDK for ReadyData asset management with cross-language validation consistency.

## Installation

```bash
pip install readydata-sdk-py
```

## Usage

```python
from readydata import AssetClient, MemoryAdapter

# Create client with in-memory adapter
client = AssetClient(MemoryAdapter())

# Store an asset
await client.put('s3://bucket/asset.jpg', asset_data)

# Retrieve an asset  
asset = await client.get('s3://bucket/asset.jpg')

# List all assets
uris = await client.list()
```

## Features

- **Type Safety**: Pydantic models with full validation
- **Cross-Language**: Compatible with TypeScript SDK
- **Extensible**: Support for meta fields and structured extensions
- **Validation**: Registry-driven extension validation
- **Testing**: Comprehensive test suite with golden examples

## Asset Types

- **Image**: JPEG, PNG, WebP, SVG with dimensions and size limits
- **Document**: PDF, DOCX, TXT, HTML, MD with page counts and language detection  
- **Dataset**: CSV, JSON, Parquet, Arrow with row/column counts and schema information

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Type checking
mypy src/readydata/
```

Part of the ReadyData cross-language SDK foundation.