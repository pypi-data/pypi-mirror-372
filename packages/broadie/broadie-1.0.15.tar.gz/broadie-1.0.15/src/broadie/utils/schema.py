"""
Schema validation utilities.
"""

from typing import Any, Dict

from .exceptions import ValidationError


def validate_config_schema(config: Dict[str, Any], schema_type: str = "agent") -> bool:
    """Validate configuration against schema."""
    required_fields = {
        "agent": ["name", "description"],
        "sub_agent": ["name", "prompt"],
    }

    if schema_type not in required_fields:
        raise ValidationError(f"Unknown schema type: {schema_type}")

    for field in required_fields[schema_type]:
        if field not in config:
            raise ValidationError(f"Missing required field: {field}")

    return True


class SchemaValidator:
    """Basic schema validator."""

    @staticmethod
    def validate(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        return True  # Simplified for now
