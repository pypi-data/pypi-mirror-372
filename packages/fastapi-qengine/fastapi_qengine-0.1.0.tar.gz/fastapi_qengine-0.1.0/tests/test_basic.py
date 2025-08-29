"""
Basic tests for fastapi-qengine core functionality.
"""

import pytest

from fastapi_qengine.backends.beanie import BeanieQueryCompiler
from fastapi_qengine.core.ast import ASTBuilder
from fastapi_qengine.core.errors import ParseError, ValidationError
from fastapi_qengine.core.normalizer import FilterNormalizer
from fastapi_qengine.core.parser import FilterParser
from fastapi_qengine.core.types import ComparisonOperator, FilterFormat, LogicalOperator


class TestFilterParser:
    """Test filter parsing functionality."""

    def test_parse_json_string(self, sample_json_strings):
        """Test parsing JSON string format."""
        parser = FilterParser()

        result = parser.parse(sample_json_strings["simple"])

        assert result.format == FilterFormat.JSON_STRING
        assert result.where == {"category": "electronics"}
        assert result.order is None

    def test_parse_json_string_complex(self, sample_json_strings):
        """Test parsing complex JSON string."""
        parser = FilterParser()

        result = parser.parse(sample_json_strings["complex"])

        assert result.format == FilterFormat.JSON_STRING
        assert result.where is not None and "$or" in result.where
        assert result.order == "name"

    def test_parse_json_string_with_url_encoding(self):
        """Test parsing URL-encoded JSON string."""
        parser = FilterParser()
        # URL-encoded version of {"where": {"category": "electronics"}}
        encoded_json = "%7B%22where%22%3A%20%7B%22category%22%3A%20%22electronics%22%7D%7D"

        result = parser.parse(encoded_json)

        assert result.format == FilterFormat.JSON_STRING
        assert result.where == {"category": "electronics"}

    def test_parse_dict_input(self, sample_filter_data):
        """Test parsing dictionary input."""
        parser = FilterParser()

        result = parser.parse(sample_filter_data["simple_equality"])

        assert result.format == FilterFormat.DICT_OBJECT
        assert result.where == {"category": "electronics"}

    def test_parse_nested_params(self, sample_nested_params):
        """Test parsing nested parameters format."""
        parser = FilterParser()

        result = parser.parse(sample_nested_params["simple"])

        assert result.format == FilterFormat.NESTED_PARAMS
        assert result.where == {
            "category": "electronics",
            "price": {"$gt": 50},  # Should be converted to number
        }

    def test_parse_nested_params_with_order(self, sample_nested_params):
        """Test parsing nested params with order."""
        parser = FilterParser()

        result = parser.parse(sample_nested_params["with_order"])

        assert result.format == FilterFormat.NESTED_PARAMS
        assert result.where == {"in_stock": True}  # Should be converted to boolean
        assert result.order == "-price"

    def test_parse_invalid_json(self):
        """Test parsing invalid JSON raises error."""
        parser = FilterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('{"invalid": json}')

        assert "Invalid JSON" in str(exc_info.value)

    def test_parse_non_object_json(self):
        """Test parsing non-object JSON raises error."""
        parser = FilterParser()

        with pytest.raises(ParseError) as exc_info:
            parser.parse('["not", "an", "object"]')

        assert "must be an object" in str(exc_info.value)

    def test_convert_value_types(self):
        """Test value type conversion."""
        parser = FilterParser()

        # Test boolean conversion
        assert parser._convert_value("true") is True
        assert parser._convert_value("false") is False
        assert parser._convert_value("null") is None

        # Test numeric conversion
        assert parser._convert_value("42") == 42
        assert abs(parser._convert_value("3.14") - 3.14) < 1e-10

        # Test JSON array conversion
        assert parser._convert_value('["a", "b"]') == ["a", "b"]

        # Test string passthrough
        assert parser._convert_value("hello") == "hello"


class TestFilterNormalizer:
    """Test filter normalization."""

    def test_normalize_where_simple_equality(self):
        """Test normalizing simple equality conditions."""
        normalizer = FilterNormalizer()
        filter_input = FilterParser().parse({"where": {"category": "electronics"}})

        result = normalizer.normalize(filter_input)

        # Simple equality should be converted to explicit $eq
        assert result.where == {"category": {"$eq": "electronics"}}

    def test_normalize_where_complex_condition(self, sample_filter_data):
        """Test normalizing complex conditions."""
        normalizer = FilterNormalizer()
        filter_input = FilterParser().parse(sample_filter_data["comparison_operators"])

        result = normalizer.normalize(filter_input)

        assert result.where == {"price": {"$gt": 50, "$lte": 100}}

    def test_normalize_logical_operators(self, sample_filter_data):
        """Test normalizing logical operators."""
        normalizer = FilterNormalizer()
        filter_input = FilterParser().parse(sample_filter_data["logical_operators"])

        result = normalizer.normalize(filter_input)

        assert result.where is not None
        assert "$or" in result.where
        assert len(result.where["$or"]) == 2

    def test_normalize_invalid_operator(self):
        """Test normalizing invalid operator raises error."""
        normalizer = FilterNormalizer()
        filter_input = FilterParser().parse({"where": {"price": {"invalid": 50}}})

        with pytest.raises(ValidationError) as exc_info:
            normalizer.normalize(filter_input)

        assert "Invalid operator" in str(exc_info.value)

    def test_normalize_fields_boolean_values(self):
        """Test normalizing fields with boolean values."""
        normalizer = FilterNormalizer()
        filter_input = FilterParser().parse({"fields": {"name": True, "price": False, "category": 1}})

        result = normalizer.normalize(filter_input)

        assert result.fields == {"name": 1, "price": 0, "category": 1}


class TestASTBuilder:
    """Test AST building."""

    def test_build_simple_condition(self):
        """Test building AST for simple condition."""
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse({"where": {"category": "electronics"}})
        normalized = normalizer.normalize(filter_input)

        ast = builder.build(normalized)

        assert ast.where is not None
        # Check if it's a comparison node with proper attributes
        if hasattr(ast.where, "field") and hasattr(ast.where, "operator") and hasattr(ast.where, "value"):
            assert ast.where.field == "category"  # type: ignore
            assert ast.where.operator == ComparisonOperator.EQ  # type: ignore
            assert ast.where.value == "electronics"  # type: ignore
        else:
            # For other node types, just verify the AST was built
            assert ast.where is not None

    def test_build_logical_condition(self, sample_filter_data):
        """Test building AST for logical condition."""
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse(sample_filter_data["logical_operators"])
        normalized = normalizer.normalize(filter_input)

        ast = builder.build(normalized)

        assert ast.where is not None
        assert hasattr(ast.where, "operator")
        if hasattr(ast.where, "operator"):
            assert ast.where.operator == LogicalOperator.OR  # type: ignore
        if hasattr(ast.where, "conditions"):
            assert len(ast.where.conditions) == 2  # type:ignore

    def test_build_order_nodes(self):
        """Test building order nodes."""
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse({"order": "name,-price"})
        normalized = normalizer.normalize(filter_input)

        ast = builder.build(normalized)

        assert ast.order is not None
        assert len(ast.order) == 2
        assert ast.order[0].field == "name"
        assert ast.order[0].ascending is True
        assert ast.order[1].field == "price"
        assert ast.order[1].ascending is False

    def test_build_fields_node(self, sample_filter_data):
        """Test building fields node."""
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse(sample_filter_data["complex_query"])
        normalized = normalizer.normalize(filter_input)

        ast = builder.build(normalized)

        assert ast.fields is not None
        assert ast.fields.fields == {"name": 1, "price": 1, "category": 1}

    def test_build_multiple_field_conditions(self):
        """Test building AST with multiple field conditions on same field."""
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse({"where": {"price": {"$gte": 10, "$lte": 100}}})
        normalized = normalizer.normalize(filter_input)

        ast = builder.build(normalized)

        # Should create logical AND condition for multiple operators on same field
        assert ast.where is not None
        assert hasattr(ast.where, "operator")
        assert ast.where.operator == LogicalOperator.AND  # type: ignore

    def test_build_invalid_operator(self):
        """Test building AST with invalid operator raises error."""
        builder = ASTBuilder()

        # Manually create invalid condition to bypass normalizer validation
        from fastapi_qengine.core.types import FilterFormat, FilterInput

        invalid_input = FilterInput(where={"price": {"$invalid": 50}}, format=FilterFormat.DICT_OBJECT)

        with pytest.raises(ParseError) as exc_info:
            builder.build(invalid_input)

        assert "Unknown operator" in str(exc_info.value)


class TestBeanieCompiler:
    """Test Beanie query compilation."""

    def test_compile_simple_condition(self):
        """Test compiling simple condition to MongoDB format."""
        compiler = BeanieQueryCompiler()
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse({"where": {"category": "electronics"}})
        normalized = normalizer.normalize(filter_input)
        ast = builder.build(normalized)

        result = compiler.compile(ast)

        assert "filter" in result
        assert result["filter"] == {"category": "electronics"}

    def test_compile_comparison_operators(self):
        """Test compiling various comparison operators."""
        compiler = BeanieQueryCompiler()
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse({"where": {"price": {"$gt": 50, "$lt": 100}}})
        normalized = normalizer.normalize(filter_input)
        ast = builder.build(normalized)

        result = compiler.compile(ast)

        assert "filter" in result
        # Should have AND condition combining the two price conditions
        assert "$and" in result["filter"]

    def test_compile_logical_operators(self, sample_filter_data):
        """Test compiling logical operators."""
        compiler = BeanieQueryCompiler()
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse(sample_filter_data["logical_operators"])
        normalized = normalizer.normalize(filter_input)
        ast = builder.build(normalized)

        result = compiler.compile(ast)

        assert "filter" in result
        assert "$or" in result["filter"]
        assert len(result["filter"]["$or"]) == 2

    def test_compile_with_ordering(self):
        """Test compiling with ordering."""
        compiler = BeanieQueryCompiler()
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse({"where": {"category": "electronics"}, "order": "name,-price"})
        normalized = normalizer.normalize(filter_input)
        ast = builder.build(normalized)

        result = compiler.compile(ast)

        assert "filter" in result
        assert "sort" in result
        assert result["sort"] == [("name", 1), ("price", -1)]

    def test_compile_with_projection(self, sample_filter_data):
        """Test compiling with field projection."""
        compiler = BeanieQueryCompiler()
        builder = ASTBuilder()
        normalizer = FilterNormalizer()

        filter_input = FilterParser().parse(sample_filter_data["complex_query"])
        normalized = normalizer.normalize(filter_input)
        ast = builder.build(normalized)

        result = compiler.compile(ast)

        assert "filter" in result
        assert "projection" in result
        assert result["projection"] == {"name": 1, "price": 1, "category": 1}

    def test_compile_empty_ast(self):
        """Test compiling empty AST."""
        compiler = BeanieQueryCompiler()
        from fastapi_qengine.core.types import FilterAST

        empty_ast = FilterAST()
        result = compiler.compile(empty_ast)

        # Should return empty result but not fail
        assert isinstance(result, dict)


class TestEndToEndPipeline:
    """Test complete pipeline from input to compiled query."""

    def test_complete_pipeline_simple(self, sample_filter_data):
        """Test complete pipeline with simple filter using explicit backend."""
        from fastapi_qengine import process_filter_to_ast

        compiler = BeanieQueryCompiler()

        ast = process_filter_to_ast(sample_filter_data["simple_equality"])
        result = compiler.compile(ast)

        assert "filter" in result
        assert result["filter"]["category"] == "electronics"

    def test_complete_pipeline_complex(self, sample_filter_data):
        """Test complete pipeline with complex filter using explicit backend."""
        from fastapi_qengine import process_filter_to_ast

        compiler = BeanieQueryCompiler()
        ast = process_filter_to_ast(sample_filter_data["complex_query"])
        result = compiler.compile(ast)

        assert "filter" in result
        assert "sort" in result
        assert "projection" in result

    def test_complete_pipeline_json_string(self, sample_json_strings):
        """Test complete pipeline with JSON string input using explicit backend."""
        from fastapi_qengine import process_filter_to_ast

        compiler = BeanieQueryCompiler()
        ast = process_filter_to_ast(sample_json_strings["complex"])
        result = compiler.compile(ast)

        assert "filter" in result
        assert "$or" in result["filter"]
        assert "sort" in result

    def test_complete_pipeline_nested_params(self, sample_nested_params):
        """Test complete pipeline with nested params using explicit backend."""
        from fastapi_qengine import process_filter_to_ast

        compiler = BeanieQueryCompiler()
        ast = process_filter_to_ast(sample_nested_params["with_order"])
        result = compiler.compile(ast)

        assert "filter" in result
        assert result["filter"]["in_stock"] is True
        assert "sort" in result

    def test_pipeline_error_handling(self):
        """Test pipeline error handling."""
        from fastapi_qengine import process_filter_to_ast
        from fastapi_qengine.core.errors import QEngineError

        # Test invalid JSON
        with pytest.raises(QEngineError):
            process_filter_to_ast('{"invalid": json}')

    def test_empty_filter_handling(self):
        """Test handling of empty/None filters (compiler should handle empty AST)."""
        compiler = BeanieQueryCompiler()
        from fastapi_qengine.core.types import FilterAST

        empty_ast = FilterAST()
        result = compiler.compile(empty_ast)
        assert isinstance(result, dict)
