"""Adapter implementations for asset storage."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import Asset


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