"""Core module initialization."""

from .ast import ASTBuilder
from .compiler_base import BaseQueryCompiler, QueryAdapter
from .config import (
    CacheConfig,
    OptimizerConfig,
    ParserConfig,
    QEngineConfig,
    ValidatorConfig,
    default_config,
)
from .errors import (
    CompilerError,
    OptimizationError,
    ParseError,
    QEngineError,
    RegistryError,
    SecurityError,
    UnsupportedOperatorError,
    ValidationError,
)
from .normalizer import FilterNormalizer
from .optimizer import ASTOptimizer
from .parser import FilterParser
from .registry import operator_registry
from .response import create_response_model
from .types import (
    ASTNode,
    BackendQuery,
    ComparisonOperator,
    FieldCondition,
    FieldsNode,
    FieldsSpec,
    FilterAST,
    FilterDict,
    FilterFormat,
    FilterInput,
    FilterValue,
    LogicalCondition,
    LogicalOperator,
    OrderNode,
    OrderSpec,
    QueryCompiler,
    SecurityPolicy,
    ValidationRule,
)
from .validator import FilterValidator

__all__ = [
    # Types
    "FilterValue",
    "FilterDict",
    "OrderSpec",
    "FieldsSpec",
    "FilterFormat",
    "LogicalOperator",
    "ComparisonOperator",
    "FilterInput",
    "ASTNode",
    "FieldCondition",
    "LogicalCondition",
    "OrderNode",
    "FieldsNode",
    "FilterAST",
    "BackendQuery",
    "QueryCompiler",
    "ValidationRule",
    "SecurityPolicy",
    # Errors
    "QEngineError",
    "ParseError",
    "ValidationError",
    "SecurityError",
    "CompilerError",
    "UnsupportedOperatorError",
    "RegistryError",
    "OptimizationError",
    # Config
    "ParserConfig",
    "ValidatorConfig",
    "OptimizerConfig",
    "CacheConfig",
    "QEngineConfig",
    "default_config",
    # Components
    "FilterParser",
    "FilterNormalizer",
    "FilterValidator",
    "ASTBuilder",
    "ASTOptimizer",
    "BaseQueryCompiler",
    "QueryAdapter",
    # Registry
    "operator_registry",
    # Response Model Factory
    "create_response_model",
]
