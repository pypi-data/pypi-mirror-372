import re
from typing import List, Optional, Tuple
import clyp.stdlib as stdlib
from clyp import __version__

CURRENT_CLYP_VERSION = __version__



"""
Error Codes (see errors.md for full scheme):

| Code      | Description                                                        |
| --------- | ------------------------------------------------------------------ |
| A100      | Syntax error: <details>                                            |
| A101      | Python-style function definition detected on line <n>: '<code>'    |
| U500      | Major version mismatch: expected <major>, got <major>              |
| U501      | Minor version mismatch: expected <major>.<minor>, got <major>.<minor> |
| U502      | Patch version mismatch: expected <version>, got <version>          |
| W501      | Deprecated syntax 'repeat [times] times' on line <n>: '<code>'     |
"""

def get_builtin_names() -> set[str]:
    import builtins
    python_builtins = set(dir(builtins))
    clyp_builtins = set(
        name for name in dir(stdlib)
        if not name.startswith("_")
    )
    # Add Clyp constants/types
    clyp_constants = {"true", "false", "null"}
    clyp_types = {"int", "float", "str", "bool", "list", "dict", "any"}
    return python_builtins | clyp_builtins | clyp_constants | clyp_types

def colorize(msg: str) -> str:
    # ANSI color codes
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    if msg.startswith("ERROR"):
        prefix, rest = msg.split("]", 1)
        return f"{RED}{prefix}]{RESET}{rest}"
    elif msg.startswith("WARNING"):
        prefix, rest = msg.split("]", 1)
        return f"{YELLOW}{prefix}]{RESET}{rest}"
    return msg

def extract_version_info(clyp_code: str) -> Tuple[Optional[str], Optional[str]]:
    version_match = re.search(r"define\s+clyp_version\s+([0-9]+\.[0-9]+\.[0-9]+)", clyp_code)
    strictness_match = re.search(
        r"define\s+version_strictness\s+(major|minor|patch)", clyp_code
    )
    version = version_match.group(1) if version_match else None
    strictness = strictness_match.group(1) if strictness_match else None
    return version, strictness

def compare_versions(
    code_version: str, strictness: str, current_version: str
) -> Optional[str]:
    code_parts = [int(x) for x in code_version.split(".")]
    current_parts = [int(x) for x in current_version.split(".")]
    # Only warn when the current runtime is older than the version the
    # code requires. For example, if the code requires major 3 and the
    # runtime is major 2, warn. If the runtime is newer, it's compatible.
    if strictness == "major":
        if current_parts[0] < code_parts[0]:
            return (
                f"WARNING [ U500 ] Major version mismatch: "
                f"expected {code_parts[0]}, got {current_parts[0]}"
            )
    elif strictness == "minor":
        # Require the same major version, and current minor must be >= required
        # If majors differ at all, warn (even if runtime is newer).
        if current_parts[0] != code_parts[0] or current_parts[1] < code_parts[1]:
            return (
                f"WARNING [ U501 ] Minor version mismatch: "
                f"expected {code_parts[0]}.{code_parts[1]}, "
                f"got {current_parts[0]}.{current_parts[1]}"
            )
    elif strictness == "patch":
        # Require same major and minor, and current patch must be >= required
        # If major or minor differ at all, warn.
        if (
            current_parts[0] != code_parts[0]
            or current_parts[1] != code_parts[1]
            or current_parts[2] < code_parts[2]
        ):
            return (
                f"WARNING [ U502 ] Patch version mismatch: "
                f"expected {code_version}, got {current_version}"
            )
    return None

def precheck_clyp_code(clyp_code: str, verbose: bool = False) -> List[str]:
    if verbose:
        print("Starting to precheck Clyp code")
    errors: List[str] = []
    # --- Version check (before any other errors) ---
    code_version, strictness = extract_version_info(clyp_code)
    if code_version and strictness:
        warning = compare_versions(code_version, strictness, CURRENT_CLYP_VERSION)
        if warning:
            errors.append(colorize(warning))

    def_pattern = re.compile(r"^\s*def\s+\w+\s*\(.*\)\s*(returns\s+\w+)?\s*\{", re.MULTILINE)
    repeat_deprecated_pattern = re.compile(r"^\s*repeat\s*\[\s*\d+\s*\]\s+times\s*$", re.MULTILINE)
    assignment_pattern = re.compile(
        r"^\s*(\w+)\s*:\s*(int|float|str|bool|list|dict)\s*=\s*(.+)$"
    )
    int_literal_pattern = re.compile(r"^\d+$")
    float_literal_pattern = re.compile(r"^\d+\.\d+$")
    str_literal_pattern = re.compile(r"^\".*\"$|^'.*'$")
    bool_literal_pattern = re.compile(r"^(true|false)$", re.IGNORECASE)
    list_literal_pattern = re.compile(r"^\[.*\]$")
    dict_literal_pattern = re.compile(r"^\{.*\}$")

    # Add pattern for class method with 'self' argument
    class_method_self_pattern = re.compile(
        r"^\s*def\s+\w+\s*\(\s*self\s*(?:,|\))", re.MULTILINE
    )

    for i, line in enumerate(clyp_code.splitlines()):
        if def_pattern.match(line):
            errors.append(colorize(
                f"ERROR [ A101 ] Python-style function definition detected on line {i+1}: '{line.strip()}'\n"
                "💡 Tip: Use Clyp function syntax instead\n"
                "💡 Change: def func_name(args) -> return_type:\n"
                "💡 To: function func_name(args) returns return_type {{"
            ))
        if repeat_deprecated_pattern.match(line):
            errors.append(colorize(
                f"WARNING [ W501 ] Deprecated syntax 'repeat [times] times' on line {i+1}: '{line.strip()}'\n"
                "💡 Tip: Use modern Clyp repeat syntax instead\n"
                "💡 Change: repeat [n] times\n"
                "💡 To: repeat n {{ }}"
            ))
        assign_match = assignment_pattern.match(line)
        if assign_match:
            var_name, var_type, value = assign_match.groups()
            value = value.strip()
            if var_type == "int" and not int_literal_pattern.match(value):
                errors.append(colorize(
                    f"ERROR [ C100 ] Type error on line {i+1}: Expected int, got '{value}'\n"
                    "💡 Tip: Use integer literal (e.g., 42, 0, -10)\n"
                    "💡 Check for quotes around number or decimal points"
                ))
            elif var_type == "float" and not float_literal_pattern.match(value):
                errors.append(colorize(
                    f"ERROR [ C100 ] Type error on line {i+1}: Expected float, got '{value}'\n"
                    "💡 Tip: Use decimal number format (e.g., 3.14, 0.0, -2.5)\n"
                    "💡 Float literals must have decimal points"
                ))
            elif var_type == "str" and not str_literal_pattern.match(value):
                errors.append(colorize(
                    f"ERROR [ C100 ] Type error on line {i+1}: Expected str, got '{value}'\n"
                    "💡 Tip: String literals must be in quotes (e.g., \"hello\", 'world')\n"
                    "💡 Check for missing or unmatched quotes"
                ))
            elif var_type == "bool" and not bool_literal_pattern.match(value):
                errors.append(colorize(
                    f"ERROR [ C100 ] Type error on line {i+1}: Expected bool, got '{value}'\n"
                    "💡 Tip: Use boolean literals 'true' or 'false' (lowercase)\n"
                    "💡 Note: Clyp uses 'true'/'false', not 'True'/'False'"
                ))
            elif var_type == "list" and not list_literal_pattern.match(value):
                errors.append(colorize(
                    f"ERROR [ C101 ] Type error on line {i+1}: Expected list, got '{value}'\n"
                    "💡 Tip: Use list literal syntax [item1, item2, ...]\n"
                    "💡 Example: [1, 2, 3] or [\"a\", \"b\", \"c\"]"
                ))
            elif var_type == "dict" and not dict_literal_pattern.match(value):
                errors.append(colorize(
                    f"ERROR [ C102 ] Type error on line {i+1}: Expected dict, got '{value}'\n"
                    "💡 Tip: Use dictionary literal syntax {{key: value, ...}}\n"
                    "💡 Example: {{\"name\": \"John\", \"age\": 30}}"
                ))
        # Check for explicit 'self' argument in class methods
        if class_method_self_pattern.match(line):
            errors.append(colorize(
                f"ERROR [ L100 ] 'self' argument should not be defined explicitly in class methods (line {i+1})\n"
                "💡 Tip: Clyp automatically provides 'self' in class methods\n"
                "💡 Change: function myMethod(self, int x) returns str\n"
                "💡 To: function myMethod(int x) returns str"
            ))
    return errors

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m clyp.precheck <file.clyp>")
        sys.exit(1)
    file_path = sys.argv[1]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            clyp_code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    errors = precheck_clyp_code(clyp_code)
    if errors:
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("Precheck passed: no errors found.")
