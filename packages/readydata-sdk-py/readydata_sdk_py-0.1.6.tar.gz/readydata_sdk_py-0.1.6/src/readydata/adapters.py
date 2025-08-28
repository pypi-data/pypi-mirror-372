"""Adapter implementations for asset storage."""

import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

from .models import Asset

# GCS imports - only import if available
try:
    from google.cloud import storage
    import google.auth
    from dotenv import load_dotenv
    
    load_dotenv()
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False


class Adapter(ABC):
    """Abstract base class for asset storage adapters."""
    
    @abstractmethod
    async def get(self, uri: str) -> Optional[Asset]:
        """Get an asset by URI."""
        pass
    
    @abstractmethod
    async def put(self, uri: str, asset: Asset) -> None:
        """Put an asset at the given URI."""
        pass
    
    @abstractmethod
    async def list(self) -> List[str]:
        """List all asset URIs."""
        pass
    
    @abstractmethod
    async def get_blob(self, uri: str) -> Optional[bytes]:
        """Get blob data by URI."""
        pass
    
    @abstractmethod
    async def put_blob(self, uri: str, data: bytes) -> None:
        """Put blob data at the given URI."""
        pass


class MemoryAdapter(Adapter):
    """In-memory adapter for local development and testing."""
    
    def __init__(self):
        self._assets: Dict[str, Dict[str, Any]] = {}
        self._blobs: Dict[str, bytes] = {}
    
    async def get(self, uri: str) -> Optional[Asset]:
        """Get an asset by URI."""
        asset_data = self._assets.get(uri)
        if not asset_data:
            return None
        
        # Import here to avoid circular imports
        from .validation import asset_validator
        return asset_validator.validate(asset_data)
    
    async def put(self, uri: str, asset: Asset) -> None:
        """Put an asset at the given URI."""
        # Convert Pydantic model to dict for storage
        self._assets[uri] = asset.model_dump(by_alias=True)
    
    async def list(self) -> List[str]:
        """List all asset URIs."""
        return list(self._assets.keys())
    
    async def get_blob(self, uri: str) -> Optional[bytes]:
        """Get blob data by URI."""
        return self._blobs.get(uri)
    
    async def put_blob(self, uri: str, data: bytes) -> None:
        """Put blob data at the given URI."""
        self._blobs[uri] = data
    
    def clear(self) -> None:
        """Clear all stored data (useful for testing)."""
        self._assets.clear()
        self._blobs.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored data."""
        total_blob_size = sum(len(blob) for blob in self._blobs.values())
        return {
            "asset_count": len(self._assets),
            "blob_count": len(self._blobs),
            "total_blob_size": total_blob_size,
        }


class GCPBucketAdapter(Adapter):
    """Google Cloud Storage bucket adapter for asset storage."""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """Initialize GCP Bucket adapter.
        
        Args:
            bucket_name: GCS bucket name. If None, uses GCS_BUCKET_NAME env var.
        """
        if not GCS_AVAILABLE:
            raise ImportError(
                "GCS dependencies not available. Install with: pip install google-cloud-storage python-dotenv"
            )
        
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError(
                "Bucket name must be provided either as parameter or GCS_BUCKET_NAME env var"
            )
        
        # Initialize GCS client using your existing pattern
        try:
            credentials, project = google.auth.default()
            self.storage_client = storage.Client(credentials=credentials, project=project)
            # Validate bucket access
            self.bucket = self.storage_client.get_bucket(self.bucket_name)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GCS client or access bucket '{self.bucket_name}': {e}")
    
    async def get(self, uri: str) -> Optional[Asset]:
        """Get an asset by URI."""
        try:
            # Asset metadata stored as companion .meta.json file
            meta_blob_name = f"{uri}.meta.json"
            blob = self.bucket.blob(meta_blob_name)
            
            if not blob.exists():
                return None
            
            # Download metadata
            metadata_bytes = await asyncio.to_thread(blob.download_as_bytes)
            metadata_dict = json.loads(metadata_bytes.decode('utf-8'))
            
            # Import here to avoid circular imports
            from .validation import asset_validator
            return asset_validator.validate(metadata_dict)
            
        except Exception:
            # For Phase 1, simple error handling - just return None
            return None
    
    async def put(self, uri: str, asset: Asset) -> None:
        """Put an asset at the given URI."""
        try:
            # Store asset metadata as companion .meta.json file
            meta_blob_name = f"{uri}.meta.json"
            blob = self.bucket.blob(meta_blob_name)
            
            # Convert asset to JSON using Pydantic's JSON serialization
            asset_json = asset.model_dump_json(by_alias=True, indent=2)
            
            # Upload metadata
            await asyncio.to_thread(
                blob.upload_from_string, 
                asset_json, 
                content_type="application/json"
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to store asset {uri}: {e}")
    
    async def list(self) -> List[str]:
        """List all asset URIs."""
        try:
            # List all .meta.json files and extract URIs
            blobs = await asyncio.to_thread(self.storage_client.list_blobs, self.bucket_name)
            
            uris = []
            for blob in blobs:
                if blob.name.endswith('.meta.json'):
                    # Remove .meta.json suffix to get original URI
                    uri = blob.name[:-10]  # len('.meta.json') = 10
                    uris.append(uri)
            
            return uris
            
        except Exception as e:
            raise RuntimeError(f"Failed to list assets: {e}")
    
    async def get_blob(self, uri: str) -> Optional[bytes]:
        """Get blob data by URI."""
        try:
            blob = self.bucket.blob(uri)
            
            if not blob.exists():
                return None
            
            return await asyncio.to_thread(blob.download_as_bytes)
            
        except Exception:
            # For Phase 1, simple error handling
            return None
    
    async def put_blob(self, uri: str, data: bytes) -> None:
        """Put blob data at the given URI."""
        try:
            blob = self.bucket.blob(uri)
            await asyncio.to_thread(blob.upload_from_string, data)
            
        except Exception as e:
            raise RuntimeError(f"Failed to store blob {uri}: {e}")