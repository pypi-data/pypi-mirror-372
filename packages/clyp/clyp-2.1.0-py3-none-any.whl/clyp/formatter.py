import black
import re
from .transpiler import parse_clyp, transpile_to_clyp


def _normalize_clyp_spacing(clyp_code: str) -> str:
    """
    Simple Clyp code formatter that normalizes spacing and indentation
    without going through the full transpilation cycle.
    """
    lines = clyp_code.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            formatted_lines.append('')
            continue
        
        # Handle closing braces - decrease indent before the line
        if stripped.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        # Apply indentation
        formatted_line = '    ' * indent_level + stripped
        
        # Split line into string and non-string parts to protect string content
        parts = []
        current_part = ""
        in_string = False
        string_char = None
        i = 0
        
        while i < len(formatted_line):
            char = formatted_line[i]
            
            if not in_string and char in ('"', "'"):
                # Start of string
                if current_part:
                    parts.append(('code', current_part))
                current_part = char
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                # End of string (handle escaping)
                current_part += char
                if i > 0 and formatted_line[i-1] != '\\':
                    parts.append(('string', current_part))
                    current_part = ""
                    in_string = False
                    string_char = None
            else:
                current_part += char
            
            i += 1
        
        # Handle remaining content
        if current_part:
            if in_string:
                parts.append(('string', current_part))
            else:
                parts.append(('code', current_part))
        
        # Process each part separately
        processed_parts = []
        for part_type, content in parts:
            if part_type == 'string':
                # Don't modify string content
                processed_parts.append(content)
            else:
                # Apply formatting to code parts only
                processed_content = content
                
                # Handle function signature spacing
                processed_content = re.sub(r'function\s+(\w+)\s*\(', r'function \1(', processed_content)
                processed_content = re.sub(r'\)\s*returns\s+', r') returns ', processed_content)
                processed_content = re.sub(r'returns\s+(\w+)\s*{', r'returns \1 {', processed_content)
                
                # Clean up common spacing issues
                processed_content = re.sub(r'\s*{\s*$', ' {', processed_content)  # normalize brace spacing
                processed_content = re.sub(r'\s*;\s*$', ';', processed_content)   # normalize semicolon spacing
                processed_content = re.sub(r'\s*,\s*', ', ', processed_content)   # normalize comma spacing
                
                # Normalize parentheses - be careful not to affect function calls
                processed_content = re.sub(r'(\w)\s*\(', r'\1(', processed_content)  # function calls
                processed_content = re.sub(r'\(\s+', '(', processed_content)         # opening parenthesis
                processed_content = re.sub(r'\s+\)', ')', processed_content)         # closing parenthesis
                
                # Add operator spacing - be more careful with regex
                # Handle assignment - check for = at end of part or with following character
                processed_content = re.sub(r'(\w)\s*=\s*$', r'\1 = ', processed_content)            # assignment at end
                processed_content = re.sub(r'(\w)\s*=\s*([^=])', r'\1 = \2', processed_content)      # assignment with following char
                # Handle equality comparison
                processed_content = re.sub(r'(\w)\s*==\s*$', r'\1 == ', processed_content)           # equality at end
                processed_content = re.sub(r'(\w)\s*==\s*([^=])', r'\1 == \2', processed_content)    # equality with following char
                processed_content = re.sub(r'(\w)\s*!=\s*$', r'\1 != ', processed_content)           # inequality at end
                processed_content = re.sub(r'(\w)\s*!=\s*([^=])', r'\1 != \2', processed_content)    # inequality with following char
                processed_content = re.sub(r'(\w)\s*<=\s*(\w)', r'\1 <= \2', processed_content)      # less than or equal
                processed_content = re.sub(r'(\w)\s*>=\s*(\w)', r'\1 >= \2', processed_content)      # greater than or equal
                processed_content = re.sub(r'(\w)\s*<\s*(\w)', r'\1 < \2', processed_content)        # less than
                processed_content = re.sub(r'(\w)\s*>\s*(\w)', r'\1 > \2', processed_content)        # greater than
                processed_content = re.sub(r'(\w)\s*\+\s*(\w)', r'\1 + \2', processed_content)       # addition
                processed_content = re.sub(r'(\w)\s*-\s*(\w)', r'\1 - \2', processed_content)        # subtraction
                processed_content = re.sub(r'(\w)\s*\*\s*(\w)', r'\1 * \2', processed_content)       # multiplication
                
                # Clean up multiple spaces only in code sections
                processed_content = re.sub(r'\s+', ' ', processed_content)
                
                processed_parts.append(processed_content)
        
        formatted_line = ''.join(processed_parts)
        formatted_lines.append(formatted_line)
        
        # Handle opening braces - increase indent after the line
        if stripped.endswith('{'):
            indent_level += 1
    
    return '\n'.join(formatted_lines)


def _extract_user_code_from_python(python_code: str) -> str:
    """
    Extract only the user's code from the Python code generated by parse_clyp,
    removing the boilerplate imports and setup.
    """
    lines = python_code.split('\n')
    user_code_lines = []
    
    # Skip boilerplate lines
    skip_patterns = [
        r'from typeguard import',
        r'install_import_hook',
        r'import gc',
        r'gc\.enable',
        r'del gc',
        r'import clyp',
        r'from clyp\.importer import',
        r'from clyp\.stdlib import',
        r'import clyp\.stdlib',
        r'del clyp',
        r'true = True; false = False; null = None'
    ]
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            user_code_lines.append(line)
            continue
        
        # Check if this line matches any skip pattern
        should_skip = False
        for pattern in skip_patterns:
            if re.search(pattern, stripped):
                should_skip = True
                break
        
        if not should_skip:
            user_code_lines.append(line)
    
    return '\n'.join(user_code_lines).strip()


def _extract_user_code_from_clyp(clyp_code: str) -> str:
    """
    Extract only the user's code from the Clyp code generated by transpile_to_clyp,
    removing the boilerplate comments and assignments.
    """
    lines = clyp_code.split('\n')
    user_code_lines = []
    
    # Skip boilerplate lines
    skip_patterns = [
        r'^// from typeguard import',
        r'^install_import_hook\(\);$',
        r'^// import gc$',
        r'^gc\.enable\(\);$',
        r'^// import clyp$',
        r'^// from clyp\.importer import',
        r'^// from clyp\.stdlib import',
        r'^true = True;$',
        r'^false = False;$',
        r'^null = None;$'
    ]
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            user_code_lines.append(line)
            continue
        
        # Check if this line matches any skip pattern
        should_skip = False
        for pattern in skip_patterns:
            if re.search(pattern, stripped):
                should_skip = True
                break
        
        if not should_skip:
            user_code_lines.append(line)
    
    return '\n'.join(user_code_lines).strip()


def format_clyp_code(clyp_code: str) -> str:
    """
    Formats Clyp code using a combination of direct syntax formatting
    and transpilation-based formatting for more complex cases.

    Args:
        clyp_code: The Clyp code to format.

    Returns:
        The formatted Clyp code.
    """
    # First try simple direct formatting
    try:
        simple_formatted = _normalize_clyp_spacing(clyp_code)
        return simple_formatted
    except Exception:
        pass
    
    # Fallback to transpilation-based formatting for complex cases
    try:
        # Transpile Clyp to Python
        python_code = parse_clyp(clyp_code)
        if not isinstance(python_code, str):
            # If parse_clyp returns a tuple, extract the string part
            python_code = python_code[0]

        # Extract only user code from the generated Python
        user_python_code = _extract_user_code_from_python(python_code)

        # Format the Python code using black
        try:
            formatted_python_code = black.format_str(user_python_code, mode=black.FileMode())
        except Exception:
            formatted_python_code = user_python_code

        # Transpile the formatted Python back to Clyp
        formatted_clyp_code = transpile_to_clyp(formatted_python_code)

        # Extract only user code from the generated Clyp
        formatted_user_clyp_code = _extract_user_code_from_clyp(formatted_clyp_code)

        return formatted_user_clyp_code
    except Exception:
        # If all formatting fails, return the original code
        return clyp_code
