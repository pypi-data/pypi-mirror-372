"""Basic tests for Python SDK."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from readydata.models import ImageAsset, DocumentAsset, DatasetAsset
from datetime import datetime


class TestBasicModels:
    """Basic tests for Pydantic models."""
    
    def test_image_asset_creation(self):
        """Test creating an ImageAsset."""
        data = {
            "schema": "asset",
            "version": "1.0.0",
            "id": "test_image_123",
            "kind": "image",
            "createdAt": "2024-01-15T10:30:00Z",
            "contentUri": "s3://test/image.jpg",
            "format": "jpeg",
            "width": 100,
            "height": 100,
            "size": 1000,
            "mime": "image/jpeg"
        }
        
        asset = ImageAsset.model_validate(data)
        assert asset.kind == "image"
        assert asset.format == "jpeg"
        assert asset.width == 100
        assert asset.height == 100
    
    def test_document_asset_creation(self):
        """Test creating a DocumentAsset."""
        data = {
            "schema": "asset", 
            "version": "1.0.0",
            "id": "test_doc_456",
            "kind": "document",
            "createdAt": "2024-01-15T10:30:00Z",
            "contentUri": "s3://test/document.pdf",
            "format": "pdf",
            "size": 5000,
            "mime": "application/pdf"
        }
        
        asset = DocumentAsset.model_validate(data)
        assert asset.kind == "document"
        assert asset.format == "pdf"
        assert asset.size == 5000
    
    def test_dataset_asset_creation(self):
        """Test creating a DatasetAsset."""
        data = {
            "schema": "asset",
            "version": "1.0.0", 
            "id": "test_data_789",
            "kind": "dataset",
            "createdAt": "2024-01-15T10:30:00Z",
            "contentUri": "s3://test/data.csv",
            "format": "csv",
            "rows": 1000,
            "columns": 5,
            "size": 10000,
            "mime": "text/csv"
        }
        
        asset = DatasetAsset.model_validate(data)
        assert asset.kind == "dataset"
        assert asset.format == "csv"
        assert asset.rows == 1000
        assert asset.columns == 5