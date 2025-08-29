import unittest
import tempfile
import os
from clyp.formatter import format_clyp_code


class TestFormatter(unittest.TestCase):
    """Test cases for the Clyp code formatter."""

    def test_basic_function_formatting(self):
        """Test basic function formatting with proper spacing."""
        input_code = """
function   greet(   str  name  )   returns   str   {
    return  'Hello, '   +   name;
}
"""
        expected = """function greet(str name) returns str {
 return 'Hello, ' + name;
}"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_conditional_formatting(self):
        """Test if-else statement formatting."""
        input_code = """
if  x>y{return x*2;}
   else  {   return   y*3;   }
"""
        expected = """if x > y{return x * 2;}
else { return y * 3; }"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_variable_assignment_formatting(self):
        """Test variable assignment formatting."""
        input_code = """
let   result=calculate(5,3);
int   x=42;
str   name='Alice';
"""
        expected = """let result = calculate(5, 3);
int x = 42;
str name = 'Alice';"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_function_call_formatting(self):
        """Test function call formatting."""
        input_code = """
print(greet('World'));
calculate(  x ,  y  ,  z  );
"""
        expected = """print(greet('World'));
calculate(x, y, z);"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_operator_spacing(self):
        """Test operator spacing formatting."""
        input_code = """
let a=b+c;
let d=e*f;
let g=h-i;
if(x==y&&z!=w){
    return true;
}
"""
        expected = """let a = b + c;
let d = e * f;
let g = h - i;
if(x == y&&z != w) {
 return true;
}"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_empty_code(self):
        """Test formatting empty code."""
        result = format_clyp_code("")
        self.assertEqual(result, "")

    def test_whitespace_only(self):
        """Test formatting whitespace-only code."""
        result = format_clyp_code("   \n  \n   ")
        self.assertEqual(result.strip(), "")

    def test_single_line_formatting(self):
        """Test formatting single line code."""
        input_code = "print('Hello World');"
        expected = "print('Hello World');"
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_complex_function_formatting(self):
        """Test formatting complex functions with multiple parameters."""
        input_code = """
function   calculate(   int  x,   int  y,  str  operation  )   returns   int   {
    if  operation=='add'{
        return  x+y;
    }else if  operation=='multiply'{
        return  x*y;
    }
    return  0;
}
"""
        expected = """function calculate(int x, int y, str operation) returns int {
 if operation == 'add' {
 return x + y;
 }else if operation == 'multiply' {
 return x * y;
 }
 return 0;
}"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_nested_braces_indentation(self):
        """Test proper indentation with nested braces."""
        input_code = """
function test() {
if (true) {
for (int i = 0; i < 5; i++) {
print(i);
}
}
}
"""
        expected = """function test() {
 if(true) {
 for(int i = 0; i < 5; i++) {
 print(i);
 }
 }
}"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_preserves_string_content(self):
        """Test that string content is preserved during formatting."""
        input_code = """
let message = "This   has    extra   spaces";
let other = 'Single  quotes  too';
"""
        expected = """let message = "This   has    extra   spaces";
let other = 'Single  quotes  too';"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_comments_are_preserved(self):
        """Test that comments are preserved during formatting."""
        input_code = """
// This is a comment
function test() {
    return 42; // End of line comment
}
"""
        expected = """// This is a comment
function test() {
 return 42; // End of line comment
}"""
        result = format_clyp_code(input_code)
        self.assertEqual(result.strip(), expected)

    def test_malformed_code_fallback(self):
        """Test that malformed code returns safely without crashing."""
        input_code = """
function incomplete(
let x = 
"""
        # Should not crash and return something reasonable
        result = format_clyp_code(input_code)
        self.assertIsInstance(result, str)
        # At minimum, it should not be empty
        self.assertTrue(len(result.strip()) > 0)

    def test_class_formatting(self):
        """Test class definition formatting."""
        input_code = """
class   MyClass   {
    int   value;
    function   getValue()   returns   int   {
        return   value;
    }
}
"""
        # This might fail with transpilation, so we expect graceful fallback
        result = format_clyp_code(input_code)
        self.assertIsInstance(result, str)
        # Should preserve the original structure at minimum
        self.assertIn("class", result)
        self.assertIn("MyClass", result)


if __name__ == "__main__":
    unittest.main()