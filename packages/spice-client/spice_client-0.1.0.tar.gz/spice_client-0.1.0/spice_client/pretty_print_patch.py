# coding: utf-8

"""
Monkey patch to add pretty printing to all SPICE client models.
Import this module to automatically enhance all model string representations.

Usage:
    import spice_client.pretty_print_patch
    # All models will now have pretty printing enabled
"""

from datetime import datetime
from typing import Any
import json


def _pretty_str(self) -> str:
    """Returns a clean, readable string representation."""
    return _format_model(self)


def _pretty_repr(self) -> str:
    """Returns a detailed string representation for debugging."""
    return f"{self.__class__.__name__}(\n{_format_model(self, indent=2)})"


def _format_model(obj, indent: int = 0) -> str:
    """Format the model for display with proper indentation and readability."""
    try:
        data = obj.model_dump(exclude_unset=True, exclude_none=True)
        return _format_dict(data, indent)
    except Exception:
        # Fallback to original representation if something goes wrong
        return object.__str__(obj)


def _format_dict(obj: Any, indent: int = 0) -> str:
    """Recursively format dictionary-like objects with proper indentation."""
    spacing = "  " * indent
    next_spacing = "  " * (indent + 1)
    
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        
        # Sort keys for consistent output, but put 'name' and 'id' first if they exist
        keys = list(obj.keys())
        priority_keys = ['name', 'id']
        sorted_keys = []
        
        # Add priority keys first
        for key in priority_keys:
            if key in keys:
                sorted_keys.append(key)
                keys.remove(key)
        
        # Add remaining keys
        sorted_keys.extend(sorted(keys))
        
        items = []
        for key in sorted_keys:
            value = obj[key]
            formatted_value = _format_value(value, indent + 1)
            items.append(f"{next_spacing}{key}: {formatted_value}")
        
        if indent == 0:
            return "{\n" + ",\n".join(items) + "\n}"
        else:
            return "{\n" + ",\n".join(items) + f"\n{spacing}}}"
            
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        
        if len(obj) == 1:
            return f"[{_format_value(obj[0], indent)}]"
        elif len(obj) <= 3:
            # Show first few items inline for short lists
            items = [_format_value(item, 0) for item in obj]
            return f"[{', '.join(items)}]"
        else:
            # Show count for long lists
            return f"[{len(obj)} items: {_format_value(obj[0], 0)}, ...]"
    
    else:
        return _format_value(obj, indent)


def _format_value(value: Any, indent: int = 0) -> str:
    """Format individual values with appropriate representation."""
    if isinstance(value, str):
        # Truncate very long strings
        if len(value) > 100:
            return f'"{value[:100]}..."'
        else:
            return f'"{value}"'
    
    elif isinstance(value, datetime):
        return f'"{value.strftime("%Y-%m-%d %H:%M:%S")}"'
    
    elif isinstance(value, dict):
        return _format_dict(value, indent)
    
    elif isinstance(value, list):
        return _format_dict(value, indent)
    
    elif value is None:
        return "null"
    
    elif isinstance(value, (int, float, bool)):
        return str(value)
    
    else:
        return f'"{str(value)}"'


def pretty_json(self, indent: int = 2) -> str:
    """Return a pretty-printed JSON representation."""
    try:
        data = self.model_dump(exclude_unset=True, exclude_none=True, mode='json')
        return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
    except Exception:
        return str(self)


# Apply the monkey patch to all imported models
def apply_pretty_printing():
    """Apply pretty printing to all SPICE client models."""
    import spice_client.models
    from pydantic import BaseModel
    
    # Get all model classes from the models module
    model_classes = []
    for attr_name in dir(spice_client.models):
        attr = getattr(spice_client.models, attr_name)
        if (isinstance(attr, type) and 
            issubclass(attr, BaseModel) and 
            attr != BaseModel):
            model_classes.append(attr)
    
    # Apply pretty printing to each model class
    for model_class in model_classes:
        model_class.__str__ = _pretty_str
        model_class.__repr__ = _pretty_repr
        model_class.pretty_json = pretty_json


# Automatically apply when this module is imported
apply_pretty_printing()