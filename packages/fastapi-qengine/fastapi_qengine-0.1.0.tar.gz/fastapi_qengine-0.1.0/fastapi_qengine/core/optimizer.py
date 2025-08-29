"""
AST Optimizer for simplifying and optimizing filter ASTs.
"""

from typing import Dict, List, Optional

from .config import OptimizerConfig
from .types import ASTNode, FieldCondition, FilterAST, LogicalCondition, LogicalOperator, OrderNode


class ASTOptimizer:
    """Optimizes filter ASTs for better performance."""

    def __init__(self, config: Optional[OptimizerConfig] = None):
        self.config = config or OptimizerConfig()

    def optimize(self, ast: FilterAST) -> FilterAST:
        """
        Optimize a FilterAST.

        Args:
            ast: Input FilterAST

        Returns:
            Optimized FilterAST
        """
        if not self.config.enabled:
            return ast

        optimized_ast = FilterAST(
            where=ast.where,
            order=ast.order[:] if ast.order else [],  # Copy order nodes
            fields=ast.fields,
        )

        # Optimize where clause
        if optimized_ast.where is not None:
            for _ in range(self.config.max_optimization_passes):
                original = optimized_ast.where
                if optimized_ast.where is not None:
                    optimized_ast.where = self._optimize_node(optimized_ast.where)

                # Stop if no changes were made
                if self._nodes_equal(original, optimized_ast.where):
                    break

        # Optimize order (remove duplicates, etc.)
        if optimized_ast.order:
            optimized_ast.order = self._optimize_order_nodes(optimized_ast.order)

        return optimized_ast

    def _optimize_node(self, node: ASTNode) -> ASTNode:
        """Optimize a single AST node."""
        if isinstance(node, LogicalCondition):
            optimized = self._optimize_logical_condition(node)
            return optimized if optimized is not None else node
        elif isinstance(node, FieldCondition):
            return self._optimize_field_condition(node)
        else:
            return node

    def _optimize_logical_condition(self, node: LogicalCondition) -> ASTNode | None:
        """Optimize a logical condition node."""
        # First, recursively optimize nested conditions
        optimized_conditions = [self._optimize_node(condition) for condition in node.conditions]

        # Remove any null/empty conditions
        optimized_conditions = [c for c in optimized_conditions if c is not None]

        if not optimized_conditions:
            return None  # Empty logical condition

        if len(optimized_conditions) == 1:
            # Single condition in logical operator can be flattened
            return optimized_conditions[0]

        # Apply various optimizations based on configuration
        if self.config.simplify_logical_operators:
            optimized_conditions = self._simplify_logical_operators(node.operator, optimized_conditions)

        if self.config.combine_range_conditions:
            optimized_conditions = self._combine_range_conditions(optimized_conditions)

        if self.config.remove_redundant_conditions:
            optimized_conditions = self._remove_redundant_conditions(optimized_conditions)

        # Check if we still have multiple conditions
        if len(optimized_conditions) == 1:
            return optimized_conditions[0]
        elif len(optimized_conditions) == 0:
            return None

        return LogicalCondition(operator=node.operator, conditions=optimized_conditions)

    def _optimize_field_condition(self, node: FieldCondition) -> FieldCondition:
        """Optimize a field condition node."""
        # For now, just return as-is
        # Future optimizations could include:
        # - Converting ranges to more efficient operators
        # - Normalizing values
        return node

    def _simplify_logical_operators(self, operator: LogicalOperator, conditions: List[ASTNode]) -> List[ASTNode]:
        """Simplify nested logical operators of the same type."""
        simplified = []

        for condition in conditions:
            if isinstance(condition, LogicalCondition) and condition.operator == operator:
                # Flatten nested logical operators of same type
                # $and: [$and: [a, b], c] -> $and: [a, b, c]
                simplified.extend(condition.conditions)
            else:
                simplified.append(condition)

        return simplified

    def _combine_range_conditions(self, conditions: List[ASTNode]) -> List[ASTNode]:
        """Combine range conditions on the same field."""
        if not self.config.combine_range_conditions:
            return conditions

        # Group field conditions by field name
        field_conditions: Dict[str, List[FieldCondition]] = {}
        other_conditions = []

        for condition in conditions:
            if isinstance(condition, FieldCondition):
                if condition.field not in field_conditions:
                    field_conditions[condition.field] = []
                field_conditions[condition.field].append(condition)
            else:
                other_conditions.append(condition)

        # Combine range conditions for each field
        combined_conditions = []
        for field, field_conds in field_conditions.items():
            if len(field_conds) == 1:
                combined_conditions.append(field_conds[0])
            else:
                # Try to combine range conditions
                combined = self._try_combine_field_conditions(field_conds)
                combined_conditions.extend(combined)

        return combined_conditions + other_conditions

    def _try_combine_field_conditions(self, conditions: List[FieldCondition]) -> List[FieldCondition]:
        """Try to combine multiple conditions on the same field."""
        # For now, just return as-is
        # Future optimization could combine things like:
        # price >= 10 AND price <= 100 -> price: {$gte: 10, $lte: 100}
        return conditions

    def _remove_redundant_conditions(self, conditions: List[ASTNode]) -> List[ASTNode]:
        """Remove redundant conditions."""
        if not self.config.remove_redundant_conditions:
            return conditions

        # Remove exact duplicates
        seen = set()
        unique_conditions = []

        for condition in conditions:
            condition_key = self._get_condition_key(condition)
            if condition_key not in seen:
                seen.add(condition_key)
                unique_conditions.append(condition)

        return unique_conditions

    def _get_condition_key(self, condition: ASTNode) -> str:
        """Get a string key for a condition for deduplication."""
        if isinstance(condition, FieldCondition):
            return f"field:{condition.field}:{condition.operator.value}:{condition.value}"
        elif isinstance(condition, LogicalCondition):
            sub_keys = [self._get_condition_key(c) for c in condition.conditions]
            return f"logical:{condition.operator.value}:{','.join(sorted(sub_keys))}"
        else:
            return str(condition)

    def _optimize_order_nodes(self, order_nodes: List[OrderNode]) -> List[OrderNode]:
        """Optimize order nodes."""
        if not order_nodes:
            return []

        # Remove duplicate order fields (keep first occurrence)
        seen_fields = set()
        unique_order = []

        for order_node in order_nodes:
            if order_node.field not in seen_fields:
                seen_fields.add(order_node.field)
                unique_order.append(order_node)

        return unique_order

    def _nodes_equal(self, node1: Optional[ASTNode], node2: Optional[ASTNode]) -> bool:
        """Check if two nodes are equal."""
        if node1 is None and node2 is None:
            return True
        if node1 is None or node2 is None:
            return False

        if not isinstance(node1, type(node2)):
            return False

        if isinstance(node1, FieldCondition) and isinstance(node2, FieldCondition):
            return self._field_conditions_equal(node1, node2)

        elif isinstance(node1, LogicalCondition) and isinstance(node2, LogicalCondition):
            return self._logical_conditions_equal(node1, node2)

        return False

    def _field_conditions_equal(self, node1: FieldCondition, node2: FieldCondition) -> bool:
        """Check if two field conditions are equal."""
        return node1.field == node2.field and node1.operator == node2.operator and node1.value == node2.value

    def _logical_conditions_equal(self, node1: LogicalCondition, node2: LogicalCondition) -> bool:
        """Check if two logical conditions are equal."""
        if node1.operator != node2.operator:
            return False
        if len(node1.conditions) != len(node2.conditions):
            return False

        # Check if all conditions are equal (order-independent for commutative operators)
        if node1.operator in [LogicalOperator.AND, LogicalOperator.OR]:
            return self._commutative_conditions_equal(node1.conditions, node2.conditions)
        else:
            return self._ordered_conditions_equal(node1.conditions, node2.conditions)

    def _commutative_conditions_equal(self, conditions1: List[ASTNode], conditions2: List[ASTNode]) -> bool:
        """Check if two lists of conditions are equal for commutative operators."""
        keys1 = [self._get_condition_key(c) for c in conditions1]
        keys2 = [self._get_condition_key(c) for c in conditions2]
        return sorted(keys1) == sorted(keys2)

    def _ordered_conditions_equal(self, conditions1: List[ASTNode], conditions2: List[ASTNode]) -> bool:
        """Check if two lists of conditions are equal in order."""
        return all(self._nodes_equal(c1, c2) for c1, c2 in zip(conditions1, conditions2))
