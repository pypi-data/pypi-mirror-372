"""Generated Pydantic models for ReadyData assets."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class AssetRef(BaseModel):
    """Reference to another resource."""
    
    model_config = ConfigDict(extra='forbid')
    
    role: str = Field(..., pattern=r'^[a-z][a-z0-9._-]{0,63}$', description="Short, namespaced-ish role")
    uri: str = Field(..., description="URI of the referenced resource")


class TableField(BaseModel):
    """Dataset table field definition."""
    
    model_config = ConfigDict(extra='forbid')
    
    name: str
    type: str
    nullable: Optional[bool] = None


class TableSchema(BaseModel):
    """Dataset schema information."""
    
    model_config = ConfigDict(extra='forbid')
    
    fields: Optional[List[TableField]] = None


class AssetBase(BaseModel):
    """Base asset model with common fields."""
    
    model_config = ConfigDict(extra='forbid')
    
    schema: Literal['asset'] = Field(..., description="Schema identifier")
    version: str = Field(
        ...,
        pattern=r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$',
        description="Schema version in semver format"
    )
    id: str = Field(
        ...,
        pattern=r'^[A-Za-z0-9_-]{8,64}$',
        description="Stable opaque identifier for the asset"
    )
    created_at: datetime = Field(..., alias='createdAt', description="When the asset was created")
    updated_at: Optional[datetime] = Field(None, alias='updatedAt', description="When the asset was last updated")
    created_by: Optional[str] = Field(None, alias='createdBy', description="User who created the asset")
    updated_by: Optional[str] = Field(None, alias='updatedBy', description="User who last updated the asset")
    tags: List[str] = Field(default_factory=list, description="Tags for search and categorization")
    status: Literal['pending', 'ready', 'failed'] = Field(default='pending', description="Processing status")
    checksum: Optional[str] = Field(
        None,
        pattern=r'^(?:sha256:[A-Fa-f0-9]{64}|md5:[A-Fa-f0-9]{32})$',
        description="Integrity checksum"
    )
    content_uri: str = Field(..., alias='contentUri', description="Primary blob location")
    refs: List[AssetRef] = Field(default_factory=list, description="Additional references")
    meta: Dict[str, Union[str, float, bool, None]] = Field(
        default_factory=dict, 
        description="Freeform metadata with namespaced keys"
    )
    extensions: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Structured extensions with module-versioned keys"
    )


class ImageAsset(AssetBase):
    """Image asset with format-specific properties."""
    
    kind: Literal['image'] = Field(..., description="Asset type discriminator")
    format: Literal['jpeg', 'png', 'webp', 'svg'] = Field(..., description="Image format")
    width: Optional[int] = Field(None, ge=1, description="Image width in pixels")
    height: Optional[int] = Field(None, ge=1, description="Image height in pixels")
    size: int = Field(..., ge=0, le=104857600, description="File size in bytes (max 100MB)")
    mime: str = Field(..., pattern=r'^[a-z]+/[a-z0-9][a-z0-9.+!#$&\-\^_]*$', description="IANA MIME type")


class DocumentAsset(AssetBase):
    """Document asset with document-specific properties."""
    
    kind: Literal['document'] = Field(..., description="Asset type discriminator")
    format: Literal['pdf', 'docx', 'txt', 'html', 'md'] = Field(..., description="Document format")
    pages: Optional[int] = Field(None, ge=1, description="Number of pages")
    size: int = Field(..., ge=0, le=209715200, description="File size in bytes (max 200MB)")
    language: Optional[str] = Field(None, description="BCP-47 language tag")
    mime: str = Field(..., pattern=r'^[a-z]+/[a-z0-9][a-z0-9.+!#$&\-\^_]*$', description="IANA MIME type")


class DatasetAsset(AssetBase):
    """Dataset asset with data-specific properties."""
    
    kind: Literal['dataset'] = Field(..., description="Asset type discriminator")
    format: Literal['csv', 'json', 'parquet', 'arrow'] = Field(..., description="Dataset format")
    rows: int = Field(..., ge=0, description="Number of rows")
    columns: int = Field(..., ge=0, description="Number of columns")
    size: int = Field(..., ge=0, le=5368709120, description="File size in bytes (max 5GB)")
    table_schema: Optional[TableSchema] = Field(None, alias='tableSchema', description="Dataset schema information")
    mime: str = Field(..., pattern=r'^[a-z]+/[a-z0-9][a-z0-9.+!#$&\-\^_]*$', description="IANA MIME type")


# Union type for all asset variants
Asset = Union[ImageAsset, DocumentAsset, DatasetAsset]