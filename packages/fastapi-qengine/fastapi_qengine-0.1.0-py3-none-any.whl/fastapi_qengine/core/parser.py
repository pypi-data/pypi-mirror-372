"""
Parser for filter inputs in different formats.
"""

import json
import urllib.parse
from typing import Any, Dict, Optional, Union

from .config import ParserConfig
from .errors import ParseError
from .types import FilterFormat, FilterInput


class FilterParser:
    """Parses filter inputs from various formats."""

    def __init__(self, config: Optional[ParserConfig] = None):
        self.config = config or ParserConfig()

    def parse(self, filter_input: Union[str, Dict[str, Any]]) -> FilterInput:
        """
        Parse filter input and return a normalized FilterInput object.

        Args:
            filter_input: Can be a JSON string, dict, or nested params dict

        Returns:
            FilterInput object with normalized data
        """
        if isinstance(filter_input, str):
            return self._parse_json_string(filter_input)
        elif isinstance(filter_input, dict):
            return self._parse_dict_input(filter_input)
        else:
            raise ParseError(f"Unsupported filter input type: {type(filter_input)}")

    def _parse_json_string(self, json_str: str) -> FilterInput:
        """Parse a JSON string filter."""
        try:
            # URL decode if needed
            if "%" in json_str:
                json_str = urllib.parse.unquote(json_str)

            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise ParseError("Filter JSON must be an object")

            return FilterInput(
                where=data.get("where"),
                order=data.get("order"),
                fields=data.get("fields"),
                format=FilterFormat.JSON_STRING,
            )
        except json.JSONDecodeError as e:
            raise ParseError(f"Invalid JSON in filter: {e}", source=json_str, position=e.pos)

    def _parse_dict_input(self, data: Dict[str, Any]) -> FilterInput:
        """Parse a dictionary input (could be nested params or direct dict)."""
        # Check if this looks like nested params (has 'filter' key with nested structure)
        if self._is_nested_params_format(data):
            return self._parse_nested_params(data)
        else:
            # Assume it's a direct filter dict
            return FilterInput(
                where=data.get("where"),
                order=data.get("order"),
                fields=data.get("fields"),
                format=FilterFormat.DICT_OBJECT,
            )

    def _is_nested_params_format(self, data: Dict[str, Any]) -> bool:
        """Check if the data looks like nested params format."""
        # Look for patterns like filter[where][field] or similar nested structures
        for key in data.keys():
            if isinstance(key, str) and "[" in key and "]" in key:
                return True
        return False

    def _parse_nested_params(self, data: Dict[str, Any]) -> FilterInput:
        """Parse nested parameters format like filter[where][field]=value."""
        filter_data = {}

        for key, value in data.items():
            if not isinstance(key, str):
                continue

            # Parse nested key like "filter[where][price][$gt]"
            parts = self._parse_nested_key(key)
            if not parts:
                continue

            # Build nested structure
            current = filter_data
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the final value
            final_key = parts[-1]
            current[final_key] = self._convert_value(value)

        # Extract the filter components
        filter_root = filter_data.get("filter", {})

        return FilterInput(
            where=filter_root.get("where"),
            order=filter_root.get("order"),
            fields=filter_root.get("fields"),
            format=FilterFormat.NESTED_PARAMS,
        )

    def _parse_nested_key(self, key: str) -> list:
        """
        Parse a nested key like 'filter[where][price][$gt]' into parts.

        Returns:
            List of key parts like ['filter', 'where', 'price', '$gt']
        """
        parts = []
        current = ""

        for char in key:
            if char in ["[", "]"]:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char

        if current:
            parts.append(current)

        return parts

    def _convert_value(self, value: Any) -> Any:
        """Convert string values to appropriate types."""
        if not isinstance(value, str):
            return value

        # Try to convert to appropriate type
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.lower() == "null":
            return None

        # Try numeric conversion
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Try JSON parsing for arrays/objects
        if value.startswith("[") or value.startswith("{"):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass

        return value

    def validate_depth(self, data: Dict[str, Any], current_depth: int = 0) -> None:
        """Validate nesting depth doesn't exceed configuration limits."""
        if current_depth > self.config.max_nesting_depth:
            raise ParseError(f"Filter nesting depth exceeds maximum of {self.config.max_nesting_depth}")

        if isinstance(data, dict):
            for value in data.values():
                self.validate_depth(value, current_depth + 1)
        elif isinstance(data, list):
            for item in data:
                self.validate_depth(item, current_depth + 1)
