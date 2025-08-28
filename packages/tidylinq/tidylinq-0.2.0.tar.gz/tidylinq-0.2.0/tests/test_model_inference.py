"""Tests for model inference utilities."""

from typing import Any, Union, cast

from pydantic import BaseModel

from tidylinq.model_inference import (
    create_model_from_data_sample,
    infer_fields_from_data,
    infer_type_from_values,
)


class TestInferTypeFromValues:
    """Test type inference from value samples."""

    def test_empty_values_returns_any(self):
        """Empty values should return Any type."""
        result = infer_type_from_values([])
        assert result is Any

    def test_single_type_values(self):
        """Values of same type should return that type."""
        result = infer_type_from_values([1, 2, 3])
        assert result is int

        result = infer_type_from_values(["a", "b", "c"])
        assert result is str

    def test_mixed_types_returns_union(self):
        """Mixed types should return Union."""
        result = infer_type_from_values([1, "a", True])
        assert hasattr(result, "__origin__")
        assert result.__origin__ is Union


class TestInferFieldsFromData:
    """Test field inference from structured data samples."""

    def test_empty_data_returns_empty_dict(self):
        """Empty data should return empty field definitions."""
        result = infer_fields_from_data([])
        assert result == {}

    def test_dict_data_infers_field_types(self):
        """Dictionary data should infer field types correctly."""
        data = [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
            {"name": "Charlie", "age": 35},  # Missing active field
        ]

        result = infer_fields_from_data(data)

        # All fields should be present
        assert "name" in result
        assert "age" in result
        assert "active" in result

        # Check that types are correct
        name_type, name_default = result["name"]
        age_type, age_default = result["age"]
        active_type, active_default = result["active"]

        # name and age are present in all samples
        assert name_type is str
        assert age_type is int

        # active is missing in one sample, so should be Optional
        assert str(active_type) == "bool | None", active_type

    def test_basemodel_data_extracts_fields(self):
        """BaseModel data should extract field information."""

        class Person(BaseModel):
            name: str
            age: int
            active: bool = True

        data = [
            Person(name="Alice", age=30),
            Person(name="Bob", age=25, active=False),
        ]

        result = infer_fields_from_data(data)

        assert "name" in result
        assert "age" in result
        assert "active" in result

        # Check types match original model
        name_type, name_default = result["name"]
        age_type, age_default = result["age"]
        active_type, active_default = result["active"]

        assert name_type is str
        assert age_type is int
        assert active_type is bool
        assert active_default is True  # Default value

    def test_primitive_data_returns_empty(self):
        """Primitive data should return empty dict (handled by create_model_from_data_sample)."""
        data = [1, 2, 3, 4, 5]

        result = infer_fields_from_data(data)

        # infer_fields_from_data is for structured data, primitives return empty
        assert result == {}


class TestCreateModelFromDataSample:
    """Test model creation from data samples."""

    def test_empty_data_creates_empty_model(self):
        """Empty data should create a model with no fields."""
        Model = create_model_from_data_sample([])

        # Should be able to create instance with no fields
        instance = Model()
        assert instance is not None

    def test_dict_data_creates_model(self):
        """Dictionary data should create a working model."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

        Model = create_model_from_data_sample(data, "PersonModel")

        # Should be able to create instances
        instance = cast(Any, Model(name="Charlie", age=35))
        assert instance.name == "Charlie"
        assert instance.age == 35

    def test_basemodel_data_returns_same_type(self):
        """If all samples are same BaseModel type, should return that type."""

        class Person(BaseModel):
            name: str
            age: int

        data = [
            Person(name="Alice", age=30),
            Person(name="Bob", age=25),
        ]

        Model = create_model_from_data_sample(data)

        # Should return the original Person class
        assert Model is Person

    def test_mixed_basemodel_types_creates_new_model(self):
        """Mixed BaseModel types should create a new inferred model."""

        class Person(BaseModel):
            name: str
            age: int

        class Employee(BaseModel):
            name: str
            salary: float

        data = [
            Person(name="Alice", age=30),
            Employee(name="Bob", salary=50000.0),
        ]

        Model = create_model_from_data_sample(data)

        # Should create a new model, not return Person or Employee
        assert Model is not Person
        assert Model is not Employee
        assert Model.__name__ == "InferredSchema"

    def test_primitive_data_creates_value_model(self):
        """Primitive data should create a model with 'value' field."""
        data = [1, 2, 3, 4, 5]

        Model = create_model_from_data_sample(data, "NumberModel")

        # Should have a 'value' field
        instance = cast(Any, Model(value=42))
        assert instance.value == 42

    def test_custom_model_name(self):
        """Should use custom model name when provided."""
        data = [{"x": 1}, {"x": 2}]

        Model = create_model_from_data_sample(data, "CustomName")

        assert Model.__name__ == "CustomName"


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_full_workflow_with_complex_data(self):
        """Test complete workflow with complex nested data."""
        data = [
            {
                "user": "alice",
                "metadata": {"score": 95, "premium": True},
                "tags": ["python", "data"],
            },
            {
                "user": "bob",
                "metadata": {"score": 87, "premium": False},
                "tags": ["javascript"],
            },
            {
                "user": "charlie",
                "metadata": {"score": 92},  # Missing premium
                "tags": [],
            },
        ]

        Model = create_model_from_data_sample(data, "UserModel")

        # Should be able to create instances with optional fields
        instance = cast(
            Any,
            Model(user="dave", metadata={"score": 88, "premium": True}, tags=["rust", "systems"]),
        )

        assert instance.user == "dave"
        assert instance.metadata == {"score": 88, "premium": True}
        assert instance.tags == ["rust", "systems"]
