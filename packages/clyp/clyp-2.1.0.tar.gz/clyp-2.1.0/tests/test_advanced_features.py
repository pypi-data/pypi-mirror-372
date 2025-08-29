import pytest
from clyp.transpiler import parse_clyp


class TestAdvancedFeatures:
    """Test additional advanced features for enhanced developer experience."""

    def test_arrow_functions_implicit_return(self):
        clyp_code = 'let double = x => x * 2;'
        python_code = parse_clyp(clyp_code)
        assert 'lambda x: x * 2' in python_code

    def test_arrow_functions_multi_param(self):
        clyp_code = 'let add = (a, b) => a + b;'
        python_code = parse_clyp(clyp_code)
        assert 'lambda a, b: a + b' in python_code

    def test_ternary_operator(self):
        clyp_code = 'let result = age >= 18 ? "adult" : "minor";'
        python_code = parse_clyp(clyp_code)
        assert '("adult" if age >= 18 else "minor")' in python_code

    def test_pipe_operator(self):
        clyp_code = 'let result = value |> double;'
        python_code = parse_clyp(clyp_code)
        assert 'double(value)' in python_code

    def test_compound_assignment_plus(self):
        clyp_code = 'counter += 1;'
        python_code = parse_clyp(clyp_code)
        assert 'counter = counter + 1' in python_code

    def test_compound_assignment_minus(self):
        clyp_code = 'balance -= amount;'
        python_code = parse_clyp(clyp_code)
        assert 'balance = balance - amount' in python_code

    def test_compound_assignment_multiply(self):
        clyp_code = 'score *= 2;'
        python_code = parse_clyp(clyp_code)
        assert 'score = score * 2' in python_code

    def test_compound_assignment_divide(self):
        clyp_code = 'value /= 10;'
        python_code = parse_clyp(clyp_code)
        assert 'value = value / 10' in python_code

    def test_compound_assignment_or_equals(self):
        clyp_code = 'name ||= "default";'
        python_code = parse_clyp(clyp_code)
        assert 'name = name if name is not None else "default"' in python_code

    def test_increment_postfix(self):
        clyp_code = 'counter++;'
        python_code = parse_clyp(clyp_code)
        assert 'counter = counter + 1' in python_code

    def test_increment_prefix(self):
        clyp_code = '++counter;'
        python_code = parse_clyp(clyp_code)
        assert 'counter = counter + 1' in python_code

    def test_decrement_postfix(self):
        clyp_code = 'counter--;'
        python_code = parse_clyp(clyp_code)
        assert 'counter = counter - 1' in python_code

    def test_decrement_prefix(self):
        clyp_code = '--counter;'
        python_code = parse_clyp(clyp_code)
        assert 'counter = counter - 1' in python_code

    def test_const_declaration(self):
        clyp_code = 'const PI = 3.14159;'
        python_code = parse_clyp(clyp_code)
        assert 'PI = 3.14159' in python_code
        assert '# const PI' in python_code

    def test_array_comprehension_simple(self):
        clyp_code = 'let squares = [x * x for x in numbers];'
        python_code = parse_clyp(clyp_code)
        assert 'squares = [x * x for x in numbers]' in python_code

    def test_array_comprehension_with_condition(self):
        clyp_code = 'let evens = [x for x in numbers if x % 2 == 0];'
        python_code = parse_clyp(clyp_code)
        assert 'evens = [x for x in numbers if x % 2 == 0]' in python_code

    def test_static_method(self):
        clyp_code = '''
        class Utils {
            static function format(str value) returns str {
                return value.upper();
            }
        }
        '''
        python_code = parse_clyp(clyp_code)
        assert '@staticmethod' in python_code
        assert 'def format(value: str) -> str:' in python_code

    def test_async_function(self):
        clyp_code = 'async function fetchData() returns str;'
        python_code = parse_clyp(clyp_code)
        assert 'async def fetchData() -> str:' in python_code

    def test_await_expression(self):
        clyp_code = 'let data = await fetchData();'
        python_code = parse_clyp(clyp_code)
        assert 'await fetchData()' in python_code


class TestNewStandardLibrary:
    """Test new standard library functions."""

    def test_pipe_function(self):
        from clyp.stdlib import pipe
        
        def double(x):
            return x * 2
        
        def add_one(x):
            return x + 1
        
        pipeline = pipe(double, add_one)
        result = pipeline(5)
        assert result == 11  # (5 * 2) + 1

    def test_compose_function(self):
        from clyp.stdlib import compose
        
        def double(x):
            return x * 2
        
        def add_one(x):
            return x + 1
        
        composition = compose(double, add_one)
        result = composition(5)
        assert result == 12  # (5 + 1) * 2

    def test_curry_function(self):
        from clyp.stdlib import curry
        
        @curry
        def add(a, b, c):
            return a + b + c
        
        # Can be called with all args
        assert add(1, 2, 3) == 6
        
        # Can be partially applied
        add_5 = add(5)
        assert add_5(2, 3) == 10
        
        add_5_2 = add(5)(2)
        assert add_5_2(3) == 10

    def test_tap_function(self):
        from clyp.stdlib import tap
        
        side_effects = []
        
        def log_value(x):
            side_effects.append(x)
        
        tapper = tap(log_value)
        result = tapper(42)
        
        assert result == 42
        assert side_effects == [42]

    def test_safe_get_dict(self):
        from clyp.stdlib import safe_get
        
        data = {"name": "Alice", "age": 30}
        
        assert safe_get(data, "name") == "Alice"
        assert safe_get(data, "missing") is None
        assert safe_get(data, "missing", "default") == "default"

    def test_safe_get_list(self):
        from clyp.stdlib import safe_get
        
        data = [1, 2, 3]
        
        assert safe_get(data, 0) == 1
        assert safe_get(data, 10) is None
        assert safe_get(data, 10, "default") == "default"

    def test_safe_call(self):
        from clyp.stdlib import safe_call
        
        def divide(a, b):
            return a / b
        
        assert safe_call(divide, 10, 2) == 5.0
        assert safe_call(divide, 10, 0) is None
        assert safe_call(divide, 10, 0, default="error") == "error"

    def test_chain_function(self):
        from clyp.stdlib import chain
        
        result = chain([1, 2], [3, 4], [5, 6])
        assert result == [1, 2, 3, 4, 5, 6]

    def test_take_function(self):
        from clyp.stdlib import take
        
        result = take(3, [1, 2, 3, 4, 5])
        assert result == [1, 2, 3]

    def test_drop_function(self):
        from clyp.stdlib import drop
        
        result = drop(2, [1, 2, 3, 4, 5])
        assert result == [3, 4, 5]

    def test_take_while_function(self):
        from clyp.stdlib import take_while
        
        result = take_while(lambda x: x < 5, [1, 2, 3, 4, 5, 6, 7])
        assert result == [1, 2, 3, 4]

    def test_drop_while_function(self):
        from clyp.stdlib import drop_while
        
        result = drop_while(lambda x: x < 5, [1, 2, 3, 4, 5, 6, 7])
        assert result == [5, 6, 7]

    def test_find_index_function(self):
        from clyp.stdlib import find_index
        
        result = find_index(lambda x: x > 3, [1, 2, 3, 4, 5])
        assert result == 3  # Index of 4
        
        result = find_index(lambda x: x > 10, [1, 2, 3, 4, 5])
        assert result == -1

    def test_count_by_function(self):
        from clyp.stdlib import count_by
        
        result = count_by(lambda x: x % 2 == 0, [1, 2, 3, 4, 5, 6])
        assert result == 3  # Three even numbers


class TestFeatureIntegration:
    """Test combinations of new features working together."""

    def test_arrow_functions_with_pipe(self):
        clyp_code = 'let result = value |> (x => x * 2);'
        python_code = parse_clyp(clyp_code)
        assert '(lambda x: x * 2)(value)' in python_code

    def test_ternary_with_null_coalescing(self):
        clyp_code = 'let message = user?.name ? "Hello " + user.name : name ?? "Anonymous";'
        python_code = parse_clyp(clyp_code)
        assert 'if' in python_code and 'else' in python_code
        assert 'is not None else' in python_code

    def test_array_comprehension_with_optional_chaining(self):
        clyp_code = 'let names = [user?.name for user in users if user?.active];'
        python_code = parse_clyp(clyp_code)
        assert 'for user in users' in python_code
        assert 'if' in python_code

    def test_const_with_compound_assignment(self):
        clyp_code = '''
        const MAX_COUNT = 100;
        let counter = 0;
        counter += 5;
        '''
        python_code = parse_clyp(clyp_code)
        assert '# const MAX_COUNT' in python_code
        assert 'counter = counter + 5' in python_code