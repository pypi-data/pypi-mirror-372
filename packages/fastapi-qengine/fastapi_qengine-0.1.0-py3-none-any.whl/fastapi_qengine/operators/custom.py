"""
Custom operators and operator utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

from ..core.registry import operator_registry


class CustomOperatorHandler(ABC):
    """Base class for custom operator handlers."""

    @abstractmethod
    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile custom operator."""
        pass

    @property
    @abstractmethod
    def supported_backends(self) -> list:
        """List of supported backends."""
        pass


def register_custom_operator(name: str, handler: CustomOperatorHandler) -> None:
    """
    Register a custom operator.

    Args:
        name: Operator name (must start with $)
        handler: Operator handler instance
    """
    operator_registry.register_operator(name=name, implementation=handler, backends=handler.supported_backends)


def create_simple_operator(name: str, mongo_impl: Callable[[str, Any], Dict], backends: list | None = None) -> None:
    """
    Create and register a simple custom operator.

    Args:
        name: Operator name
        mongo_impl: Function that takes (field, value) and returns MongoDB query dict
        backends: Supported backends (defaults to ['beanie', 'pymongo'])
    """
    if backends is None:
        backends = ["beanie", "pymongo"]

    class SimpleOperatorHandler(CustomOperatorHandler):
        def compile(self, field: str, value: Any, backend: str) -> Any:
            if backend in ["beanie", "pymongo"]:
                return mongo_impl(field, value)
            else:
                raise NotImplementedError(f"{name} not implemented for backend: {backend}")

        @property
        def supported_backends(self) -> list:
            return backends

    register_custom_operator(name, SimpleOperatorHandler())


# Example custom operators


def register_builtin_custom_operators():
    """Register built-in custom operators."""

    # $text operator for text search
    create_simple_operator("$text", lambda field, value: {"$text": {"$search": value}}, ["beanie", "pymongo"])

    # $geoWithin operator for geospatial queries
    create_simple_operator("$geoWithin", lambda field, value: {field: {"$geoWithin": value}}, ["beanie", "pymongo"])

    # $near operator for proximity queries
    create_simple_operator("$near", lambda field, value: {field: {"$near": value}}, ["beanie", "pymongo"])


# Operator utility functions


def get_operator_handler(operator_name: str, backend: str | None = None) -> Any:
    """Get handler for an operator."""
    from ..core.types import ComparisonOperator, LogicalOperator
    from .comparison import COMPARISON_OPERATORS
    from .logical import LOGICAL_OPERATORS

    # Try comparison operators first
    try:
        comp_op = ComparisonOperator(operator_name)
        return COMPARISON_OPERATORS[comp_op]
    except ValueError:
        pass

    # Try logical operators
    try:
        logic_op = LogicalOperator(operator_name)
        return LOGICAL_OPERATORS[logic_op]
    except ValueError:
        pass

    # Try custom operators
    if operator_registry.is_registered(operator_name, backend):
        return operator_registry.get_operator(operator_name, backend)

    raise ValueError(f"Unknown operator: {operator_name}")


def compile_operator(operator_name: str, field: str, value: Any, backend: str) -> Any:
    """Compile an operator to backend-specific format."""
    handler = get_operator_handler(operator_name, backend)

    if hasattr(handler, "compile"):
        if operator_name in ["$and", "$or", "$nor"]:
            # Logical operators don't use field parameter
            return handler.compile(value, backend)
        else:
            # Comparison operators use field parameter
            return handler.compile(field, value, backend)
    else:
        raise ValueError(f"Operator handler for '{operator_name}' doesn't have compile method")
