"""Golden tests for Python SDK."""

import json
import pytest
from pathlib import Path

from readydata.validation import asset_validator, ValidationError
from readydata.client import AssetClient
from readydata.adapters import MemoryAdapter


class TestGoldenTests:
    """Test suite for golden examples validation."""
    
    @pytest.fixture
    def client(self):
        """Create a client with memory adapter."""
        adapter = MemoryAdapter()
        return AssetClient(adapter)
    
    @pytest.fixture
    def examples_dir(self):
        """Get the examples directory path."""
        return Path(__file__).parent.parent.parent / "examples"
    
    def test_valid_image_jpeg(self, examples_dir, client):
        """Test validation of valid JPEG image asset."""
        file_path = examples_dir / "valid" / "image-jpeg.json"
        with open(file_path) as f:
            data = json.load(f)
        
        # Should validate without error
        asset = asset_validator.validate(data)
        assert asset.kind == "image"
        assert asset.format == "jpeg"
    
    def test_valid_image_svg(self, examples_dir, client):
        """Test validation of valid SVG image asset."""
        file_path = examples_dir / "valid" / "image-svg.json"
        with open(file_path) as f:
            data = json.load(f)
        
        asset = asset_validator.validate(data)
        assert asset.kind == "image"
        assert asset.format == "svg"
        # SVG may not have width/height
    
    def test_valid_document_pdf(self, examples_dir, client):
        """Test validation of valid PDF document asset."""
        file_path = examples_dir / "valid" / "document-pdf.json"
        with open(file_path) as f:
            data = json.load(f)
        
        asset = asset_validator.validate(data)
        assert asset.kind == "document"
        assert asset.format == "pdf"
    
    def test_valid_dataset_csv(self, examples_dir, client):
        """Test validation of valid CSV dataset asset."""
        file_path = examples_dir / "valid" / "dataset-csv.json"
        with open(file_path) as f:
            data = json.load(f)
        
        asset = asset_validator.validate(data)
        assert asset.kind == "dataset"
        assert asset.format == "csv"
    
    @pytest.mark.asyncio
    async def test_roundtrip_through_client(self, examples_dir, client):
        """Test storing and retrieving assets through the client."""
        file_path = examples_dir / "valid" / "image-jpeg.json"
        with open(file_path) as f:
            original_data = json.load(f)
        
        # Validate original
        original_asset = asset_validator.validate(original_data)
        
        # Store through client
        uri = original_asset.content_uri
        await client.put(uri, original_asset)
        
        # Retrieve through client
        retrieved = await client.get(uri)
        assert retrieved is not None
        assert retrieved.id == original_asset.id
        assert retrieved.kind == original_asset.kind
    
    def test_invalid_missing_required_fields(self, examples_dir):
        """Test rejection of asset with missing required fields."""
        file_path = examples_dir / "invalid" / "missing-required-fields.json"
        with open(file_path) as f:
            data = json.load(f)
        
        with pytest.raises(ValidationError):
            asset_validator.validate(data)
    
    def test_invalid_semver(self, examples_dir):
        """Test rejection of invalid semver version."""
        file_path = examples_dir / "invalid" / "invalid-semver.json"
        with open(file_path) as f:
            data = json.load(f)
        
        with pytest.raises(ValidationError):
            asset_validator.validate(data)
    
    def test_invalid_meta_keys(self, examples_dir):
        """Test rejection of invalid meta keys."""
        file_path = examples_dir / "invalid" / "invalid-meta-keys.json"
        with open(file_path) as f:
            data = json.load(f)
        
        with pytest.raises(ValidationError):
            asset_validator.validate(data)
    
    def test_invalid_extension_keys(self, examples_dir):
        """Test rejection of invalid extension keys."""
        file_path = examples_dir / "invalid" / "invalid-extension-keys.json"
        with open(file_path) as f:
            data = json.load(f)
        
        with pytest.raises(ValidationError):
            asset_validator.validate(data)
    
    def test_valid_meta_fields(self):
        """Test acceptance of valid meta field formats."""
        valid_data = {
            "schema": "asset",
            "version": "1.0.0",
            "id": "test12345",
            "kind": "image",
            "createdAt": "2024-01-15T10:30:00Z",
            "contentUri": "s3://test/image.jpg",
            "format": "jpeg",
            "width": 100,
            "height": 100,
            "size": 1000,
            "mime": "image/jpeg",
            "meta": {
                "seo:title": "Test Title",
                "camera:make": "Canon",
                "ml:confidence": 0.95,
                "system:processed": True,
                "backup:archived": None
            },
            "extensions": {}
        }
        
        # Should validate without error
        asset = asset_validator.validate(valid_data)
        assert asset.meta["seo:title"] == "Test Title"
    
    def test_registered_extensions(self):
        """Test acceptance of registered extensions."""
        valid_data = {
            "schema": "asset",
            "version": "1.0.0",
            "id": "test12345",
            "kind": "image",
            "createdAt": "2024-01-15T10:30:00Z",
            "contentUri": "s3://test/image.jpg",
            "format": "jpeg",
            "width": 100,
            "height": 100,
            "size": 1000,
            "mime": "image/jpeg",
            "meta": {},
            "extensions": {
                "renditions@1": {
                    "thumbnail": {"width": 200, "height": 150, "uri": "s3://test/thumb.jpg"}
                }
            }
        }
        
        asset = asset_validator.validate(valid_data)
        assert "renditions@1" in asset.extensions
    
    def test_experimental_extensions(self):
        """Test acceptance of experimental extensions."""
        valid_data = {
            "schema": "asset",
            "version": "1.0.0",
            "id": "test12345",
            "kind": "image",
            "createdAt": "2024-01-15T10:30:00Z",
            "contentUri": "s3://test/image.jpg",
            "format": "jpeg",
            "width": 100,
            "height": 100,
            "size": 1000,
            "mime": "image/jpeg",
            "meta": {},
            "extensions": {
                "exp:ml-analysis@1": {
                    "confidence": 0.95,
                    "categories": ["nature", "landscape"]
                }
            }
        }
        
        asset = asset_validator.validate(valid_data)
        assert "exp:ml-analysis@1" in asset.extensions