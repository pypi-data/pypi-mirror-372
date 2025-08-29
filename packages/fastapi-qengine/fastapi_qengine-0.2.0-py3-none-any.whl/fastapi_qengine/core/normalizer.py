"""
Normalizer for filter inputs to canonical format.
"""

from typing import Any, Dict

from .errors import ValidationError
from .types import FieldsSpec, FilterDict, FilterInput, OrderSpec


class FilterNormalizer:
    """Normalizes filter inputs to a canonical format."""

    def normalize(self, filter_input: FilterInput) -> FilterInput:
        """
        Normalize a FilterInput to canonical format.

        Args:
            filter_input: Raw FilterInput from parser

        Returns:
            Normalized FilterInput with canonical structure
        """
        normalized_where = None
        normalized_order = None
        normalized_fields = None

        # Normalize where clause
        if filter_input.where is not None:
            normalized_where = self._normalize_where(filter_input.where)

        # Normalize order clause
        if filter_input.order is not None:
            normalized_order = self._normalize_order(filter_input.order)

        # Normalize fields clause
        if filter_input.fields is not None:
            normalized_fields = self._normalize_fields(filter_input.fields)

        return FilterInput(
            where=normalized_where, order=normalized_order, fields=normalized_fields, format=filter_input.format
        )

    def _normalize_where(self, where: FilterDict) -> FilterDict:
        """Normalize where conditions to canonical format."""
        if not isinstance(where, dict):
            raise ValidationError("'where' clause must be an object")

        return self._normalize_condition(where)

    def _normalize_condition(self, condition: Any) -> Any:
        """Recursively normalize a condition."""
        if not isinstance(condition, dict):
            return condition

        normalized = {}

        for key, value in condition.items():
            if key.startswith("$"):
                # Logical operator or comparison operator
                normalized[key] = self._normalize_operator_value(key, value)
            else:
                # Field condition
                normalized[key] = self._normalize_field_condition(value)

        return normalized

    def _normalize_operator_value(self, operator: str, value: Any) -> Any:
        """Normalize operator value."""
        if operator in ["$and", "$or", "$nor"]:
            # Logical operators expect arrays
            if not isinstance(value, list):
                raise ValidationError(f"Operator '{operator}' requires an array value")
            return [self._normalize_condition(item) for item in value]
        else:
            # Comparison operators
            return value

    def _normalize_field_condition(self, condition: Any) -> Any:
        """Normalize a field condition."""
        if not isinstance(condition, dict):
            # Simple equality: field: value -> field: {$eq: value}
            return {"$eq": condition}

        # Complex condition with operators
        normalized = {}
        for op, value in condition.items():
            if not op.startswith("$"):
                raise ValidationError(f"Invalid operator '{op}'. Operators must start with '$'")
            normalized[op] = value

        return normalized

    def _normalize_order(self, order: OrderSpec) -> str:
        """Normalize order specification."""
        if not isinstance(order, str):
            raise ValidationError("'order' clause must be a string")

        # Basic validation - just return as-is for now
        # More sophisticated normalization could handle multiple fields, etc.
        return order.strip()

    def _normalize_fields(self, fields: FieldsSpec) -> Dict[str, int]:
        """Normalize fields specification."""
        if not isinstance(fields, dict):
            raise ValidationError("'fields' clause must be an object")

        normalized = {}
        for field, include in fields.items():
            if not isinstance(field, str):
                raise ValidationError("Field names must be strings")

            # Normalize include value to 0 or 1
            if isinstance(include, bool):
                normalized[field] = 1 if include else 0
            elif isinstance(include, (int, float)):
                normalized[field] = 1 if include else 0
            else:
                raise ValidationError(f"Field inclusion value must be boolean or number, got {type(include)}")

        return normalized

    def _simplify_logical_operators(self, condition: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify redundant logical operators."""
        if not isinstance(condition, dict):
            return condition

        simplified = {}

        for key, value in condition.items():
            if key in ["$and", "$or"]:
                simplified.update(self._process_logical_operator(key, value))
            else:
                simplified[key] = self._process_regular_field(value)

        return simplified

    def _process_logical_operator(self, operator: str, value: Any) -> Dict[str, Any]:
        """Process logical operators ($and, $or) and simplify them."""
        if not isinstance(value, list):
            return {operator: value}

        simplified_items = [self._simplify_logical_operators(item) for item in value]
        return self._handle_simplified_logical_items(operator, simplified_items)

    def _handle_simplified_logical_items(self, operator: str, items: list) -> Dict[str, Any]:
        """Handle simplified logical operator items."""
        if len(items) == 1:
            return self._merge_single_logical_item(items[0])
        return {operator: items}

    def _merge_single_logical_item(self, item: Any) -> Dict[str, Any]:
        """Merge single logical operator item into parent."""
        if isinstance(item, dict):
            return item
        return {}

    def _process_regular_field(self, value: Any) -> Any:
        """Process regular field values."""
        if isinstance(value, dict):
            return self._simplify_logical_operators(value)
        return value
