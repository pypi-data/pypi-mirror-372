"""
Model inference utilities for schema creation from data samples.

Provides functions to automatically infer Pydantic model schemas from sample data,
supporting various data types including dictionaries and existing BaseModel instances.
"""

from typing import Any, Union

from pydantic import BaseModel, create_model


def infer_type_from_values(values: list[Any]) -> type | Any:
    """Infer a single type from a list of values.

    Args:
        values: List of values to analyze for type inference

    Returns:
        Inferred type (int, str, Union[...], etc.)
    """
    if not values:
        return Any

    types = []
    for item in values:
        types.append(type(item))

    # If all values are the same type, return that type
    if all(t == types[0] for t in types):
        return types[0]

    # If <= 3 different types, return Union of the types
    unique_types = set(types)
    if len(unique_types) <= 3:
        return Union[tuple(unique_types)]  # type: ignore  # noqa: UP007

    # If mixed types, return Any
    return Any


def infer_fields_from_data(data_samples: list[Any]) -> dict[str, tuple[type, Any]]:
    """Infer field definitions from structured data samples.

    Args:
        data_samples: List of dict or BaseModel instances to analyze

    Returns:
        Dict mapping field names to (type, default_value) tuples
    """
    if not data_samples:
        return {}

    first_item = data_samples[0]

    if isinstance(first_item, BaseModel):
        # Check if all samples are the same BaseModel type
        model_type = type(first_item)
        if all(isinstance(item, BaseModel) and type(item) is model_type for item in data_samples):
            # Extract from Pydantic model fields
            field_definitions = {}
            for field_name, field_info in model_type.model_fields.items():
                field_type = field_info.annotation
                # Determine if field is optional
                default_value = field_info.default if field_info.default is not ... else ...
                field_definitions[field_name] = (field_type, default_value)
            return field_definitions

    if isinstance(first_item, dict | BaseModel):
        # Infer from dictionary/mixed structure
        all_keys = set()
        for item in data_samples:
            if isinstance(item, dict):
                all_keys.update(item.keys())
            elif isinstance(item, BaseModel):
                all_keys.update(type(item).model_fields.keys())

        field_definitions = {}
        for key in all_keys:
            # Collect all values for this key across samples
            values = []
            present_count = 0
            for item in data_samples:
                if isinstance(item, dict) and key in item:
                    values.append(item[key])
                    present_count += 1
                elif isinstance(item, BaseModel) and hasattr(item, key):
                    values.append(getattr(item, key))
                    present_count += 1

            # Infer type from collected values
            if values:
                field_type = infer_type_from_values(values)
                # Make field optional if not present in all samples
                if present_count < len(data_samples):
                    field_type = field_type | None
                field_definitions[key] = (field_type, ...)
            else:
                field_definitions[key] = (Any, ...)

        return field_definitions

    # For non-structured data, return empty (will be handled by create_model_from_data_sample)
    return {}


def create_model_from_data_sample(
    data_samples: list[Any],
    model_name: str = "InferredSchema",
) -> type[BaseModel]:
    """Create a Pydantic model by inferring schema from data samples.

    Args:
        data_samples: List of data items to analyze
        model_name: Name for the generated model class

    Returns:
        Dynamically created Pydantic model class
    """
    if len(data_samples) == 0:
        return create_model(model_name)

    first_item = data_samples[0]

    # Handle primitive data: wrap in "value" field
    if not isinstance(first_item, dict | BaseModel):
        field_type = infer_type_from_values(data_samples)
        return create_model(model_name, value=(field_type, ...))

    # Handle structured data: get field definitions
    field_definitions = infer_fields_from_data(data_samples)

    # Special case: if all samples are the same BaseModel type, return that type
    if isinstance(first_item, BaseModel):
        model_type = type(first_item)
        if all(isinstance(item, BaseModel) and type(item) is model_type for item in data_samples):
            return model_type

    return create_model(model_name, **field_definitions)  # type: ignore
