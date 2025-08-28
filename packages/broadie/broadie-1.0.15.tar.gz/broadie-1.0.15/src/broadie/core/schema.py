"""
Schema validation and management for agent outputs.
Provides validation, normalization, and fallback handling for structured agent responses.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Default schema for agents without explicit output schemas
DEFAULT_PAYLOAD_SCHEMA = {
    "type": "object",
    "properties": {
        "raw_output": {"type": "string"}
    },
    "required": ["raw_output"]
}


class SchemaValidationError(Exception):
    """Raised when schema validation fails in strict mode."""
    pass


class SchemaManager:
    """Manages schema validation and normalization for agent outputs."""
    
    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initialize schema manager.
        
        Args:
            schema: JSON schema dict for validation, uses default if None
        """
        self.schema = schema or DEFAULT_PAYLOAD_SCHEMA
        self.schema_name = "user_payload" if schema else "default_payload"
        
        # Try to import jsonschema, gracefully handle if not available
        try:
            from jsonschema import validate, ValidationError
            self._validate_func = validate
            self._validation_error = ValidationError
            self._jsonschema_available = True
        except ImportError:
            logger.warning("jsonschema not available, validation will be skipped")
            self._jsonschema_available = False
    
    def validate(self, payload: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
        """
        Validate payload against schema.
        
        Args:
            payload: The payload to validate
            strict: Whether to raise on validation failure
            
        Returns:
            Validated payload or fallback structure
            
        Raises:
            SchemaValidationError: If validation fails and strict=True
        """
        if not self._jsonschema_available:
            # If jsonschema not available, return payload as-is
            logger.debug("Schema validation skipped (jsonschema not available)")
            return payload
            
        try:
            self._validate_func(instance=payload, schema=self.schema)
            logger.debug(f"Schema validation passed for {self.schema_name}")
            return payload
        except self._validation_error as e:
            error_msg = f"Schema validation failed: {str(e)}"
            logger.warning(error_msg)
            
            if strict:
                raise SchemaValidationError(error_msg) from e
            
            # Fallback to raw_output format
            fallback_payload = {"raw_output": json.dumps(payload) if isinstance(payload, dict) else str(payload)}
            logger.info("Using fallback payload due to validation failure")
            return fallback_payload
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the current schema."""
        return {
            "schema_name": self.schema_name,
            "schema": self.schema,
            "jsonschema_available": self._jsonschema_available
        }


def build_envelope(
    agent_name: str, 
    schema_name: str, 
    payload: Dict[str, Any], 
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build a universal envelope wrapping the validated payload.
    
    Args:
        agent_name: Name of the agent that produced the payload
        schema_name: Name/type of the schema used
        payload: The validated payload data
        metadata: Additional metadata about the response
        
    Returns:
        Universal envelope structure
    """
    envelope = {
        "agent": agent_name,
        "timestamp": datetime.utcnow().isoformat(),
        "schema": schema_name,
        "payload": payload,
        "metadata": metadata or {}
    }
    
    # Add default metadata if not provided
    if not envelope["metadata"]:
        envelope["metadata"] = {
            "should_send": True,
            "escalate_to_human": False,
            "tier_label": "INFORMATIONAL"
        }
    
    return envelope


def augment_instruction(base_instruction: str, schema: Optional[Dict[str, Any]] = None) -> str:
    """
    Augment agent instruction with schema directive.
    
    Args:
        base_instruction: Original agent instruction
        schema: JSON schema to include in instruction
        
    Returns:
        Augmented instruction with schema requirement
    """
    if not schema:
        return base_instruction
    
    schema_instruction = (
        f"{base_instruction}\n\n"
        "IMPORTANT: Return a single JSON object matching this JSON Schema:\n"
        f"{json.dumps(schema, indent=2)}\n"
        "Do not include prose or explanations. Output only valid JSON that matches the schema exactly."
    )
    
    return schema_instruction


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Extract JSON from agent response text.
    
    Args:
        response_text: Raw response text from agent
        
    Returns:
        Extracted JSON dict or fallback structure
    """
    try:
        # Try to parse the entire response as JSON
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        # Try to find JSON within the text
        try:
            # Look for JSON blocks
            start_markers = ['{', '[']
            end_markers = ['}', ']']
            
            for start_char, end_char in zip(start_markers, end_markers):
                start_idx = response_text.find(start_char)
                if start_idx != -1:
                    # Find matching closing bracket
                    bracket_count = 0
                    for i, char in enumerate(response_text[start_idx:], start_idx):
                        if char == start_char:
                            bracket_count += 1
                        elif char == end_char:
                            bracket_count -= 1
                            if bracket_count == 0:
                                json_str = response_text[start_idx:i+1]
                                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # If no valid JSON found, return fallback
        logger.debug("No valid JSON found in response, using fallback")
        return {"raw_output": response_text}