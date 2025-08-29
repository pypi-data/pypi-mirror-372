"""Operators module initialization."""

from .comparison import COMPARISON_OPERATORS
from .custom import (
    compile_operator,
    create_simple_operator,
    get_operator_handler,
    register_builtin_custom_operators,
    register_custom_operator,
)
from .logical import LOGICAL_OPERATORS

# Register built-in custom operators
register_builtin_custom_operators()

__all__ = [
    "LOGICAL_OPERATORS",
    "COMPARISON_OPERATORS",
    "register_custom_operator",
    "create_simple_operator",
    "register_builtin_custom_operators",
    "get_operator_handler",
    "compile_operator",
]
