"""Asset validation using Pydantic with registry-driven extension validation."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Union

from pydantic import ValidationError as PydanticValidationError

from .models import Asset, ImageAsset, DocumentAsset, DatasetAsset


class ValidationError(Exception):
    """Custom validation error with detailed error information."""
    
    def __init__(self, message: str, errors: List[Dict[str, Any]]):
        super().__init__(message)
        self.errors = errors


class AssetValidator:
    """Validator for Asset objects with registry-driven extension validation."""
    
    def __init__(self, registry_path: str = None):
        """Initialize validator with registry data."""
        if registry_path is None:
            registry_path = Path(__file__).parent.parent.parent.parent / "contracts" / "registry-data.json"
        
        with open(registry_path) as f:
            self.registry_data = json.load(f)
    
    def validate(self, data: Dict[str, Any]) -> Asset:
        """Validate asset data and return typed Asset instance."""
        try:
            # First validate with Pydantic based on kind
            kind = data.get('kind')
            
            if kind == 'image':
                asset = ImageAsset.model_validate(data)
            elif kind == 'document':
                asset = DocumentAsset.model_validate(data)
            elif kind == 'dataset':
                asset = DatasetAsset.model_validate(data)
            else:
                raise ValidationError(
                    f"Invalid asset kind: {kind}",
                    [{"message": f"Asset kind '{kind}' is not supported"}]
                )
            
            # Additional registry-driven validations
            self._validate_extensions(asset)
            self._validate_meta(asset)
            
            return asset
            
        except PydanticValidationError as e:
            errors = [{"message": err["msg"], "field": err["loc"]} for err in e.errors()]
            raise ValidationError("Asset validation failed", errors)
    
    def _validate_extensions(self, asset: Asset) -> None:
        """Validate extensions against the registry."""
        if not asset.extensions:
            return
        
        for extension_key, extension_data in asset.extensions.items():
            # Check if extension is registered or experimental
            is_experimental = extension_key.startswith('exp:')
            registry_section = (
                self.registry_data.get('experimental', {}) if is_experimental 
                else self.registry_data.get('extensions', {})
            )
            
            if extension_key not in registry_section:
                raise ValidationError(
                    f"Unknown extension: {extension_key}",
                    [{"message": f"Extension '{extension_key}' is not registered"}]
                )
            
            # Validate extension key format
            key_pattern = (
                r'^exp:[a-z][a-z0-9-]*@[1-9]\d*$' if is_experimental
                else r'^[a-z][a-z0-9-]*@[1-9]\d*$'
            )
            
            if not re.match(key_pattern, extension_key):
                raise ValidationError(
                    f"Invalid extension key format: {extension_key}",
                    [{"message": f"Extension key '{extension_key}' does not match required pattern"}]
                )
    
    def _validate_meta(self, asset: Asset) -> None:
        """Validate meta field keys and values."""
        if not asset.meta:
            return
        
        for meta_key, meta_value in asset.meta.items():
            # Validate key pattern
            key_pattern = r'^[a-z0-9]+:[a-zA-Z0-9_.-]+$'
            if not re.match(key_pattern, meta_key):
                raise ValidationError(
                    f"Invalid meta key format: {meta_key}",
                    [{"message": f"Meta key '{meta_key}' must follow pattern 'namespace:key'"}]
                )
            
            # Validate value type and size
            if isinstance(meta_value, str) and len(meta_value) > 4096:
                raise ValidationError(
                    f"Meta value too long for key: {meta_key}",
                    [{"message": f"Meta value for '{meta_key}' exceeds 4096 characters"}]
                )
    
    def get_error_messages(self, errors: List[Dict[str, Any]]) -> List[str]:
        """Get validation errors as formatted strings."""
        messages = []
        for err in errors:
            field = err.get('field', 'unknown')
            message = err.get('message', 'Unknown error')
            messages.append(f"{field}: {message}")
        return messages


# Export a default validator instance
asset_validator = AssetValidator()