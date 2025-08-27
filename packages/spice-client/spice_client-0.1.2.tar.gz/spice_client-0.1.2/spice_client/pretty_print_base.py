# coding: utf-8

"""
Pretty printing mixin for SPICE client models.
Provides clean, readable string representations for all model objects.
"""

from datetime import datetime
from typing import Any
from pydantic import BaseModel
import json


class PrettyPrintMixin(BaseModel):
    """Mixin to add pretty printing capabilities to Pydantic models."""
    
    def __str__(self) -> str:
        """Returns a clean, readable string representation."""
        return self._format_model()
    
    def __repr__(self) -> str:
        """Returns a detailed string representation for debugging."""
        return f"{self.__class__.__name__}({self._format_model(compact=True)})"
    
    def _format_model(self, compact: bool = False) -> str:
        """Format the model for display with proper indentation and readability."""
        data = self.model_dump(exclude_unset=True, exclude_none=True)
        return self._format_dict(data, indent=0, compact=compact)
    
    def _format_dict(self, obj: Any, indent: int = 0, compact: bool = False) -> str:
        """Recursively format dictionary-like objects with proper indentation."""
        if compact and indent > 0:
            # For compact mode (repr), only show first level
            return "{...}"
        
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            
            items = []
            for key, value in obj.items():
                formatted_value = self._format_value(value, indent + 2, compact)
                if compact:
                    items.append(f"{key}={formatted_value}")
                else:
                    items.append(f"{'  ' * (indent + 1)}{key}: {formatted_value}")
            
            if compact:
                return ", ".join(items)
            else:
                return "{\n" + ",\n".join(items) + f"\n{'  ' * indent}}}"
                
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            
            if compact:
                return f"[{len(obj)} items]"
            
            items = []
            for item in obj:
                formatted_item = self._format_value(item, indent + 2, compact)
                items.append(f"{'  ' * (indent + 1)}{formatted_item}")
            
            return "[\n" + ",\n".join(items) + f"\n{'  ' * indent}]"
        
        else:
            return self._format_value(obj, indent, compact)
    
    def _format_value(self, value: Any, indent: int = 0, compact: bool = False) -> str:
        """Format individual values with appropriate representation."""
        if isinstance(value, str):
            # Truncate long strings for readability
            if len(value) > 50 and not compact:
                return f'"{value[:50]}..."'
            else:
                return f'"{value}"'
        
        elif isinstance(value, datetime):
            return f'"{value.strftime("%Y-%m-%d %H:%M:%S")}"'
        
        elif isinstance(value, dict):
            return self._format_dict(value, indent, compact)
        
        elif isinstance(value, list):
            return self._format_dict(value, indent, compact)
        
        elif value is None:
            return "null"
        
        else:
            return str(value)
    
    def pretty_json(self, indent: int = 2) -> str:
        """Return a pretty-printed JSON representation."""
        data = self.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)