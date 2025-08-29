"""
Logical operators for query building.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from ..core.types import LogicalOperator


class LogicalOperatorHandler(ABC):
    """Base class for logical operator handlers."""

    @abstractmethod
    def compile(self, conditions: List[Any], backend: str) -> Any:
        """Compile logical operator with conditions."""
        pass


class AndOperatorHandler(LogicalOperatorHandler):
    """Handler for $and operator."""

    def compile(self, conditions: List[Any], backend: str) -> Any:
        """Compile $and operator."""
        if backend == "beanie" or backend == "pymongo":
            return {"$and": conditions}
        elif backend == "sqlalchemy":
            # For SQLAlchemy, would use and_() function
            pass  # Implement when SQLAlchemy backend is added
        else:
            raise NotImplementedError(f"$and not implemented for backend: {backend}")


class OrOperatorHandler(LogicalOperatorHandler):
    """Handler for $or operator."""

    def compile(self, conditions: List[Any], backend: str) -> Any:
        """Compile $or operator."""
        if backend == "beanie" or backend == "pymongo":
            return {"$or": conditions}
        elif backend == "sqlalchemy":
            # For SQLAlchemy, would use or_() function
            pass  # Implement when SQLAlchemy backend is added
        else:
            raise NotImplementedError(f"$or not implemented for backend: {backend}")


class NorOperatorHandler(LogicalOperatorHandler):
    """Handler for $nor operator."""

    def compile(self, conditions: List[Any], backend: str) -> Any:
        """Compile $nor operator."""
        if backend == "beanie" or backend == "pymongo":
            return {"$nor": conditions}
        else:
            raise NotImplementedError(f"$nor not implemented for backend: {backend}")


# Registry of logical operators
LOGICAL_OPERATORS = {
    LogicalOperator.AND: AndOperatorHandler(),
    LogicalOperator.OR: OrOperatorHandler(),
    LogicalOperator.NOR: NorOperatorHandler(),
}
