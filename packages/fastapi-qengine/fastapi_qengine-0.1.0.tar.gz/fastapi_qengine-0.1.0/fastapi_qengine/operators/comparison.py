"""
Comparison operators for query building.
"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.types import ComparisonOperator


class ComparisonOperatorHandler(ABC):
    """Base class for comparison operator handlers."""

    @abstractmethod
    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile comparison operator with field and value."""
        pass


class EqualOperatorHandler(ComparisonOperatorHandler):
    """Handler for $eq operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $eq operator."""
        if backend in ["beanie", "pymongo"]:
            # In MongoDB, simple equality doesn't need $eq operator
            return {field: value}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field == value
            pass  # Implement when SQLAlchemy backend is added
        else:
            raise NotImplementedError(f"$eq not implemented for backend: {backend}")


class NotEqualOperatorHandler(ComparisonOperatorHandler):
    """Handler for $ne operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $ne operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$ne": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field != value
            pass
        else:
            raise NotImplementedError(f"$ne not implemented for backend: {backend}")


class GreaterThanOperatorHandler(ComparisonOperatorHandler):
    """Handler for $gt operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $gt operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$gt": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field > value
            pass
        else:
            raise NotImplementedError(f"$gt not implemented for backend: {backend}")


class GreaterThanEqualOperatorHandler(ComparisonOperatorHandler):
    """Handler for $gte operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $gte operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$gte": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field >= value
            pass
        else:
            raise NotImplementedError(f"$gte not implemented for backend: {backend}")


class LessThanOperatorHandler(ComparisonOperatorHandler):
    """Handler for $lt operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $lt operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$lt": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field < value
            pass
        else:
            raise NotImplementedError(f"$lt not implemented for backend: {backend}")


class LessThanEqualOperatorHandler(ComparisonOperatorHandler):
    """Handler for $lte operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $lte operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$lte": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field <= value
            pass
        else:
            raise NotImplementedError(f"$lte not implemented for backend: {backend}")


class InOperatorHandler(ComparisonOperatorHandler):
    """Handler for $in operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $in operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$in": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field.in_(value)
            pass
        else:
            raise NotImplementedError(f"$in not implemented for backend: {backend}")


class NotInOperatorHandler(ComparisonOperatorHandler):
    """Handler for $nin operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $nin operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$nin": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: ~field.in_(value)
            pass
        else:
            raise NotImplementedError(f"$nin not implemented for backend: {backend}")


class RegexOperatorHandler(ComparisonOperatorHandler):
    """Handler for $regex operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $regex operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$regex": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field.regexp(value) or similar
            pass
        else:
            raise NotImplementedError(f"$regex not implemented for backend: {backend}")


class ExistsOperatorHandler(ComparisonOperatorHandler):
    """Handler for $exists operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $exists operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$exists": value}}
        elif backend == "sqlalchemy":
            # For SQLAlchemy: field.isnot(None) or field.is_(None)
            pass
        else:
            raise NotImplementedError(f"$exists not implemented for backend: {backend}")


class SizeOperatorHandler(ComparisonOperatorHandler):
    """Handler for $size operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $size operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$size": value}}
        else:
            raise NotImplementedError(f"$size not implemented for backend: {backend}")


class TypeOperatorHandler(ComparisonOperatorHandler):
    """Handler for $type operator."""

    def compile(self, field: str, value: Any, backend: str) -> Any:
        """Compile $type operator."""
        if backend in ["beanie", "pymongo"]:
            return {field: {"$type": value}}
        else:
            raise NotImplementedError(f"$type not implemented for backend: {backend}")


# Registry of comparison operators
COMPARISON_OPERATORS = {
    ComparisonOperator.EQ: EqualOperatorHandler(),
    ComparisonOperator.NE: NotEqualOperatorHandler(),
    ComparisonOperator.GT: GreaterThanOperatorHandler(),
    ComparisonOperator.GTE: GreaterThanEqualOperatorHandler(),
    ComparisonOperator.LT: LessThanOperatorHandler(),
    ComparisonOperator.LTE: LessThanEqualOperatorHandler(),
    ComparisonOperator.IN: InOperatorHandler(),
    ComparisonOperator.NIN: NotInOperatorHandler(),
    ComparisonOperator.REGEX: RegexOperatorHandler(),
    ComparisonOperator.EXISTS: ExistsOperatorHandler(),
    ComparisonOperator.SIZE: SizeOperatorHandler(),
    ComparisonOperator.TYPE: TypeOperatorHandler(),
}
