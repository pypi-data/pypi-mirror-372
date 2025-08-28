"""Adapter implementations for asset storage."""

import os
import json
import asyncio
import hashlib
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .models import Asset, ImageAsset, DocumentAsset, DatasetAsset

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
    
    async def list_all_objects(self) -> Dict[str, List[str]]:
        """List all objects in bucket, categorized by type."""
        try:
            blobs = await asyncio.to_thread(self.storage_client.list_blobs, self.bucket_name)
            
            content_files = []
            metadata_files = []
            
            for blob in blobs:
                if blob.name.endswith('.meta.json'):
                    metadata_files.append(blob.name)
                else:
                    content_files.append(blob.name)
            
            return {
                'content': content_files,
                'metadata': metadata_files
            }
            
        except Exception as e:
            raise RuntimeError(f"Failed to list all objects: {e}")
    
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
    
    # Enhanced API methods
    
    def _generate_id(self, path: str) -> str:
        """Generate a unique asset ID based on path and timestamp."""
        # Clean path: remove extension and special chars, keep structure
        clean_path = path.replace('/', '_').replace('.', '_').lower()
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Add short UUID for collision avoidance
        short_uuid = str(uuid.uuid4())[:8]
        return f"{clean_path}_{timestamp}_{short_uuid}"
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate SHA256 checksum of data."""
        return hashlib.sha256(data).hexdigest()
    
    def _analyze_image(self, image_bytes: bytes) -> tuple[int, int, str]:
        """Analyze image to extract width, height, and format.
        
        This is a simple implementation. For production, consider using PIL/Pillow.
        """
        # Simple PNG detection
        if image_bytes.startswith(b'\x89PNG'):
            # For PNG, width/height are at bytes 16-23 (big endian)
            if len(image_bytes) >= 24:
                width = int.from_bytes(image_bytes[16:20], byteorder='big')
                height = int.from_bytes(image_bytes[20:24], byteorder='big')
                return width, height, 'png'
            return 100, 100, 'png'  # Default if can't read
        
        # Simple JPEG detection
        elif image_bytes.startswith(b'\xff\xd8\xff'):
            # For JPEG, this is more complex. For demo, return defaults
            return 100, 100, 'jpeg'
        
        # Default fallback
        return 100, 100, 'unknown'
    
    def _detect_document_info(self, doc_bytes: bytes, format: str) -> Dict[str, Any]:
        """Detect document information like page count."""
        info = {}
        
        if format == 'pdf' and doc_bytes.startswith(b'%PDF'):
            # Simple PDF page counting (not robust, but works for basic PDFs)
            try:
                content = doc_bytes.decode('latin1', errors='ignore')
                page_count = content.count('/Type /Page')
                if page_count > 0:
                    info['pages'] = page_count
                else:
                    info['pages'] = 1  # Default
            except:
                info['pages'] = 1
        
        return info
    
    async def put_asset_with_content(
        self, 
        path: str, 
        content: bytes, 
        asset_type: str,
        **metadata_overrides
    ) -> Asset:
        """Store file content and metadata in a single operation.
        
        Args:
            path: GCS path for the file (e.g., 'images/products/hero.jpg')
            content: File content as bytes
            asset_type: Type of asset ('image', 'document', 'dataset')
            **metadata_overrides: Override any generated metadata
            
        Returns:
            Created Asset instance
        """
        try:
            # Generate core metadata automatically
            asset_id = metadata_overrides.pop('id', self._generate_id(path))
            
            asset_data = {
                "schema": "asset",
                "version": "1.0.0",
                "id": asset_id,
                "kind": asset_type,
                "createdAt": datetime.now().isoformat(),
                "contentUri": f"gs://{self.bucket_name}/{path}",
                "size": len(content),
                "checksum": f"sha256:{self._calculate_checksum(content)}",
                **metadata_overrides
            }
            
            # Store file content
            await self.put_blob(path, content)
            
            # Store metadata co-located with content
            meta_path = f"{path}.meta.json"
            meta_json = json.dumps(asset_data, indent=2, default=str)
            await self.put_blob(meta_path, meta_json.encode('utf-8'))
            
            # Return proper asset type
            from .validation import asset_validator
            return asset_validator.validate(asset_data)
            
        except Exception as e:
            raise RuntimeError(f"Failed to store asset with content at {path}: {e}")
    
    async def create_image_asset(
        self,
        image_bytes: bytes,
        path: str,
        tags: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
        **overrides
    ) -> ImageAsset:
        """Create an image asset with auto-detected properties.
        
        Args:
            image_bytes: Image file content
            path: GCS path (e.g., 'images/products/hero.jpg')
            tags: List of tags for the asset
            meta: Metadata dictionary
            **overrides: Override any auto-detected properties
            
        Returns:
            Created ImageAsset
        """
        # Auto-detect image properties
        width, height, format = self._analyze_image(image_bytes)
        
        # Determine MIME type
        mime_map = {
            'png': 'image/png',
            'jpeg': 'image/jpeg', 
            'jpg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml'
        }
        mime = mime_map.get(format.lower(), f'image/{format}')
        
        asset_data = {
            "format": format,
            "width": width,
            "height": height,
            "mime": mime,
            "tags": tags or [],
            "meta": meta or {},
            "status": "ready",
            **overrides
        }
        
        asset = await self.put_asset_with_content(path, image_bytes, "image", **asset_data)
        return asset
    
    async def create_document_asset(
        self,
        doc_bytes: bytes,
        path: str,
        format: str,
        language: str = "en-US",
        tags: Optional[List[str]] = None,
        meta: Optional[Dict[str, Any]] = None,
        **overrides
    ) -> DocumentAsset:
        """Create a document asset with auto-detected properties.
        
        Args:
            doc_bytes: Document file content
            path: GCS path (e.g., 'documents/manuals/guide.pdf')
            format: Document format ('pdf', 'docx', 'txt', etc.)
            language: Document language (BCP-47 tag)
            tags: List of tags for the asset
            meta: Metadata dictionary
            **overrides: Override any auto-detected properties
            
        Returns:
            Created DocumentAsset
        """
        # Auto-detect document properties
        doc_info = self._detect_document_info(doc_bytes, format)
        
        # Determine MIME type
        mime_map = {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'html': 'text/html',
            'md': 'text/markdown'
        }
        mime = mime_map.get(format.lower(), f'application/{format}')
        
        asset_data = {
            "format": format,
            "language": language,
            "mime": mime,
            "tags": tags or [],
            "meta": meta or {},
            "status": "ready",
            **doc_info,  # Include detected info (like page count)
            **overrides
        }
        
        asset = await self.put_asset_with_content(path, doc_bytes, "document", **asset_data)
        return asset
    
    async def get_asset_with_content(self, asset_id: str) -> Optional[tuple[Asset, bytes]]:
        """Retrieve both asset metadata and file content.
        
        Returns:
            Tuple of (Asset, file_content_bytes) or None if not found
        """
        # Get asset metadata
        asset = await self.get(asset_id)
        if not asset:
            return None
        
        # Extract path from contentUri
        if asset.content_uri and asset.content_uri.startswith(f"gs://{self.bucket_name}/"):
            path = asset.content_uri[len(f"gs://{self.bucket_name}/"):]
            content = await self.get_blob(path)
            if content:
                return asset, content
        
        return None