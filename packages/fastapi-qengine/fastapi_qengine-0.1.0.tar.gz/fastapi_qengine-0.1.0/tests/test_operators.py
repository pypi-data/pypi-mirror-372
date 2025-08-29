"""
Tests for operators functionality.
"""

import pytest

from fastapi_qengine.core.types import ComparisonOperator, LogicalOperator
from fastapi_qengine.operators.comparison import COMPARISON_OPERATORS
from fastapi_qengine.operators.custom import create_simple_operator, register_custom_operator
from fastapi_qengine.operators.logical import LOGICAL_OPERATORS


class TestComparisonOperators:
    """Test comparison operators."""

    def test_equal_operator(self):
        """Test $eq operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.EQ]
        result = handler.compile("category", "electronics", "beanie")

        assert result == {"category": "electronics"}

    def test_not_equal_operator(self):
        """Test $ne operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.NE]
        result = handler.compile("category", "electronics", "beanie")

        assert result == {"category": {"$ne": "electronics"}}

    def test_greater_than_operator(self):
        """Test $gt operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.GT]
        result = handler.compile("price", 50, "beanie")

        assert result == {"price": {"$gt": 50}}

    def test_greater_than_equal_operator(self):
        """Test $gte operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.GTE]
        result = handler.compile("price", 50, "beanie")

        assert result == {"price": {"$gte": 50}}

    def test_less_than_operator(self):
        """Test $lt operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.LT]
        result = handler.compile("price", 100, "beanie")

        assert result == {"price": {"$lt": 100}}

    def test_less_than_equal_operator(self):
        """Test $lte operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.LTE]
        result = handler.compile("price", 100, "beanie")

        assert result == {"price": {"$lte": 100}}

    def test_in_operator(self):
        """Test $in operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.IN]
        result = handler.compile("category", ["electronics", "books"], "beanie")

        assert result == {"category": {"$in": ["electronics", "books"]}}

    def test_not_in_operator(self):
        """Test $nin operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.NIN]
        result = handler.compile("category", ["electronics", "books"], "beanie")

        assert result == {"category": {"$nin": ["electronics", "books"]}}

    def test_regex_operator(self):
        """Test $regex operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.REGEX]
        result = handler.compile("name", "^test.*", "beanie")

        assert result == {"name": {"$regex": "^test.*"}}

    def test_exists_operator(self):
        """Test $exists operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.EXISTS]
        result = handler.compile("name", True, "beanie")

        assert result == {"name": {"$exists": True}}

    def test_size_operator(self):
        """Test $size operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.SIZE]
        result = handler.compile("tags", 3, "beanie")

        assert result == {"tags": {"$size": 3}}

    def test_type_operator(self):
        """Test $type operator."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.TYPE]
        result = handler.compile("value", "string", "beanie")

        assert result == {"value": {"$type": "string"}}

    def test_unsupported_backend(self):
        """Test operator with unsupported backend."""
        handler = COMPARISON_OPERATORS[ComparisonOperator.EQ]

        with pytest.raises(NotImplementedError):
            handler.compile("field", "value", "unsupported_backend")


class TestLogicalOperators:
    """Test logical operators."""

    def test_and_operator(self):
        """Test $and operator."""
        handler = LOGICAL_OPERATORS[LogicalOperator.AND]
        conditions = [{"category": "electronics"}, {"price": {"$gt": 50}}]

        result = handler.compile(conditions, "beanie")

        assert result == {"$and": conditions}

    def test_or_operator(self):
        """Test $or operator."""
        handler = LOGICAL_OPERATORS[LogicalOperator.OR]
        conditions = [{"category": "electronics"}, {"price": {"$lt": 20}}]

        result = handler.compile(conditions, "beanie")

        assert result == {"$or": conditions}

    def test_nor_operator(self):
        """Test $nor operator."""
        handler = LOGICAL_OPERATORS[LogicalOperator.NOR]
        conditions = [{"category": "electronics"}, {"price": {"$gt": 100}}]

        result = handler.compile(conditions, "beanie")

        assert result == {"$nor": conditions}

    def test_logical_operator_unsupported_backend(self):
        """Test logical operator with unsupported backend."""
        handler = LOGICAL_OPERATORS[LogicalOperator.AND]

        with pytest.raises(NotImplementedError):
            handler.compile([], "unsupported_backend")


class TestCustomOperators:
    """Test custom operators functionality."""

    def test_create_simple_operator(self):
        """Test creating a simple custom operator."""

        def custom_impl(field, value):
            return {field: {"$custom": value}}

        create_simple_operator("$custom_test", custom_impl)

        # Test that it was registered
        from fastapi_qengine.core.registry import operator_registry

        assert operator_registry.is_registered("$custom_test", "beanie")

    def test_register_custom_operator_class(self):
        """Test registering a custom operator with a class."""
        from fastapi_qengine.operators.custom import CustomOperatorHandler

        class TestCustomOperator(CustomOperatorHandler):
            def compile(self, field: str, value, backend: str):
                return {field: {"$test_custom": value}}

            @property
            def supported_backends(self) -> list:
                return ["beanie", "pymongo"]

        register_custom_operator("$test_custom", TestCustomOperator())

        # Test that it was registered
        from fastapi_qengine.core.registry import operator_registry

        assert operator_registry.is_registered("$test_custom", "beanie")
        assert operator_registry.is_registered("$test_custom", "pymongo")
        assert not operator_registry.is_registered("$test_custom", "sqlalchemy")

    def test_builtin_custom_operators(self):
        """Test that built-in custom operators are registered."""
        from fastapi_qengine.core.registry import operator_registry

        # These should be registered by default
        assert operator_registry.is_registered("$text", "beanie")
        assert operator_registry.is_registered("$geoWithin", "beanie")
        assert operator_registry.is_registered("$near", "beanie")

    def test_get_operator_handler(self):
        """Test getting operator handlers."""
        from fastapi_qengine.operators.custom import get_operator_handler

        # Test comparison operator
        handler = get_operator_handler("$eq")
        assert handler is not None

        # Test logical operator
        handler = get_operator_handler("$and")
        assert handler is not None

        # Test custom operator
        handler = get_operator_handler("$text", "beanie")
        assert handler is not None

        # Test unknown operator
        with pytest.raises(ValueError):
            get_operator_handler("$unknown")

    def test_compile_operator(self):
        """Test compiling operators."""
        from fastapi_qengine.operators.custom import compile_operator

        # Test comparison operator
        result = compile_operator("$eq", "category", "electronics", "beanie")
        assert result == {"category": "electronics"}

        # Test logical operator
        conditions = [{"category": "electronics"}]
        result = compile_operator("$and", "", conditions, "beanie")
        assert result == {"$and": conditions}

        # Test with unknown operator
        with pytest.raises(ValueError):
            compile_operator("$unknown", "field", "value", "beanie")
