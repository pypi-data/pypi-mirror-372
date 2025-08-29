#!/usr/bin/env python3
"""
Tests for new Clyp language features that improve developer experience.
"""

import pytest
from clyp.transpiler import parse_clyp
from clyp.ErrorHandling import ClypSyntaxError


class TestStringInterpolation:
    """Test string interpolation features."""

    def test_basic_string_interpolation(self):
        clyp_code = 'let name = "World"; print("Hello {name}");'
        python_code = parse_clyp(clyp_code)
        assert 'f"Hello {name}"' in python_code

    def test_single_quote_interpolation(self):
        clyp_code = "let x = 42; print('Value: {x}');"
        python_code = parse_clyp(clyp_code)
        assert "f'Value: {x}'" in python_code

    def test_expression_interpolation(self):
        clyp_code = 'let a = 5; let b = 3; print("Sum: {a + b}");'
        python_code = parse_clyp(clyp_code)
        assert 'f"Sum: {a + b}"' in python_code

    def test_nested_interpolation(self):
        clyp_code = 'let user = {"name": "Alice"}; print("Hello {user["name"]}");'
        python_code = parse_clyp(clyp_code)
        assert 'f"Hello {user["name"]}"' in python_code


class TestOptionalChaining:
    """Test optional chaining syntax."""

    def test_basic_optional_chaining(self):
        clyp_code = 'let result = obj?.property;'
        python_code = parse_clyp(clyp_code)
        assert '(obj.property if obj is not None else None)' in python_code

    def test_method_optional_chaining(self):
        clyp_code = 'let result = user?.getName();'
        python_code = parse_clyp(clyp_code)
        assert '(user.getName() if user is not None else None)' in python_code

    def test_chained_optional_access(self):
        clyp_code = 'let result = data?.user?.profile;'
        python_code = parse_clyp(clyp_code)
        # Should handle nested optional chaining
        assert 'is not None' in python_code


class TestNullCoalescing:
    """Test null coalescing operator."""

    def test_basic_null_coalescing(self):
        clyp_code = 'let result = value ?? "default";'
        python_code = parse_clyp(clyp_code)
        assert '(value if value is not None else "default")' in python_code

    def test_null_coalescing_with_expressions(self):
        clyp_code = 'let result = getUser() ?? createUser();'
        python_code = parse_clyp(clyp_code)
        assert '(getUser() if getUser() is not None else createUser())' in python_code

    def test_chained_null_coalescing(self):
        clyp_code = 'let result = a ?? b ?? "fallback";'
        python_code = parse_clyp(clyp_code)
        # Should handle multiple ?? operators
        assert 'is not None' in python_code


class TestRangeExpressions:
    """Test range expression syntax."""

    def test_inclusive_range(self):
        clyp_code = 'for i in 1..10 { print(i); }'
        python_code = parse_clyp(clyp_code)
        assert 'range(1, 11)' in python_code

    def test_exclusive_range(self):
        clyp_code = 'for i in 1..<10 { print(i); }'
        python_code = parse_clyp(clyp_code)
        assert 'range(1, 10)' in python_code

    def test_range_in_assignment(self):
        clyp_code = 'let numbers = 1..5;'
        python_code = parse_clyp(clyp_code)
        assert 'range(1, 6)' in python_code


class TestLambdaExpressions:
    """Test lambda expression syntax."""

    def test_single_parameter_lambda(self):
        clyp_code = 'let double = x => x * 2;'
        python_code = parse_clyp(clyp_code)
        assert 'lambda x: x * 2' in python_code

    def test_multi_parameter_lambda(self):
        clyp_code = 'let add = (a, b) => a + b;'
        python_code = parse_clyp(clyp_code)
        assert 'lambda a, b: a + b' in python_code

    def test_lambda_with_complex_expression(self):
        clyp_code = 'let process = item => item.value * 2 + 1;'
        python_code = parse_clyp(clyp_code)
        assert 'lambda item: item.value * 2 + 1' in python_code


class TestGuardClauses:
    """Test guard clause syntax."""

    def test_basic_guard_clause(self):
        clyp_code = 'guard x > 0 else return false;'
        python_code = parse_clyp(clyp_code)
        assert 'if not (x > 0): return false' in python_code

    def test_guard_with_complex_condition(self):
        clyp_code = 'guard user != null && user.active else return "inactive";'
        python_code = parse_clyp(clyp_code)
        assert 'if not (user != null && user.active): return "inactive"' in python_code


class TestDestructuring:
    """Test destructuring assignment."""

    def test_array_destructuring(self):
        clyp_code = 'let [a, b, c] = array;'
        python_code = parse_clyp(clyp_code)
        assert 'a, b, c = array' in python_code

    def test_object_destructuring(self):
        clyp_code = 'let {name, age} = user;'
        python_code = parse_clyp(clyp_code)
        assert 'name, age = user' in python_code


class TestSpreadOperator:
    """Test spread operator syntax."""

    def test_array_spread(self):
        clyp_code = 'let combined = [1, 2, ...array, 3];'
        python_code = parse_clyp(clyp_code)
        assert '*array' in python_code

    def test_function_call_spread(self):
        clyp_code = 'let result = func(...args);'
        python_code = parse_clyp(clyp_code)
        assert 'func(*args)' in python_code


class TestPatternMatching:
    """Test pattern matching syntax."""

    def test_basic_match_statement(self):
        clyp_code = '''
        match value {
            when 1 => "one"
            when 2 => "two"
        }
        '''
        python_code = parse_clyp(clyp_code)
        assert 'match value:' in python_code
        assert 'case 1:' in python_code
        assert 'case 2:' in python_code

    def test_switch_expression(self):
        clyp_code = '''
        switch status {
            when "active" => processActive()
            when "inactive" => processInactive()
        }
        '''
        python_code = parse_clyp(clyp_code)
        assert 'match status:' in python_code


class TestExceptionHandling:
    """Test try/catch/finally syntax."""

    def test_try_catch_block(self):
        clyp_code = '''
        try {
            riskyOperation();
        }
        catch (Exception e) {
            handleError(e);
        }
        '''
        python_code = parse_clyp(clyp_code)
        assert 'try:' in python_code
        assert 'except Exception as e:' in python_code

    def test_try_finally_block(self):
        clyp_code = '''
        try {
            doSomething();
        }
        finally {
            cleanup();
        }
        '''
        python_code = parse_clyp(clyp_code)
        assert 'try:' in python_code
        assert 'finally:' in python_code


class TestTypeAliases:
    """Test type alias definitions."""

    def test_simple_type_alias(self):
        clyp_code = 'type UserId = int;'
        python_code = parse_clyp(clyp_code)
        assert 'UserId = int' in python_code

    def test_complex_type_alias(self):
        clyp_code = 'type UserData = Dict[str, Any];'
        python_code = parse_clyp(clyp_code)
        assert 'UserData = Dict[str, Any]' in python_code


class TestEnums:
    """Test enum definitions."""

    def test_simple_enum(self):
        clyp_code = 'enum Status { Active, Inactive, Pending }'
        python_code = parse_clyp(clyp_code)
        assert 'from enum import Enum' in python_code
        assert 'class Status(Enum):' in python_code
        assert 'Active = 1' in python_code
        assert 'Inactive = 2' in python_code
        assert 'Pending = 3' in python_code

    def test_multiline_enum(self):
        clyp_code = '''
        enum Color {
            Red,
            Green,
            Blue
        }
        '''
        python_code = parse_clyp(clyp_code)
        assert 'class Color(Enum):' in python_code


class TestOptionalTypes:
    """Test optional type annotations."""

    def test_optional_parameter_type(self):
        clyp_code = 'function test(int? value) returns bool { return true; }'
        python_code = parse_clyp(clyp_code)
        assert 'Optional[int]' in python_code

    def test_optional_in_method(self):
        clyp_code = '''
        class User {
            getName(str? prefix) returns str {
                return prefix + name;
            }
        }
        '''
        python_code = parse_clyp(clyp_code)
        assert 'Optional[str]' in python_code


class TestDefaultParameters:
    """Test default parameter values."""

    def test_function_with_defaults(self):
        clyp_code = 'function greet(str name = "World") returns str { return "Hello " + name; }'
        python_code = parse_clyp(clyp_code)
        assert 'name: str = "World"' in python_code

    def test_mixed_parameters(self):
        clyp_code = 'function process(str data, int count = 1, bool verbose = false) returns str { return data; }'
        python_code = parse_clyp(clyp_code)
        assert 'count: int = 1' in python_code
        assert 'verbose: bool = false' in python_code


class TestIntegrationFeatures:
    """Test combinations of multiple new features."""

    def test_lambda_with_optional_chaining(self):
        clyp_code = 'let names = users.map(user => user?.name ?? "Unknown");'
        python_code = parse_clyp(clyp_code)
        assert 'lambda user:' in python_code
        assert 'is not None' in python_code

    def test_destructuring_with_defaults(self):
        clyp_code = 'function process({name, age = 18}) returns str { return name; }'
        python_code = parse_clyp(clyp_code)
        # Should handle both destructuring and defaults
        assert 'name, age' in python_code

    def test_string_interpolation_with_optional_chaining(self):
        clyp_code = 'print("User: {user?.name ?? "Anonymous"}");'
        python_code = parse_clyp(clyp_code)
        assert 'f"User: {' in python_code

    def test_complex_feature_combination(self):
        clyp_code = '''
        function processUsers(users, str? prefix = null) returns List[str] {
            return users
                .filter(user => user?.active ?? false)
                .map(user => "{prefix ?? "User"}: {user.name}");
        }
        '''
        python_code = parse_clyp(clyp_code)
        # Should combine multiple features successfully
        assert 'Optional[str]' in python_code
        assert 'lambda user:' in python_code
        assert 'is not None' in python_code