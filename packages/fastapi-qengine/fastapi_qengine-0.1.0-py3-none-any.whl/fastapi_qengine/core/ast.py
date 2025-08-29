"""
AST Builder for converting normalized filter inputs to typed AST nodes.
"""

from typing import Any, Dict, List

from .errors import ParseError
from .types import (
    ASTNode,
    ComparisonOperator,
    FieldCondition,
    FieldsNode,
    FilterAST,
    FilterInput,
    LogicalCondition,
    LogicalOperator,
    OrderNode,
)


class ASTBuilder:
    """Builds typed AST from normalized filter inputs."""

    def build(self, filter_input: FilterInput) -> FilterAST:
        """
        Build a FilterAST from a normalized FilterInput.

        Args:
            filter_input: Normalized FilterInput

        Returns:
            FilterAST with typed nodes
        """
        where_node = None
        order_nodes = []
        fields_node = None

        # Build where AST
        if filter_input.where is not None:
            where_node = self._build_where_node(filter_input.where)

        # Build order nodes
        if filter_input.order is not None:
            order_nodes = self._build_order_nodes(filter_input.order)

        # Build fields node
        if filter_input.fields is not None:
            fields_node = self._build_fields_node(filter_input.fields)

        return FilterAST(where=where_node, order=order_nodes, fields=fields_node)

    def _build_where_node(self, where: Dict[str, Any]) -> ASTNode:
        """Build where clause AST node."""
        if not isinstance(where, dict):
            raise ParseError("Where clause must be a dictionary")

        return self._build_condition_node(where)

    def _build_condition_node(self, condition: Dict[str, Any]) -> ASTNode:
        """Build a condition node (field condition or logical condition)."""
        logical_operators = []
        field_conditions = []

        for key, value in condition.items():
            if key.startswith("$") and key in ["$and", "$or", "$nor"]:
                # Logical operator
                logical_op = LogicalOperator(key)
                if not isinstance(value, list):
                    raise ParseError(f"Logical operator '{key}' requires a list value")

                nested_conditions = [self._build_condition_node(item) for item in value]
                logical_operators.append(LogicalCondition(operator=logical_op, conditions=nested_conditions))
            else:
                # Field condition
                field_conditions.append(self._build_field_condition(key, value))

        # Combine all conditions
        all_conditions = logical_operators + field_conditions

        if len(all_conditions) == 1:
            return all_conditions[0]
        elif len(all_conditions) > 1:
            # Multiple conditions at same level - combine with AND
            return LogicalCondition(operator=LogicalOperator.AND, conditions=all_conditions)
        else:
            raise ParseError("Empty condition")

    def _build_field_condition(self, field: str, condition: Any) -> ASTNode:
        """Build a field condition node."""
        if field.startswith("$"):
            raise ParseError(f"Invalid field name '{field}' - cannot start with '$'")

        if isinstance(condition, dict):
            return self._build_complex_field_condition(field, condition)
        else:
            return self._build_simple_field_condition(field, condition)

    def _build_complex_field_condition(self, field: str, condition: Dict[str, Any]) -> ASTNode:
        """Build a complex field condition with operators."""
        if len(condition) == 1:
            return self._build_single_operator_condition(field, condition)
        else:
            return self._build_multiple_operator_condition(field, condition)

    def _build_single_operator_condition(self, field: str, condition: Dict[str, Any]) -> FieldCondition:
        """Build a field condition with a single operator."""
        op_key, op_value = next(iter(condition.items()))
        self._validate_operator(op_key)
        operator = self._get_comparison_operator(op_key)
        return FieldCondition(field=field, operator=operator, value=op_value)

    def _build_multiple_operator_condition(self, field: str, condition: Dict[str, Any]) -> ASTNode:
        """Build a field condition with multiple operators combined with AND."""
        conditions = []
        for op_key, op_value in condition.items():
            self._validate_operator(op_key)
            operator = self._get_comparison_operator(op_key)
            conditions.append(FieldCondition(field=field, operator=operator, value=op_value))

        if len(conditions) == 1:
            return conditions[0]
        else:
            return LogicalCondition(operator=LogicalOperator.AND, conditions=conditions)

    def _build_simple_field_condition(self, field: str, condition: Any) -> FieldCondition:
        """Build a simple equality field condition."""
        return FieldCondition(field=field, operator=ComparisonOperator.EQ, value=condition)

    def _validate_operator(self, op_key: str) -> None:
        """Validate that an operator key is valid."""
        if not op_key.startswith("$"):
            raise ParseError(f"Invalid operator '{op_key}' - must start with '$'")

    def _get_comparison_operator(self, op_key: str) -> ComparisonOperator:
        """Get a ComparisonOperator from an operator key."""
        try:
            return ComparisonOperator(op_key)
        except ValueError:
            raise ParseError(f"Unknown operator '{op_key}'")

    def _build_order_nodes(self, order: str) -> List[OrderNode]:
        """Build order nodes from order specification."""
        if not isinstance(order, str):
            raise ParseError("Order must be a string")

        order_nodes = []

        # Split by comma for multiple fields
        for field_spec in order.split(","):
            field_spec = field_spec.strip()
            if not field_spec:
                continue

            # Check for descending order (- prefix)
            ascending = True
            if field_spec.startswith("-"):
                ascending = False
                field_spec = field_spec[1:]

            if not field_spec:
                raise ParseError("Invalid order specification - empty field name")

            order_nodes.append(OrderNode(field=field_spec, ascending=ascending))

        return order_nodes

    def _build_fields_node(self, fields: Dict[str, int]) -> FieldsNode:
        """Build fields node from fields specification."""
        if not isinstance(fields, dict):
            raise ParseError("Fields must be a dictionary")

        # Validate field values are 0 or 1
        for field, include in fields.items():
            if include not in [0, 1]:
                raise ParseError(f"Field '{field}' inclusion value must be 0 or 1, got {include}")

        return FieldsNode(fields=fields)

    def _flatten_single_item_logical(self, node: ASTNode) -> ASTNode:
        """Flatten single-item logical conditions."""
        if isinstance(node, LogicalCondition) and len(node.conditions) == 1:
            # Single item in logical condition can be flattened
            return self._flatten_single_item_logical(node.conditions[0])
        return node
