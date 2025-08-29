#!/usr/bin/env python3
"""
Tests for new stdlib functions that enhance developer experience.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from clyp.stdlib import (
    debug, profile, json_parse, json_stringify, deep_merge, get_nested, set_nested,
    clamp, lerp, unique, group_by, partition, zip_dict, pick, omit,
    format_bytes, format_duration
)
from clyp.ErrorHandling import ClypRuntimeError


class TestDebugUtilities:
    """Test debug and profiling utilities."""

    @patch('builtins.print')
    def test_debug_simple_value(self, mock_print):
        value = 42
        result = debug(value, "test")
        
        assert result == value  # Should return original value
        mock_print.assert_called()
        
        # Check that debug info was printed
        call_args = str(mock_print.call_args)
        assert "test:" in call_args
        assert "42" in call_args

    @patch('builtins.print')
    def test_debug_complex_value(self, mock_print):
        value = {"name": "Alice", "age": 30}
        result = debug(value)
        
        assert result == value
        mock_print.assert_called()

    @patch('builtins.print')
    def test_profile_decorator(self, mock_print):
        @profile
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == 10
        
        # Should print profiling information
        mock_print.assert_called()
        call_str = str(mock_print.call_args_list)
        assert "PROFILE" in call_str
        assert "test_func" in call_str
        assert "Execution time" in call_str
        assert "Memory usage" in call_str


class TestJSONUtilities:
    """Test enhanced JSON parsing and stringifying."""

    def test_json_parse_valid(self):
        json_str = '{"name": "Alice", "age": 30}'
        result = json_parse(json_str)
        
        assert result == {"name": "Alice", "age": 30}

    def test_json_parse_invalid(self):
        json_str = '{"name": "Alice", "age":}'  # Invalid JSON
        
        with pytest.raises(ClypRuntimeError) as exc_info:
            json_parse(json_str)
        
        assert "[V200]" in str(exc_info.value)
        assert "JSON parsing failed" in str(exc_info.value)

    def test_json_stringify_simple(self):
        obj = {"name": "Alice", "age": 30}
        result = json_stringify(obj)
        
        assert json.loads(result) == obj

    def test_json_stringify_pretty(self):
        obj = {"name": "Alice", "age": 30}
        result = json_stringify(obj, pretty=True)
        
        assert "\n" in result  # Should have newlines for pretty formatting
        assert json.loads(result) == obj

    def test_json_stringify_with_default(self):
        class CustomObj:
            def __str__(self):
                return "custom"
        
        obj = {"data": CustomObj()}
        result = json_stringify(obj)
        
        assert '"custom"' in result


class TestDictionaryUtilities:
    """Test dictionary manipulation functions."""

    def test_deep_merge_simple(self):
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        
        result = deep_merge(dict1, dict2)
        
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested(self):
        dict1 = {"user": {"name": "Alice", "age": 30}}
        dict2 = {"user": {"age": 31, "email": "alice@test.com"}}
        
        result = deep_merge(dict1, dict2)
        
        expected = {
            "user": {
                "name": "Alice", 
                "age": 31, 
                "email": "alice@test.com"
            }
        }
        assert result == expected

    def test_get_nested_existing_path(self):
        obj = {"user": {"profile": {"name": "Alice"}}}
        
        result = get_nested(obj, "user.profile.name")
        assert result == "Alice"

    def test_get_nested_missing_path(self):
        obj = {"user": {"profile": {"name": "Alice"}}}
        
        result = get_nested(obj, "user.settings.theme", "dark")
        assert result == "dark"

    def test_set_nested_new_path(self):
        obj = {}
        
        result = set_nested(obj, "user.profile.name", "Alice")
        
        expected = {"user": {"profile": {"name": "Alice"}}}
        assert result == expected

    def test_pick_keys(self):
        obj = {"name": "Alice", "age": 30, "email": "alice@test.com"}
        
        result = pick(obj, ["name", "age"])
        
        assert result == {"name": "Alice", "age": 30}

    def test_omit_keys(self):
        obj = {"name": "Alice", "age": 30, "email": "alice@test.com"}
        
        result = omit(obj, ["email"])
        
        assert result == {"name": "Alice", "age": 30}


class TestMathUtilities:
    """Test mathematical utility functions."""

    def test_clamp_within_bounds(self):
        result = clamp(5, 0, 10)
        assert result == 5

    def test_clamp_below_min(self):
        result = clamp(-5, 0, 10)
        assert result == 0

    def test_clamp_above_max(self):
        result = clamp(15, 0, 10)
        assert result == 10

    def test_lerp_start(self):
        result = lerp(0, 10, 0.0)
        assert result == 0

    def test_lerp_end(self):
        result = lerp(0, 10, 1.0)
        assert result == 10

    def test_lerp_middle(self):
        result = lerp(0, 10, 0.5)
        assert result == 5


class TestListUtilities:
    """Test list manipulation functions."""

    def test_unique_preserves_order(self):
        items = [1, 2, 3, 2, 4, 1, 5]
        
        result = unique(items)
        
        assert result == [1, 2, 3, 4, 5]

    def test_group_by_function(self):
        items = ["apple", "banana", "apricot", "berry"]
        
        result = group_by(items, lambda x: x[0])  # Group by first letter
        
        assert result["a"] == ["apple", "apricot"]
        assert result["b"] == ["banana", "berry"]

    def test_partition_function(self):
        items = [1, 2, 3, 4, 5, 6]
        
        evens, odds = partition(items, lambda x: x % 2 == 0)
        
        assert evens == [2, 4, 6]
        assert odds == [1, 3, 5]

    def test_zip_dict(self):
        keys = ["name", "age", "email"]
        values = ["Alice", 30, "alice@test.com"]
        
        result = zip_dict(keys, values)
        
        expected = {"name": "Alice", "age": 30, "email": "alice@test.com"}
        assert result == expected


class TestFormattingUtilities:
    """Test formatting utility functions."""

    def test_format_bytes_small(self):
        assert format_bytes(0) == "0 B"
        assert format_bytes(512) == "512 B"

    def test_format_bytes_kilobytes(self):
        assert format_bytes(1024) == "1 KB"
        assert format_bytes(1536) == "1.5 KB"

    def test_format_bytes_megabytes(self):
        assert format_bytes(1024 * 1024) == "1 MB"
        assert format_bytes(1.5 * 1024 * 1024) == "1.5 MB"

    def test_format_bytes_gigabytes(self):
        assert format_bytes(1024 * 1024 * 1024) == "1 GB"

    def test_format_duration_seconds(self):
        assert format_duration(30) == "30.0s"
        assert format_duration(45.5) == "45.5s"

    def test_format_duration_minutes(self):
        assert format_duration(60) == "1m"
        assert format_duration(90) == "1m 30s"
        assert format_duration(150) == "2m 30s"

    def test_format_duration_hours(self):
        assert format_duration(3600) == "1h"
        assert format_duration(3660) == "1h 1m"
        assert format_duration(3690) == "1h 1m 30s"

    def test_format_duration_complex(self):
        # 2 hours, 30 minutes, 45 seconds
        seconds = 2 * 3600 + 30 * 60 + 45
        result = format_duration(seconds)
        assert result == "2h 30m 45s"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_debug_with_none(self):
        result = debug(None, "null test")
        assert result is None

    def test_get_nested_with_none_object(self):
        result = get_nested(None, "any.path", "default")
        assert result == "default"

    def test_clamp_equal_bounds(self):
        result = clamp(5, 5, 5)
        assert result == 5

    def test_unique_empty_list(self):
        result = unique([])
        assert result == []

    def test_group_by_empty_list(self):
        result = group_by([], lambda x: x)
        assert result == {}

    def test_format_bytes_negative(self):
        result = format_bytes(-1024)
        assert "KB" in result  # Should handle negative sizes

    def test_partition_all_true(self):
        items = [2, 4, 6, 8]
        true_items, false_items = partition(items, lambda x: x % 2 == 0)
        
        assert true_items == [2, 4, 6, 8]
        assert false_items == []

    def test_deep_merge_empty_dicts(self):
        result = deep_merge({}, {})
        assert result == {}

    def test_lerp_reverse(self):
        result = lerp(10, 0, 0.3)
        assert result == 7.0  # 10 - 0.3 * 10


class TestIntegrationWithClypFeatures:
    """Test how new stdlib functions work with Clyp language features."""

    def test_json_parse_with_debug(self):
        json_str = '{"test": "value"}'
        result = debug(json_parse(json_str), "parsed JSON")
        
        assert result == {"test": "value"}

    def test_format_utilities_integration(self):
        # Test combining multiple formatting functions
        size = 1024 * 1024 * 2.5  # 2.5 MB
        duration = 3665  # 1h 1m 5s
        
        size_str = format_bytes(size)
        duration_str = format_duration(duration)
        
        assert "2.5 MB" == size_str
        assert "1h 1m 5s" == duration_str

    def test_collection_utilities_pipeline(self):
        # Test chaining multiple collection operations
        data = [1, 2, 3, 2, 4, 5, 4, 6]
        
        # Remove duplicates, group by even/odd, pick even numbers
        unique_data = unique(data)
        grouped = group_by(unique_data, lambda x: "even" if x % 2 == 0 else "odd")
        evens = grouped.get("even", [])
        
        assert evens == [2, 4, 6]