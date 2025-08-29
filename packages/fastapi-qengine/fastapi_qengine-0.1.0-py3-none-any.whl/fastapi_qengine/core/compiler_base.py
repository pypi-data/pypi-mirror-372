"""
Base compiler class and interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from .errors import CompilerError
from .types import ASTNode, FieldCondition, FieldsNode, FilterAST, LogicalCondition, OrderNode, QueryCompiler


class BaseQueryCompiler(QueryCompiler):
    """Base class for all query compilers implementing Template Method pattern."""

    def __init__(self, backend_name: str):
        self.backend_name = backend_name

    def compile(self, ast: FilterAST) -> Any:
        """
        Template method for compiling FilterAST to backend query.

        Args:
            ast: FilterAST to compile

        Returns:
            Backend-specific query object
        """
        try:
            query = self.create_base_query()

            if ast.where is not None:
                query = self.apply_where(query, ast.where)

            if ast.order:
                query = self.apply_order(query, ast.order)

            if ast.fields is not None:
                query = self.apply_fields(query, ast.fields)

            return self.finalize_query(query)

        except Exception as e:
            raise CompilerError(f"Failed to compile AST: {e}", backend=self.backend_name)

    @abstractmethod
    def create_base_query(self) -> Any:
        """Create the base query object for this backend."""
        pass

    @abstractmethod
    def apply_where(self, query: Any, where_node: ASTNode) -> Any:
        """Apply where conditions to the query."""
        pass

    @abstractmethod
    def apply_order(self, query: Any, order_nodes: List[OrderNode]) -> Any:
        """Apply ordering to the query."""
        pass

    @abstractmethod
    def apply_fields(self, query: Any, fields_node: FieldsNode) -> Any:
        """Apply field projection to the query."""
        pass

    def finalize_query(self, query: Any) -> Any:
        """Finalize the query before returning (default: return as-is)."""
        return query

    def supports_backend(self, backend_type: str) -> bool:
        """Check if this compiler supports the given backend."""
        return backend_type == self.backend_name

    # Helper methods for common operations

    def compile_condition(self, condition: ASTNode) -> Any:
        """Compile a condition node to backend-specific format."""
        if isinstance(condition, FieldCondition):
            return self.compile_field_condition(condition)
        elif isinstance(condition, LogicalCondition):
            return self.compile_logical_condition(condition)
        else:
            raise CompilerError(f"Unknown condition type: {type(condition)}")

    @abstractmethod
    def compile_field_condition(self, condition: FieldCondition) -> Any:
        """Compile a field condition to backend-specific format."""
        pass

    @abstractmethod
    def compile_logical_condition(self, condition: LogicalCondition) -> Any:
        """Compile a logical condition to backend-specific format."""
        pass


class QueryAdapter(ABC):
    """Adapter interface for different query object types."""

    @abstractmethod
    def add_where_condition(self, condition: Any) -> "QueryAdapter":
        """Add a where condition to the query."""
        pass

    @abstractmethod
    def add_sort(self, field: str, ascending: bool = True) -> "QueryAdapter":
        """Add sorting to the query."""
        pass

    @abstractmethod
    def set_projection(self, fields: Dict[str, int]) -> "QueryAdapter":
        """Set field projection."""
        pass

    @abstractmethod
    def build(self) -> Any:
        """Build the final query object."""
        pass
