# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import json

import pytest

from ipsdk import exceptions
from ipsdk import jsonutils


def test_loads_valid_dict():
    """Test loading a valid JSON dict string."""
    json_str = '{"key": "value", "number": 123}'
    result = jsonutils.loads(json_str)
    assert isinstance(result, dict)
    assert result["key"] == "value"
    assert result["number"] == 123


def test_loads_valid_list():
    """Test loading a valid JSON list string."""
    json_str = "[1, 2, 3, 4]"
    result = jsonutils.loads(json_str)
    assert isinstance(result, list)
    assert result == [1, 2, 3, 4]


def test_loads_valid_nested():
    """Test loading a valid nested JSON structure."""
    json_str = '{"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}'
    result = jsonutils.loads(json_str)
    assert isinstance(result, dict)
    assert "users" in result
    assert len(result["users"]) == 2
    assert result["users"][0]["name"] == "Alice"


def test_loads_valid_empty():
    """Test loading valid empty JSON structures."""
    # Empty dict
    result = jsonutils.loads("{}")
    assert result == {}

    # Empty list
    result = jsonutils.loads("[]")
    assert result == []


def test_loads_valid_special_values():
    """Test loading JSON with special values."""
    json_str = '{"null": null, "bool": true, "number": 42.5}'
    result = jsonutils.loads(json_str)
    assert result["null"] is None
    assert result["bool"] is True
    assert result["number"] == 42.5


def test_loads_invalid_json():
    """Test loading malformed JSON raises JSONError."""
    json_str = '{"key": "value", "missing_end": '
    with pytest.raises(exceptions.ValidationError) as exc_info:
        jsonutils.loads(json_str)

    # Check that the exception contains helpful information
    assert "Failed to parse JSON" in str(exc_info.value)
    assert "input_data" in exc_info.value.details
    assert "json_error" in exc_info.value.details


def test_loads_invalid_json_various():
    """Test various malformed JSON inputs."""
    invalid_inputs = [
        '{"unclosed": ',  # Unclosed object
        "[1, 2, 3",  # Unclosed array
        '{"key": value}',  # Unquoted value
        '{key: "value"}',  # Unquoted key
        '{"duplicate": 1, "duplicate": 2}',  # This is actually valid JSON
        "undefined",  # Invalid literal
        "{,}",  # Invalid syntax
        '{"trailing": "comma",}',  # Trailing comma (invalid in JSON)
    ]

    for invalid_json in invalid_inputs:
        if invalid_json == '{"duplicate": 1, "duplicate": 2}':
            # This is actually valid JSON, so skip
            continue

        with pytest.raises(exceptions.ValidationError):
            jsonutils.loads(invalid_json)


def test_loads_type_error():
    """Test loads with non-string input raises JSONError."""
    with pytest.raises(exceptions.ValidationError) as exc_info:
        jsonutils.loads(123)  # type: ignore[arg-type]

    assert "Unexpected error parsing JSON" in str(exc_info.value)
    assert "original_error" in exc_info.value.details


def test_loads_none_input():
    """Test loads with None input raises JSONError."""
    with pytest.raises(exceptions.ValidationError):
        jsonutils.loads(None)  # type: ignore[arg-type]


def test_dumps_valid_dict():
    """Test dumping a valid dict to JSON."""
    data = {"key": "value", "number": 123}
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    # Verify it can be parsed back
    parsed = json.loads(result)
    assert parsed == data


def test_dumps_valid_list():
    """Test dumping a valid list to JSON."""
    data = [1, 2, 3, 4]
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    # Verify it can be parsed back
    parsed = json.loads(result)
    assert parsed == data


def test_dumps_valid_nested():
    """Test dumping nested structures."""
    data = {
        "users": [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False},
        ],
        "total": 2,
        "metadata": None,
    }
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    # Verify it can be parsed back
    parsed = json.loads(result)
    assert parsed == data


def test_dumps_valid_primitives():
    """Test dumping various primitive types."""
    test_cases = [
        {"string": "hello"},
        {"number": 42},
        {"float": 3.14},
        {"boolean": True},
        {"null": None},
        {"empty_list": []},
        {"empty_dict": {}},
    ]

    for data in test_cases:
        result = jsonutils.dumps(data)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data


def test_dumps_non_serializable():
    """Test dumping non-JSON-serializable objects raises JSONError."""

    class NonSerializable:
        def __init__(self):
            self.value = "test"

    non_serializable_obj = NonSerializable()
    with pytest.raises(exceptions.ValidationError) as exc_info:
        jsonutils.dumps(non_serializable_obj)

    assert "Failed to serialize object to JSON" in str(exc_info.value)
    assert "object_type" in exc_info.value.details
    assert "json_error" in exc_info.value.details


def test_dumps_circular_reference():
    """Test dumping objects with circular references raises JSONError."""
    data = {"key": "value"}
    data["self"] = data  # Create circular reference

    with pytest.raises(exceptions.ValidationError) as exc_info:
        jsonutils.dumps(data)

    assert "Failed to serialize object to JSON" in str(exc_info.value)
    assert "object_type" in exc_info.value.details


def test_dumps_complex_types():
    """Test dumping complex Python types that aren't JSON serializable."""
    import datetime
    import decimal

    non_serializable_objects = [
        datetime.datetime.now(tz=datetime.timezone.utc),
        decimal.Decimal("10.5"),
        {1, 2, 3},  # set
        (1, 2, 3),  # tuple - actually this might be serializable
        b"hello",
    ]

    for obj in non_serializable_objects:
        if isinstance(obj, tuple):
            # Tuples are actually serialized as arrays
            continue

        with pytest.raises(exceptions.ValidationError):
            jsonutils.dumps(obj)


def test_error_details_truncation():
    """Test that large input data is properly truncated in error details."""
    # Create a long invalid JSON string
    long_invalid_json = '{"key": "' + "x" * 300 + '"'  # Missing closing quote and brace

    with pytest.raises(exceptions.ValidationError) as exc_info:
        jsonutils.loads(long_invalid_json)

    # Check that input_data is truncated to 200 characters
    input_data = exc_info.value.details.get("input_data", "")
    assert len(input_data) <= 200


def test_exception_inheritance():
    """Test that JSONError is properly inherited from ValidationError."""
    with pytest.raises(exceptions.ValidationError):  # Should catch JSONError
        jsonutils.loads("invalid json")

    with pytest.raises(exceptions.IpsdkError):  # Should catch JSONError
        jsonutils.loads("invalid json")


def test_round_trip_consistency():
    """Test that dumps -> loads produces the same data."""
    test_data = {
        "string": "hello world",
        "number": 42,
        "float": 3.14159,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3, "four", False],
        "nested": {"inner": "value", "array": [{"a": 1}, {"b": 2}]},
    }

    # dumps -> loads should preserve the data
    json_string = jsonutils.dumps(test_data)
    parsed_data = jsonutils.loads(json_string)

    assert parsed_data == test_data


def test_dumps_tuple_serialization():
    """Test that tuples are serialized as arrays."""
    data = {"tuple": (1, 2, 3)}
    result = jsonutils.dumps(data)
    parsed = json.loads(result)
    assert parsed == {"tuple": [1, 2, 3]}


def test_loads_unicode_strings():
    """Test loading JSON with unicode characters."""
    json_str = '{"message": "Hello 世界", "emoji": "🚀", "accent": "café"}'
    result = jsonutils.loads(json_str)
    assert result["message"] == "Hello 世界"
    assert result["emoji"] == "🚀"
    assert result["accent"] == "café"


def test_dumps_unicode_strings():
    """Test dumping data with unicode characters."""
    data = {"message": "Hello 世界", "emoji": "🚀", "accent": "café"}
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed == data


def test_loads_large_numbers():
    """Test loading JSON with large numbers."""
    json_str = """{
        "large_int": 9223372036854775807,
        "large_float": 1.7976931348623157e+308
    }"""
    result = jsonutils.loads(json_str)
    assert result["large_int"] == 9223372036854775807
    assert result["large_float"] == 1.7976931348623157e+308


def test_dumps_large_numbers():
    """Test dumping large numbers."""
    data = {"large_int": 9223372036854775807, "large_float": 1.7976931348623157e+308}
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed == data


def test_loads_deeply_nested():
    """Test loading deeply nested JSON structures."""
    # Create a deeply nested structure
    nested = {"level": 1}
    current = nested
    for i in range(2, 21):  # Nest 20 levels deep
        current["child"] = {"level": i}
        current = current["child"]

    json_str = jsonutils.dumps(nested)
    result = jsonutils.loads(json_str)
    assert result["level"] == 1

    # Navigate to the deepest level
    current_result = result
    for i in range(2, 21):
        assert "child" in current_result
        current_result = current_result["child"]
        assert current_result["level"] == i


def test_loads_empty_string_raises_error():
    """Test that loading an empty string raises JSONError."""
    with pytest.raises(exceptions.ValidationError) as exc_info:
        jsonutils.loads("")

    assert "Failed to parse JSON" in str(exc_info.value)


def test_loads_whitespace_only():
    """Test loading JSON with only whitespace."""
    with pytest.raises(exceptions.ValidationError):
        jsonutils.loads("   \n\t  ")


def test_dumps_edge_case_values():
    """Test dumping edge case numeric values."""
    data = {
        "zero": 0,
        "negative": -123,
        "negative_float": -3.14,
        "scientific": 1e10,
        "small_scientific": 1e-10
    }
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed == data


def test_loads_scientific_notation():
    """Test loading JSON with scientific notation."""
    json_str = '{"big": 1.23e+10, "small": 4.56e-5}'
    result = jsonutils.loads(json_str)
    assert result["big"] == 1.23e10
    assert result["small"] == 4.56e-5


def test_dumps_unexpected_error():
    """
    Test dumps with an object that raises unexpected exceptions
    during serialization.
    """
    import unittest.mock

    # Mock json.dumps to raise a RuntimeError instead of TypeError/ValueError
    with unittest.mock.patch("json.dumps") as mock_dumps:
        mock_dumps.side_effect = RuntimeError("Unexpected error during serialization")

        with pytest.raises(exceptions.ValidationError) as exc_info:
            jsonutils.dumps({"test": "data"})

        # Should catch the general exception case (not TypeError/ValueError)
        assert "Unexpected error serializing JSON" in str(exc_info.value)
        assert "original_error" in exc_info.value.details
        assert "object_type" in exc_info.value.details


def test_loads_very_long_string():
    """Test loading JSON with very long string values."""
    long_string = "x" * 10000
    json_str = f'{{"long_value": "{long_string}"}}'
    result = jsonutils.loads(json_str)
    assert result["long_value"] == long_string


def test_dumps_very_long_string():
    """Test dumping very long string values."""
    long_string = "x" * 10000
    data = {"long_value": long_string}
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed == data


def test_loads_array_of_mixed_types():
    """Test loading JSON array with mixed data types."""
    json_str = '[1, "string", true, null, {"key": "value"}, [1, 2, 3]]'
    result = jsonutils.loads(json_str)
    expected = [1, "string", True, None, {"key": "value"}, [1, 2, 3]]
    assert result == expected


def test_dumps_array_of_mixed_types():
    """Test dumping array with mixed data types."""
    data = [1, "string", True, None, {"key": "value"}, [1, 2, 3]]
    result = jsonutils.dumps(data)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert parsed == data
