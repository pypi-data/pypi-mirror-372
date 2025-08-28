"""Tests for GCP Bucket Adapter."""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import json
import pytest
from unittest.mock import Mock, patch

from readydata.adapters import GCPBucketAdapter
from readydata.validation import asset_validator


class TestGCPBucketAdapter:
    """Test suite for GCP Bucket Adapter."""
    
    def test_import_error_handling(self):
        """Test graceful handling when GCS dependencies are not available."""
        with patch('readydata.adapters.GCS_AVAILABLE', False):
            with pytest.raises(ImportError) as exc_info:
                GCPBucketAdapter()
            
            assert "GCS dependencies not available" in str(exc_info.value)
    
    def test_missing_bucket_name(self):
        """Test error when bucket name is not provided."""
        with patch('readydata.adapters.GCS_AVAILABLE', True), \
             patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                GCPBucketAdapter()
            
            assert "Bucket name must be provided" in str(exc_info.value)
    
    @patch('readydata.adapters.GCS_AVAILABLE', True)
    @patch('readydata.adapters.google.auth.default')
    @patch('readydata.adapters.storage.Client')
    def test_successful_initialization(self, mock_client_class, mock_auth):
        """Test successful adapter initialization."""
        # Mock authentication
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "test-project")
        
        # Mock GCS client and bucket
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.get_bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Initialize adapter
        adapter = GCPBucketAdapter("test-bucket")
        
        # Verify initialization
        assert adapter.bucket_name == "test-bucket"
        assert adapter.storage_client == mock_client
        assert adapter.bucket == mock_bucket
        mock_client.get_bucket.assert_called_once_with("test-bucket")
    
    @patch('readydata.adapters.GCS_AVAILABLE', True)
    @patch('readydata.adapters.google.auth.default')
    @patch('readydata.adapters.storage.Client')
    @pytest.mark.asyncio
    async def test_put_and_get_asset(self, mock_client_class, mock_auth):
        """Test storing and retrieving an asset."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "test-project")
        
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_client.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Mock blob operations
        mock_blob.upload_from_string = Mock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes = Mock(return_value=b'{"test": "data"}')
        
        # Create adapter
        adapter = GCPBucketAdapter("test-bucket")
        
        # Create a test asset
        asset_data = {
            "schema": "asset",
            "version": "1.0.0",
            "id": "test12345",  # Valid ID: 8-64 chars
            "kind": "image",
            "createdAt": "2024-01-15T10:30:00Z",
            "contentUri": "s3://test/image.jpg",
            "format": "jpeg",
            "width": 100,
            "height": 100,
            "size": 1000,
            "mime": "image/jpeg"
        }
        asset = asset_validator.validate(asset_data)
        
        # Mock asyncio.to_thread to execute the upload directly
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.side_effect = lambda func, *args, **kwargs: func(*args, **kwargs)
            
            # Test put operation
            await adapter.put("test/image.jpg", asset)
            
            # Verify blob was created with correct name
            mock_bucket.blob.assert_called_with("test/image.jpg.meta.json")
            
            # Verify upload was called
            mock_blob.upload_from_string.assert_called_once()
            call_args = mock_blob.upload_from_string.call_args
            uploaded_data = call_args[0][0]
            
            # Verify uploaded data is valid JSON containing asset data
            uploaded_json = json.loads(uploaded_data)
            assert uploaded_json["id"] == "test12345"
            assert uploaded_json["kind"] == "image"
    
    @patch('readydata.adapters.GCS_AVAILABLE', True)
    @patch('readydata.adapters.google.auth.default')
    @patch('readydata.adapters.storage.Client')
    @pytest.mark.asyncio
    async def test_get_nonexistent_asset(self, mock_client_class, mock_auth):
        """Test retrieving a non-existent asset returns None."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "test-project")
        
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_client.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Mock blob doesn't exist
        mock_blob.exists.return_value = False
        
        # Create adapter
        adapter = GCPBucketAdapter("test-bucket")
        
        # Test get operation
        result = await adapter.get("nonexistent/file.jpg")
        
        # Should return None for non-existent asset
        assert result is None
    
    @patch('readydata.adapters.GCS_AVAILABLE', True)
    @patch('readydata.adapters.google.auth.default')
    @patch('readydata.adapters.storage.Client')
    @pytest.mark.asyncio
    async def test_list_assets(self, mock_client_class, mock_auth):
        """Test listing assets."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "test-project")
        
        mock_client = Mock()
        mock_bucket = Mock()
        
        mock_client.get_bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Mock blobs with proper name attribute
        mock_blob1 = Mock()
        mock_blob1.name = "file1.jpg.meta.json"
        mock_blob2 = Mock()
        mock_blob2.name = "file2.png.meta.json"
        mock_blob3 = Mock()
        mock_blob3.name = "folder/file3.pdf.meta.json"
        mock_blob4 = Mock()
        mock_blob4.name = "regular-file.jpg"  # Should be ignored
        
        mock_blobs = [mock_blob1, mock_blob2, mock_blob3, mock_blob4]
        
        # Create adapter
        adapter = GCPBucketAdapter("test-bucket")
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_blobs
            
            # Test list operation
            uris = await adapter.list()
            
            # Should only return URIs from .meta.json files
            expected_uris = ["file1.jpg", "file2.png", "folder/file3.pdf"]
            assert set(uris) == set(expected_uris)
    
    @patch('readydata.adapters.GCS_AVAILABLE', True)
    @patch('readydata.adapters.google.auth.default')
    @patch('readydata.adapters.storage.Client')
    @pytest.mark.asyncio
    async def test_blob_operations(self, mock_client_class, mock_auth):
        """Test blob put and get operations."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "test-project")
        
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_client.get_bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_client_class.return_value = mock_client
        
        # Mock blob operations
        mock_blob.exists.return_value = True
        mock_blob.upload_from_string = Mock()
        test_data = b"test binary data"
        mock_blob.download_as_bytes = Mock(return_value=test_data)
        
        # Create adapter
        adapter = GCPBucketAdapter("test-bucket")
        
        with patch('asyncio.to_thread') as mock_to_thread:
            # Mock async operations
            mock_to_thread.side_effect = [None, test_data]  # put, then get
            
            # Test put_blob
            await adapter.put_blob("test/file.jpg", test_data)
            mock_bucket.blob.assert_called_with("test/file.jpg")
            
            # Test get_blob  
            result = await adapter.get_blob("test/file.jpg")
            assert result == test_data
    
    @patch('readydata.adapters.GCS_AVAILABLE', True)
    @patch('readydata.adapters.google.auth.default')
    @patch('readydata.adapters.storage.Client')
    def test_env_var_bucket_name(self, mock_client_class, mock_auth):
        """Test using bucket name from environment variable."""
        # Setup mocks
        mock_credentials = Mock()
        mock_auth.return_value = (mock_credentials, "test-project")
        
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.get_bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        # Test with environment variable
        with patch.dict('os.environ', {'GCS_BUCKET_NAME': 'env-bucket'}):
            adapter = GCPBucketAdapter()
            assert adapter.bucket_name == "env-bucket"