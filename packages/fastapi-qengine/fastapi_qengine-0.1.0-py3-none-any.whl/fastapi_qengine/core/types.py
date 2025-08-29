"""
Type definitions for fastapi-qengine.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, TypeAlias, TypeVar, Union

# Basic type aliases
FilterValue: TypeAlias = Union[str, int, float, bool, List[Any], Dict[str, Any]]
FilterDict: TypeAlias = Dict[str, Any]
OrderSpec: TypeAlias = str
FieldsSpec: TypeAlias = Dict[str, int]


T = TypeVar("T")


class FilterFormat(Enum):
    """Supported filter input formats."""

    NESTED_PARAMS = "nested_params"
    JSON_STRING = "json_string"
    DICT_OBJECT = "dict_object"


class LogicalOperator(Enum):
    """Logical operators for combining conditions."""

    AND = "$and"
    OR = "$or"
    NOR = "$nor"


class ComparisonOperator(Enum):
    """Comparison operators for field conditions."""

    EQ = "$eq"  # Equal
    NE = "$ne"  # Not equal
    GT = "$gt"  # Greater than
    GTE = "$gte"  # Greater than or equal
    LT = "$lt"  # Less than
    LTE = "$lte"  # Less than or equal
    IN = "$in"  # In array
    NIN = "$nin"  # Not in array
    REGEX = "$regex"  # Regular expression
    EXISTS = "$exists"  # Field exists
    SIZE = "$size"  # Array size
    TYPE = "$type"  # Field type


@dataclass
class FilterInput:
    """Raw filter input from the request."""

    where: Optional[FilterDict] = None
    order: Optional[OrderSpec] = None
    fields: Optional[FieldsSpec] = None
    format: FilterFormat = FilterFormat.DICT_OBJECT


@dataclass
class ASTNode:
    """Base class for AST nodes."""

    pass


@dataclass
class FieldCondition(ASTNode):
    """A condition on a specific field."""

    field: str
    operator: ComparisonOperator
    value: FilterValue


@dataclass
class LogicalCondition(ASTNode):
    """A logical combination of conditions."""

    operator: LogicalOperator
    conditions: List[ASTNode]


@dataclass
class OrderNode(ASTNode):
    """Represents ordering specification."""

    field: str
    ascending: bool = True


@dataclass
class FieldsNode(ASTNode):
    """Represents field projection."""

    fields: Dict[str, int]


@dataclass
class FilterAST:
    """Complete filter Abstract Syntax Tree."""

    where: Optional[ASTNode] = None
    order: List[OrderNode] | None = None
    fields: Optional[FieldsNode] = None

    def __post_init__(self):
        if self.order is None:
            self.order = []


class BackendQuery(Protocol):
    """Protocol for backend-specific query objects."""

    def apply_where(self, condition: ASTNode) -> "BackendQuery":
        """Apply where conditions to the query."""
        ...

    def apply_order(self, order_nodes: List[OrderNode]) -> "BackendQuery":
        """Apply ordering to the query."""
        ...

    def apply_fields(self, fields_node: FieldsNode) -> "BackendQuery":
        """Apply field projection to the query."""
        ...


class QueryCompiler(ABC):
    """Abstract base class for query compilers."""

    @abstractmethod
    def compile(self, ast: FilterAST) -> Any:
        """Compile AST to backend-specific query."""
        pass

    @abstractmethod
    def supports_backend(self, backend_type: str) -> bool:
        """Check if this compiler supports the given backend."""
        pass


class ValidationRule(Protocol):
    """Protocol for validation rules."""

    def validate(self, node: ASTNode) -> List[str]:
        """Validate a node and return list of error messages."""
        ...


@dataclass
class SecurityPolicy:
    """Security policy for query execution."""

    max_depth: int = 10
    allowed_operators: Optional[List[ComparisonOperator]] = None
    allowed_fields: Optional[List[str]] = None
    blocked_fields: Optional[List[str]] = None
    max_array_size: int = 1000
