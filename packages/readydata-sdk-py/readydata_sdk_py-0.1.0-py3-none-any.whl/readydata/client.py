"""Asset client for managing assets with validation."""

from datetime import datetime
from typing import Dict, List, Optional, Any, TypeVar, Union

from .models import Asset, ImageAsset, DocumentAsset, DatasetAsset
from .validation import asset_validator, ValidationError
from .adapters import Adapter

AssetType = TypeVar('AssetType', bound=Asset)


class AssetClient:
    """Client for managing assets with validation and storage."""
    
    def __init__(self, adapter: Adapter):
        self.adapter = adapter
    
    async def get(self, uri: str) -> Optional[Asset]:
        """Get an asset by URI with validation."""
        asset = await self.adapter.get(uri)
        return asset  # Validation happens in the adapter
    
    async def put(self, uri: str, asset: Asset) -> None:
        """Put an asset with validation."""
        # Validation happens during Asset model creation in the adapter
        await self.adapter.put(uri, asset)
    
    async def list(self) -> List[str]:
        """List all asset URIs."""
        return await self.adapter.list()
    
    async def get_blob(self, uri: str) -> Optional[bytes]:
        """Get blob data for an asset."""
        return await self.adapter.get_blob(uri)
    
    async def put_blob(self, uri: str, data: bytes) -> None:
        """Put blob data for an asset."""
        await self.adapter.put_blob(uri, data)
    
    async def create(self, asset_data: Dict[str, Any]) -> Asset:
        """Create a new asset with generated timestamps."""
        now = datetime.utcnow()
        
        # Add timestamps
        asset_data = {
            **asset_data,
            'createdAt': now.isoformat() + 'Z',
            'updatedAt': now.isoformat() + 'Z',
        }
        
        # Validate and create the asset
        asset = asset_validator.validate(asset_data)
        
        # Store the asset
        await self.put(asset_data['contentUri'], asset)
        return asset
    
    async def update(self, uri: str, updates: Dict[str, Any]) -> Optional[Asset]:
        """Update an existing asset."""
        existing = await self.get(uri)
        if not existing:
            return None
        
        # Convert existing asset to dict and apply updates
        existing_data = existing.model_dump(by_alias=True)
        updated_data = {
            **existing_data,
            **updates,
            'updatedAt': datetime.utcnow().isoformat() + 'Z',
        }
        
        # Validate updated asset
        updated_asset = asset_validator.validate(updated_data)
        
        # Store the updated asset
        await self.put(uri, updated_asset)
        return updated_asset