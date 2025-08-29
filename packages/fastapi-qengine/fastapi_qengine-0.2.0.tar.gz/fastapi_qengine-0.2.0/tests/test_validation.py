"""
Tests for validation and security features.
"""

import pytest

from fastapi_qengine.core.errors import SecurityError, ValidationError
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import ComparisonOperator, SecurityPolicy
from fastapi_qengine.core.validator import FilterValidator


class TestFilterValidator:
    """Test filter validation functionality."""

    def test_validate_simple_filter(self, sample_filter_data):
        """Test validating simple filter."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse(sample_filter_data["simple_equality"])

        # Should not raise any exception
        validator.validate_filter_input(filter_input)

    def test_validate_complex_filter(self, sample_filter_data):
        """Test validating complex filter."""
        validator = FilterValidator()
        parser = FilterParser()

        filter_input = parser.parse(sample_filter_data["complex_query"])

        # Should not raise any exception
        validator.validate_filter_input(filter_input)

    def test_security_policy_blocked_fields(self):
        """Test security policy blocking specific fields."""
        security_policy = SecurityPolicy(blocked_fields=["password", "secret"])
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Should raise SecurityError for blocked field
        filter_input = parser.parse({"where": {"password": "test"}})

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "blocked" in str(exc_info.value)

    def test_security_policy_allowed_fields(self):
        """Test security policy allowing only specific fields."""
        security_policy = SecurityPolicy(allowed_fields=["name", "category", "price"])
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Should raise SecurityError for non-allowed field
        filter_input = parser.parse({"where": {"secret_field": "test"}})

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "not allowed" in str(exc_info.value)

    def test_security_policy_allowed_operators(self):
        """Test security policy restricting operators."""
        security_policy = SecurityPolicy(allowed_operators=[ComparisonOperator.EQ, ComparisonOperator.IN])
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Should raise SecurityError for non-allowed operator
        filter_input = parser.parse({"where": {"price": {"$gt": 50}}})

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "not allowed" in str(exc_info.value)

    def test_security_policy_max_depth(self):
        """Test security policy max depth limit."""
        security_policy = SecurityPolicy(max_depth=2)
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Create deeply nested query that exceeds max depth
        deep_query = {
            "where": {
                "$and": [
                    {"$or": [{"$and": [{"price": {"$gt": 10}}, {"category": "books"}]}, {"name": "test"}]},
                    {"in_stock": True},
                ]
            }
        }

        filter_input = parser.parse(deep_query)

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "depth exceeds" in str(exc_info.value)

    def test_security_policy_max_array_size(self):
        """Test security policy max array size limit."""
        security_policy = SecurityPolicy(max_array_size=3)
        validator = FilterValidator(security_policy=security_policy)
        parser = FilterParser()

        # Create query with array that exceeds max size
        filter_input = parser.parse({"where": {"category": {"$in": ["a", "b", "c", "d", "e"]}}})

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "Array size exceeds" in str(exc_info.value)

    def test_validate_regex_operator(self):
        """Test validation of regex operator."""
        validator = FilterValidator()
        parser = FilterParser()

        # Valid regex
        filter_input = parser.parse({"where": {"name": {"$regex": "^test.*"}}})
        validator.validate_filter_input(filter_input)  # Should not raise

        # Invalid regex
        filter_input = parser.parse({"where": {"name": {"$regex": "[invalid"}}})

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "Invalid regex" in str(exc_info.value)

    def test_validate_exists_operator(self):
        """Test validation of exists operator."""
        validator = FilterValidator()
        parser = FilterParser()

        # Valid exists with boolean
        filter_input = parser.parse({"where": {"name": {"$exists": True}}})
        validator.validate_filter_input(filter_input)  # Should not raise

        # Invalid exists with non-boolean
        filter_input = parser.parse({"where": {"name": {"$exists": "yes"}}})

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "boolean value" in str(exc_info.value)

    def test_validate_size_operator(self):
        """Test validation of size operator."""
        validator = FilterValidator()
        parser = FilterParser()

        # Valid size with positive integer
        filter_input = parser.parse({"where": {"tags": {"$size": 3}}})
        validator.validate_filter_input(filter_input)  # Should not raise

        # Invalid size with negative number
        filter_input = parser.parse({"where": {"tags": {"$size": -1}}})

        with pytest.raises(ValidationError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "non-negative integer" in str(exc_info.value)

    def test_validate_order_clause(self):
        """Test validation of order clause."""
        validator = FilterValidator()
        parser = FilterParser()

        # Valid order
        filter_input = parser.parse({"order": "name,-price"})
        validator.validate_filter_input(filter_input)  # Should not raise

        # Order with blocked field
        security_policy = SecurityPolicy(blocked_fields=["secret"])
        validator = FilterValidator(security_policy=security_policy)

        filter_input = parser.parse({"order": "name,-secret"})

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "blocked" in str(exc_info.value)

    def test_validate_fields_clause(self):
        """Test validation of fields clause."""
        validator = FilterValidator()
        parser = FilterParser()

        # Valid fields
        filter_input = parser.parse({"fields": {"name": 1, "price": 0}})
        validator.validate_filter_input(filter_input)  # Should not raise

        # Fields with blocked field
        security_policy = SecurityPolicy(blocked_fields=["secret"])
        validator = FilterValidator(security_policy=security_policy)

        filter_input = parser.parse({"fields": {"name": 1, "secret": 1}})

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_filter_input(filter_input)

        assert "blocked" in str(exc_info.value)
