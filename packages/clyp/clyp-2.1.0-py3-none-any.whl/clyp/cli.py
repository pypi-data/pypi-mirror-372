import sys
import os
import json
import traceback
import shutil
import re
from typing import Optional, Tuple, Dict, List, Any
from clyp import __version__
from clyp.transpiler import parse_clyp, transpile_to_clyp
from clyp.formatter import format_clyp_code
from .importer import find_clyp_imports

# Error code mapping (see errors.md)
ERROR_CODE_MAP = {
    # Syntax errors
    "SyntaxError": "A100",
    "IndentationError": "A100",
    "TabError": "A100",
    # Lexical errors (no direct Python mapping)
    # Type errors
    "TypeError": "C100",
    "OverflowError": "C100",
    # Runtime errors
    "RuntimeError": "D100",
    "RecursionError": "D100",
    "ZeroDivisionError": "D101",
    "ArithmeticError": "D100",
    "FloatingPointError": "D100",
    "SystemExit": "D100",
    "KeyboardInterrupt": "D100",
    "StopIteration": "D100",
    "StopAsyncIteration": "D100",
    # Import/module errors
    "ImportError": "E100",
    "ModuleNotFoundError": "E100",
    # File system errors
    "FileNotFoundError": "F100",
    "OSError": "F101",
    "IsADirectoryError": "F101",
    "NotADirectoryError": "F101",
    "PermissionError": "P100",
    # IO errors
    "IOError": "G100",
    "BlockingIOError": "G100",
    "ChildProcessError": "G100",
    "ConnectionError": "G100",
    "ConnectionAbortedError": "G100",
    "ConnectionRefusedError": "G100",
    "ConnectionResetError": "G100",
    "BrokenPipeError": "G100",
    "TimeoutError": "Q100",
    # Semantic errors
    "AssertionError": "H100",
    # Deprecation warnings
    "DeprecationWarning": "I100",
    "PendingDeprecationWarning": "I100",
    "FutureWarning": "I100",
    # Compiler internal errors
    "NotImplementedError": "J100",
    # Argument errors
    # Scope errors
    "AttributeError": "M100",
    "KeyError": "M101",
    "UnboundLocalError": "M100",
    # Name errors
    "NameError": "N100",
    # Optimization warnings (no direct Python mapping)
    # Permission errors (see above)
    # Concurrency errors
    "BrokenProcessPool": "Q100",
    # Memory errors
    "MemoryError": "R100",
    # Security errors
    # Transform errors
    # Versioning errors
    # Validation errors
    "ValueError": "V100",
    "UnicodeError": "V100",
    "UnicodeDecodeError": "V100",
    "UnicodeEncodeError": "V100",
    "UnicodeTranslateError": "V100",
    # Warning-level notices
    "Warning": "W501",
    "UserWarning": "W501",
    "ResourceWarning": "W501",
    "SyntaxWarning": "W501",
    "ImportWarning": "W501",
    "BytesWarning": "W501",
    "EncodingWarning": "W501",
    # Experimental feature fails
    # Language feature errors
    # Unknown/unclassified
    # Custom Clyp errors
    "ClypSyntaxError": "A100",
    "ClypTypeError": "C100",
    "ClypImportError": "E100",
    "ClypRuntimeError": "D100",
    "ClypValidationError": "V100",
    "ClypVersionError": "U500",
    "ClypDeprecationWarning": "W501",
}

def get_error_code(exc: Exception) -> str:
    """
    Map an exception to an error code string based on ERROR_CODE_MAP.
    Returns 'Z999' for unknown exceptions.
    """
    name = exc.__class__.__name__
    return ERROR_CODE_MAP.get(name, 'Z999')

class Log:
    """A simple logger with color support."""
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    _supports_color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    @classmethod
    def _print(cls, color, *args, **kwargs):
        msg = "".join(map(str, args))
        if cls._supports_color:
            print(f"{color}{msg}{cls.ENDC}", **kwargs)
        else:
            print(msg, **kwargs)
    @classmethod
    def info(cls, *args, **kwargs):
        cls._print(cls.CYAN, *args, **kwargs)
    @classmethod
    def success(cls, *args, **kwargs):
        cls._print(cls.GREEN, *args, **kwargs)
    @classmethod
    def warn(cls, *args, **kwargs):
        cls._print(cls.WARNING, *args, **kwargs)
    @classmethod
    def error(cls, *args, **kwargs):
        cls._print(cls.FAIL, *args, **kwargs)
    @classmethod
    def bold(cls, *args, **kwargs):
        msg = "".join(map(str, args))
        if cls._supports_color:
            print(f"{cls.BOLD}{msg}{cls.ENDC}", **kwargs)
        else:
            print(msg, **kwargs)
    @classmethod
    def traceback_header(cls, *args, **kwargs):
        cls._print(cls.BOLD, *args, **kwargs)
    @classmethod
    def traceback_location(cls, *args, **kwargs):
        cls._print(cls.BLUE, *args, **kwargs)
    @classmethod
    def traceback_code(cls, *args, **kwargs):
        cls._print(cls.CYAN, *args, **kwargs)

# Helper functions (move to top-level)
def get_clyp_line_for_py(
    py_line: int,
    line_map: Optional[Dict[int, int]],
    clyp_lines: Optional[List[str]],
) -> Tuple[Any, str]:
    # If we don't have mapping or source lines, return unknown
    if not line_map or not clyp_lines:
        return "?", ""
    # Try direct mapping first (exact python line -> clyp line)
    if py_line in line_map:
        clyp_line = line_map[py_line]
    else:
        # fall back to the nearest preceding mapping key (largest key <= py_line)
        keys = sorted(line_map.keys())
        prev_key = None
        for k in keys:
            if k <= py_line:
                prev_key = k
            else:
                break
        if prev_key is not None:
            clyp_line = line_map[prev_key]
        else:
            # no preceding mapping; use first mapped location as best-effort
            try:
                clyp_line = line_map[keys[0]]
            except Exception:
                return "?", ""
    # Normalize and bound-check the resulting clyp line
    try:
        if isinstance(clyp_line, int) and 1 <= clyp_line <= len(clyp_lines):
            return clyp_line, clyp_lines[clyp_line - 1]
    except Exception:
        pass
    # fallback: show last available line if any
    if clyp_lines:
        return len(clyp_lines), clyp_lines[-1]
    return "?", ""



# Add global verbose flag
VERBOSE = False

# Clyp.json configuration handling
def parse_json5(content: str) -> Dict[str, Any]:
    """Parse JSON5 format (JSON with comments and trailing commas)."""
    import re
    
    # Remove line comments (// ...) but preserve them in strings
    lines = content.split('\n')
    processed_lines = []
    for line in lines:
        # Simple check - if we're not in a string, remove comments
        in_string = False
        escaped = False
        comment_pos = len(line)
        
        for i, char in enumerate(line):
            if escaped:
                escaped = False
                continue
            if char == '\\':
                escaped = True
                continue
            if char == '"' and not escaped:
                in_string = not in_string
                continue
            if not in_string and char == '/' and i + 1 < len(line) and line[i + 1] == '/':
                comment_pos = i
                break
        
        processed_lines.append(line[:comment_pos].rstrip())
    
    content = '\n'.join(processed_lines)
    
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove trailing commas (but be careful with arrays/objects)
    content = re.sub(r',(\s*[}\]])', r'\1', content)
    
    # Parse as regular JSON
    return json.loads(content)

def load_clyp_config(config_path: str) -> Optional[Dict[str, Any]]:
    """Load and validate clyp.json configuration file."""
    try:
        if not os.path.exists(config_path):
            return None
        
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Try JSON5 parsing first, fall back to regular JSON
        try:
            config = parse_json5(content)
        except json.JSONDecodeError:
            try:
                config = json.loads(content)
            except json.JSONDecodeError as e:
                Log.error(f"[V100] Invalid JSON in clyp.json: {e}")
                Log.info("💡 Tip: Check for syntax errors like missing commas or quotes", file=sys.stderr)
                Log.info("💡 Note: clyp.json supports JSON5 format (comments and trailing commas)", file=sys.stderr)
                return None
        
        # Basic validation
        if not isinstance(config, dict):
            Log.error(f"[V100] Invalid clyp.json: Root must be an object.")
            return None
            
        # Validate required fields
        if "name" not in config:
            Log.warn("[V101] clyp.json missing 'name' field")
        if "version" not in config:
            Log.warn("[V102] clyp.json missing 'version' field")
        if "entry" not in config and "main" not in config:
            Log.warn("[V103] clyp.json missing 'entry' or 'main' field")
            
        return config
        
    except Exception as e:
        code = get_error_code(e)
        Log.error(f"[{code}] Error reading clyp.json: {e}")
        return None

def get_project_config(project_dir: str = None) -> Optional[Dict[str, Any]]:
    """Find and load the nearest clyp.json configuration."""
    try:
        if project_dir is None:
            project_dir = os.getcwd()
    except (OSError, FileNotFoundError):
        # Handle case where current directory doesn't exist
        if project_dir is None:
            return None
    
    # Look for clyp.json in current directory and parent directories
    current_dir = os.path.abspath(project_dir)
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        config_path = os.path.join(current_dir, "clyp.json")
        if os.path.exists(config_path):
            if VERBOSE:
                Log.info(f"Found clyp.json at: {config_path}")
            return load_clyp_config(config_path)
        current_dir = os.path.dirname(current_dir)
    
    return None

def resolve_config_path(file_path: str, config: Dict[str, Any]) -> str:
    """Resolve a path relative to the clyp.json location."""
    if os.path.isabs(file_path):
        return file_path
    
    # Find the directory containing clyp.json
    config_dir = os.getcwd()
    current_dir = os.path.abspath(config_dir)
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, "clyp.json")):
            config_dir = current_dir
            break
        current_dir = os.path.dirname(current_dir)
    
    return os.path.join(config_dir, file_path)

def run_project_script(script_name: str, config: Dict[str, Any]) -> bool:
    """Run a script defined in clyp.json scripts section."""
    scripts = config.get("scripts", {})
    if script_name not in scripts:
        Log.error(f"Script '{script_name}' not found in clyp.json")
        available = list(scripts.keys())
        if available:
            Log.info(f"💡 Available scripts: {', '.join(available)}")
        return False
    
    script_command = scripts[script_name]
    Log.info(f"Running script '{script_name}': {script_command}")
    
    # Execute the script command
    import subprocess
    try:
        result = subprocess.run(script_command, shell=True, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        Log.error(f"Script '{script_name}' failed with exit code {e.returncode}")
        return False
    except Exception as e:
        code = get_error_code(e)
        Log.error(f"[{code}] Error running script '{script_name}': {e}")
        return False

def save_clyp_config(config: Dict[str, Any], config_path: str) -> bool:
    """Save clyp.json configuration to file."""
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        code = get_error_code(e)
        Log.error(f"[{code}] Error saving clyp.json: {e}")
        return False

def add_dependency(dep_spec: str, config: Dict[str, Any], config_path: str, is_dev: bool = False) -> bool:
    """Add a dependency to clyp.json."""
    # Parse dependency specification (name@version or just name)
    if "@" in dep_spec:
        name, version = dep_spec.split("@", 1)
    else:
        name = dep_spec
        version = "*"  # Latest version
    
    # Determine which dependencies section to use
    deps_key = "devDependencies" if is_dev else "dependencies"
    if deps_key not in config:
        config[deps_key] = {}
    
    # Add the dependency
    config[deps_key][name] = version
    
    # Save the updated config
    if save_clyp_config(config, config_path):
        dep_type = "development " if is_dev else ""
        Log.success(f"Added {dep_type}dependency: {name}@{version}")
        return True
    return False

def remove_dependency(dep_name: str, config: Dict[str, Any], config_path: str, is_dev: bool = False) -> bool:
    """Remove a dependency from clyp.json."""
    deps_key = "devDependencies" if is_dev else "dependencies"
    
    if deps_key not in config or dep_name not in config[deps_key]:
        dep_type = "development " if is_dev else ""
        Log.error(f"{dep_type}dependency '{dep_name}' not found")
        return False
    
    # Remove the dependency
    del config[deps_key][dep_name]
    
    # Save the updated config
    if save_clyp_config(config, config_path):
        dep_type = "development " if is_dev else ""
        Log.success(f"Removed {dep_type}dependency: {dep_name}")
        return True
    return False

def find_config_file(start_dir: Optional[str] = None) -> Optional[str]:
    """Find the nearest clyp.json file."""
    current_dir = start_dir or os.getcwd()
    current_dir = os.path.abspath(current_dir)
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        config_path = os.path.join(current_dir, "clyp.json")
        if os.path.exists(config_path):
            return config_path
        current_dir = os.path.dirname(current_dir)
    return None

def resolve_project_entry_point(directory_path: str) -> Optional[str]:
    """Resolve the entry point file for a directory project with clyp.json."""
    config_path = os.path.join(directory_path, "clyp.json")
    if not os.path.exists(config_path):
        return None
    
    config = load_clyp_config(config_path)
    if not config:
        return None
    
    # Try 'entry' first, then 'main' for compatibility
    entry_point = config.get("entry") or config.get("main")
    if not entry_point:
        return None
    
    # Resolve entry point relative to the directory containing clyp.json
    entry_path = os.path.join(directory_path, entry_point)
    if os.path.exists(entry_path):
        return os.path.abspath(entry_path)
    
    return None

def resolve_input_path(input_path: str) -> Tuple[str, bool]:
    """
    Resolve input path to actual file to process.
    Returns (resolved_path, is_directory_project)
    """
    abs_path = os.path.abspath(input_path)
    
    # If it's a file, return as-is
    if os.path.isfile(abs_path):
        return abs_path, False
    
    # If it's a directory, check for clyp.json and resolve entry point
    if os.path.isdir(abs_path):
        entry_point = resolve_project_entry_point(abs_path)
        if entry_point:
            return entry_point, True
        else:
            # No clyp.json or no entry point, treat as regular directory
            return abs_path, False
    
    # Path doesn't exist
    return abs_path, False

def python_to_clyp_transpile(py_code):
    # Log when transpiler is invoked if verbose
    if VERBOSE:
        Log.info("Transpiler: starting transpile_to_clyp()")
    result = transpile_to_clyp(py_code)
    if VERBOSE:
        Log.info("Transpiler: finished transpile_to_clyp()")
    return result

def remove_dirs(root, dirs):
    for d in dirs:
        path = os.path.join(root, d)
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            Log.success(f"Removed {path}")

def print_deps(file_path, seen=None, level=0):
    if seen is None:
        seen = set()
    abs_path = os.path.abspath(file_path)
    if abs_path in seen:
        print("  " * level + f"- {os.path.basename(file_path)} (already shown)")
        return
    seen.add(abs_path)
    print("  " * level + f"- {os.path.basename(file_path)}")
    try:
        imports = find_clyp_imports(abs_path)
        if VERBOSE:
            Log.info(f"print_deps: found imports for {file_path}: {imports}")
        for imp in imports:
            # Verbose: detect std / stdlib style imports
            if VERBOSE and (imp.startswith("std") or imp.startswith("stdlib")):
                Log.info(f"Detected standard library import: {imp}")
            resolved = resolve_import_path(imp, abs_path)
            if VERBOSE:
                Log.info(f"Resolved import '{imp}' -> {resolved}")
            if resolved:
                print_deps(resolved, seen, level + 1)
    except Exception as e:
        print("  " * (level + 1) + f"[error: {e}]")



def resolve_import_path(import_name, current_file_path):
    """Resolves the absolute path of a Clyp import."""
    module_path = import_name.replace(".", os.path.sep) + ".clyp"
    search_paths = [os.path.dirname(current_file_path)] + sys.path
    if VERBOSE:
        Log.info(f"resolve_import_path: resolving {import_name} from {current_file_path}")
        Log.info(f"resolve_import_path: search_paths={search_paths}")
    for path in search_paths:
        potential_path = os.path.join(path, module_path)
        if os.path.exists(potential_path):
            if VERBOSE:
                Log.info(f"resolve_import_path: found {potential_path}")
            return os.path.abspath(potential_path)
    if VERBOSE:
        Log.info(f"resolve_import_path: could not resolve {import_name}")
    return None

# Main entry point
def main():
    import argparse
    # print(sys.argv)  # (optional: remove debug print)
    parser = argparse.ArgumentParser(
        description="Clyp CLI tool (interpreted mode only).",
        epilog="Examples:\n"
        "  clyp run hello.clyp          # Run a Clyp file\n"
        "  clyp run my-project/         # Run a directory project\n"
        "  clyp init my-project         # Create a new Clyp project\n"
        "  clyp format main.clyp        # Format Clyp code\n"
        "  clyp format src/             # Format all files in directory\n"
        "  clyp py2clyp script.py       # Convert Python to Clyp\n"
        "  clyp check .                 # Check project for errors\n"
        "  clyp deps main.clyp          # Show dependency tree\n"
        "  clyp deps my-project/        # Show dependencies for project\n"
        "  clyp script build            # Run a script from clyp.json\n"
        "  clyp config --validate       # Validate clyp.json configuration\n"
        "  clyp add math@1.0.0          # Add a dependency\n"
        "  clyp remove math             # Remove a dependency",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # Add global verbose flag
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument("--version", action="store_true", help="Display the version of Clyp.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    # Only keep run, format, py2clyp, check, deps, init commands
    run_parser = subparsers.add_parser("run", help="Run a Clyp file or directory project. Example: clyp run hello.clyp")
    run_parser.add_argument("file", type=str, help="Path to the Clyp file or project directory to execute.")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the Clyp script.")
    format_parser = subparsers.add_parser("format", help="Format Clyp files or directories. Example: clyp format main.clyp")
    format_parser.add_argument("file", type=str, help="Path to the Clyp file or directory to format.")
    format_parser.add_argument("--print", action="store_true", help="Print formatted code instead of overwriting.")
    format_parser.add_argument("--no-write", action="store_true", help="Do not overwrite the file (alias for --print).")
    py2clyp_parser = subparsers.add_parser("py2clyp", help="Transpile Python code to Clyp. Example: clyp py2clyp script.py")
    py2clyp_parser.add_argument("file", type=str, help="Path to the Python file to transpile.")
    py2clyp_parser.add_argument("-o", "--output", type=str, default=None, help="Output file for Clyp code.")
    py2clyp_parser.add_argument("--print", action="store_true", help="Print transpiled Clyp code to stdout.")
    py2clyp_parser.add_argument("--format", action="store_true", help="Format the output Clyp code.")
    py2clyp_parser.add_argument("--diff", action="store_true", help="Show a diff between the Python and Clyp code.")
    py2clyp_parser.add_argument("--overwrite", action="store_true", help="Overwrite the input Python file with Clyp code.")
    py2clyp_parser.add_argument("--check", action="store_true", help="Check if the file can be transpiled (dry run, no output).")
    py2clyp_parser.add_argument("--quiet", action="store_true", help="Suppress non-error output.")
    py2clyp_parser.add_argument("--no-format", action="store_true", help="Do not format the output.")
    py2clyp_parser.add_argument("--stats", action="store_true", help="Show statistics about the transpilation (lines, tokens, etc.).")
    py2clyp_parser.add_argument("-r", "--recursive", action="store_true", help="Recursively transpile a directory of Python files.")
    check_parser = subparsers.add_parser("check", help="Check Clyp files or directories for syntax errors. Example: clyp check main.clyp")
    check_parser.add_argument("file", type=str, nargs="?", default=None, help="Clyp file or directory to check. If omitted, checks the current directory.")
    deps_parser = subparsers.add_parser("deps", help="Show the dependency tree for a Clyp file or project. Example: clyp deps main.clyp")
    deps_parser.add_argument("file", type=str, nargs="?", default=None, help="Clyp file or project directory to analyze.")
    init_parser = subparsers.add_parser("init", help="Initialize a new Clyp project. Example: clyp init my-project")
    init_parser.add_argument("name", type=str, help="The name of the project.")
    init_parser.add_argument("--template", type=str, default="default", help="Project template (default, library, web).")
    
    # Add script command
    script_parser = subparsers.add_parser("script", help="Run a script defined in clyp.json. Example: clyp script build")
    script_parser.add_argument("name", type=str, help="Name of the script to run.")
    
    # Add config command
    config_parser = subparsers.add_parser("config", help="Show or validate clyp.json configuration. Example: clyp config")
    config_parser.add_argument("--validate", action="store_true", help="Validate clyp.json format and structure.")
    config_parser.add_argument("--show", action="store_true", help="Show the current configuration.")
    
    # Add dependency management commands
    add_parser = subparsers.add_parser("add", help="Add a dependency to clyp.json. Example: clyp add math@1.0.0")
    add_parser.add_argument("dependency", type=str, help="Dependency name[@version] to add.")
    add_parser.add_argument("--dev", action="store_true", help="Add as development dependency.")
    
    remove_parser = subparsers.add_parser("remove", help="Remove a dependency from clyp.json. Example: clyp remove math")
    remove_parser.add_argument("dependency", type=str, help="Dependency name to remove.")
    remove_parser.add_argument("--dev", action="store_true", help="Remove from development dependencies.")
    
    args = parser.parse_args()
    # ... existing code ...

    # Activate global verbose flag for use in helper functions
    global VERBOSE
    VERBOSE = bool(getattr(args, "verbose", False))
    if VERBOSE:
        Log.info(f"Verbose mode enabled. Command: {args.command} args={sys.argv[1:]}")

    if args.version:
        print(f"{__version__}")
        sys.exit(0)

    if args.command == "run":
        # Resolve input path - could be a file or directory project
        resolved_path, is_directory_project = resolve_input_path(args.file)
        
        # Check if resolved path exists
        if not os.path.exists(resolved_path):
            if is_directory_project:
                Log.error(f"[F100] Entry point file not found: {resolved_path}", file=sys.stderr)
                Log.info("💡 Tip: Check the 'entry' field in your clyp.json file.", file=sys.stderr)
            else:
                Log.error(f"[F100] File or directory not found: {args.file}", file=sys.stderr)
                if os.path.isdir(args.file):
                    Log.info("💡 Tip: Directory found but no clyp.json with entry point. Create a clyp.json file or specify a .clyp file.", file=sys.stderr)
                else:
                    Log.info("💡 Tip: Check the file path and make sure the file exists.", file=sys.stderr)
            sys.exit(1)
        
        file_path = resolved_path
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                clyp_code = f.read()
        except FileNotFoundError as e:
            code = get_error_code(e)
            Log.error(f"[{code}] File {file_path} not found.", file=sys.stderr)
            Log.info("💡 Tip: Check the file path and make sure the file exists.", file=sys.stderr)
            sys.exit(1)
        except (IOError, UnicodeDecodeError) as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Error reading file {args.file}: {e}", file=sys.stderr)
            if isinstance(e, UnicodeDecodeError):
                Log.info("💡 Tip: Make sure the file is saved with UTF-8 encoding.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Unexpected error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        # --- Run precheck before executing ---
        from clyp.precheck import precheck_clyp_code
        if VERBOSE:
            Log.info("Precheck: starting precheck_clyp_code()")
        precheck_errors = precheck_clyp_code(clyp_code)
        if VERBOSE:
            Log.info(f"Precheck: finished precheck_clyp_code(); errors={precheck_errors}")
        if precheck_errors:
            for err in precheck_errors:
                print(err, file=sys.stderr)
            sys.exit(1)
        try:
            if VERBOSE:
                Log.info("Calling parse_clyp(..., return_line_map=True)")
            result = parse_clyp(clyp_code, file_path, return_line_map=True)
            if VERBOSE:
                Log.info("parse_clyp returned successfully")
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] {type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
        if isinstance(result, tuple):
            python_code, line_map, clyp_lines = result
        else:
            python_code = result
            line_map = None
            clyp_lines = None
        # Verbose: show input and output code
        if VERBOSE:
            Log.info("=== INPUT CLYP CODE ===")
            print(clyp_code)
            Log.info("=== GENERATED PYTHON CODE ===")
            print(python_code)
        sys.argv = [file_path] + (args.args if hasattr(args, "args") else [])
        try:
            exec(python_code, {"__name__": "__main__", "__file__": file_path})
        except SyntaxError as e:
            code = get_error_code(e)
            py_line = e.lineno or 1
            Log.traceback_header("\nTraceback (most recent call last):", file=sys.stderr)
            clyp_line, code_line = get_clyp_line_for_py(py_line, line_map, clyp_lines)
            Log.traceback_location(f"  File '{args.file}', line {clyp_line}", file=sys.stderr)
            # If we can show Clyp context, show surrounding lines with pointer
            if clyp_lines and clyp_line != "?":
                start = max(0, clyp_line - 3)
                end = min(len(clyp_lines), clyp_line + 2)
                for i in range(start, end):
                    pointer = "->" if (i + 1) == clyp_line else "  "
                    Log.traceback_code(f"{pointer} {i + 1}: {clyp_lines[i]}", file=sys.stderr)
            else:
                Log.traceback_code(f"    {code_line}", file=sys.stderr)
            Log.warn(f"(Python error at transpiled line {py_line})", file=sys.stderr)
            Log.error(f"[{code}] {type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            err_code = get_error_code(e)
            tb = traceback.extract_tb(sys.exc_info()[2])
            Log.traceback_header("\nTraceback (most recent call last):", file=sys.stderr)
            clyp_frame_indices = [idx for idx, frame in enumerate(tb) if frame.filename == "<string>"]
            last_clyp_frame_idx = clyp_frame_indices[-1] if clyp_frame_indices else None
            for idx, frame in enumerate(tb):
                if frame.filename == "<string>":
                    py_line = frame.lineno
                    clyp_line, code_line = get_clyp_line_for_py(py_line, line_map, clyp_lines)
                    marker = ">>>" if idx == last_clyp_frame_idx else "   "
                    Log.traceback_location(f"{marker} File '{args.file}', line {clyp_line}", file=sys.stderr)
                    if clyp_lines and clyp_line != "?":
                        start = max(0, clyp_line - 3)
                        end = min(len(clyp_lines), clyp_line + 2)
                        for i in range(start, end):
                            pointer = "->" if (i + 1) == clyp_line else "  "
                            Log.traceback_code(f"{pointer} {i + 1}: {clyp_lines[i]}", file=sys.stderr)
                    else:
                        Log.traceback_code(f"    {code_line}", file=sys.stderr)
                else:
                    Log.traceback_location(f"    File '{frame.filename}', line {frame.lineno}", file=sys.stderr)
                    Log.traceback_code(f"      {frame.line}", file=sys.stderr)
            Log.error(f"[{err_code}] {type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "init":
        project_name = args.name
        project_root = os.path.join(os.getcwd(), project_name)
        if os.path.exists(project_root):
            Log.error(f"Directory '{project_name}' already exists.")
            sys.exit(1)
        os.makedirs(project_root)
        
        # Enhanced clyp.json with comprehensive metadata
        config = {
            "name": project_name,
            "version": "0.1.0",
            "description": f"A new Clyp project: {project_name}",
            "entry": "src/main.clyp",
            "author": {
                "name": "Your Name",
                "email": "you@example.com"
            },
            "license": "MIT",
            "keywords": ["clyp", "project"],
            "repository": {
                "type": "git",
                "url": f"https://github.com/yourusername/{project_name}.git"
            },
            "dependencies": {},
            "devDependencies": {},
            "scripts": {
                "build": "python -m clyp.cli check .",
                "test": "python -m clyp.cli run tests/test_main.clyp",
                "format": "python -m clyp.cli format src/",
                "clean": "rm -rf build/ dist/ .clyp-cache/"
            },
            "build": {
                "outputDir": "build",
                "transpileOnly": False,
                "sourceMap": True
            },
            "imports": {
                "paths": {
                    "@src/*": ["src/*"],
                    "@lib/*": ["lib/*"],
                    "@tests/*": ["tests/*"]
                }
            },
            "tools": {
                "formatter": {
                    "lineLength": 88,
                    "indentSize": 4,
                    "useTabs": False
                },
                "linter": {
                    "strict": False,
                    "rules": {
                        "requireReturnTypes": True,
                        "enforceNamingConventions": True
                    }
                }
            }
        }
        
        config_path = os.path.join(project_root, "clyp.json")
        
        # Save clean clyp.json without comments and with proper scripts
        config_content = """{
  "name": \"""" + project_name + """\",
  "version": "0.1.0",
  "description": "A new Clyp project: """ + project_name + """\",
  "entry": "src/main.clyp",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "license": "MIT",
  "keywords": ["clyp", "project"],
  "repository": {
    "type": "git",
    "url": "https://github.com/yourusername/""" + project_name + """.git"
  },
  "dependencies": {},
  "devDependencies": {},
  "scripts": {
    "build": "clyp check .",
    "test": "clyp run tests/test_main.clyp",
    "format": "clyp format src/",
    "clean": "rm -rf build/ dist/ .clyp-cache/"
  },
  "build": {
    "outputDir": "build",
    "transpileOnly": false,
    "sourceMap": true
  },
  "imports": {
    "paths": {
      "@src/*": ["src/*"],
      "@lib/*": ["lib/*"],
      "@tests/*": ["tests/*"]
    }
  },
  "tools": {
    "formatter": {
      "lineLength": 88,
      "indentSize": 4,
      "useTabs": false
    },
    "linter": {
      "strict": false,
      "rules": {
        "requireReturnTypes": true,
        "enforceNamingConventions": true
      }
    }
  }
}"""
        
        with open(config_path, "w") as f:
            f.write(config_content)
        
        src_dir = os.path.join(project_root, "src")
        os.makedirs(src_dir)
        main_clyp_path = os.path.join(src_dir, "main.clyp")
        with open(main_clyp_path, "w") as f:
            f.write('# Welcome to Clyp!\n')
            f.write('# This is a simple Hello World program\n')
            f.write('\n')
            f.write('print("Hello from Clyp!")\n')
            f.write('\n')
            f.write('# Try defining a function:\n')
            f.write('# function greet(str name) returns str {\n')
            f.write('#     return "Hello, " + name + "!";\n')
            f.write('# }\n')
            f.write('# print(greet("World"));\n')
        
        # Create tests directory with example test
        tests_dir = os.path.join(project_root, "tests")
        os.makedirs(tests_dir)
        test_main_path = os.path.join(tests_dir, "test_main.clyp")
        with open(test_main_path, "w") as f:
            f.write('# Example test file\n')
            f.write('# TODO: Add actual tests\n')
            f.write('print("All tests passed!");\n')
        
        gitignore_path = os.path.join(project_root, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("# Build outputs\n")
            f.write("build/\n")
            f.write("dist/\n")
            f.write(".clyp-cache/\n")
            f.write("\n")
            f.write("# Python bytecode\n")
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write("*.pyo\n")
            f.write("\n")
            f.write("# IDE files\n")
            f.write(".vscode/\n")
            f.write(".idea/\n")
            f.write("*.swp\n")
            f.write("*.swo\n")
            f.write("\n")
            f.write("# OS files\n")
            f.write(".DS_Store\n")
            f.write("Thumbs.db\n")
            f.write("\n")
            f.write("# Clyp-specific\n")
            f.write("*.clyp.temp\n")
            f.write(".clyp-debug/\n")
        
        # Create README.md
        readme_path = os.path.join(project_root, "README.md")
        with open(readme_path, "w") as f:
            f.write(f"# {project_name}\n\n")
            f.write(f"A new Clyp project: {project_name}\n\n")
            f.write("## Getting Started\n\n")
            f.write("```bash\n")
            f.write("# Run the main program\n")
            f.write("clyp run src/main.clyp\n\n")
            f.write("# Run tests\n")
            f.write("clyp run tests/test_main.clyp\n\n")
            f.write("# Format code\n")
            f.write("clyp format src/\n\n")
            f.write("# Check project for errors\n")
            f.write("clyp check .\n")
            f.write("```\n\n")
            f.write("## Project Structure\n\n")
            f.write("```\n")
            f.write(f"{project_name}/\n")
            f.write("├── clyp.json          # Project configuration\n")
            f.write("├── src/               # Source code\n")
            f.write("│   └── main.clyp      # Main entry point\n")
            f.write("├── tests/             # Test files\n")
            f.write("│   └── test_main.clyp # Example test\n")
            f.write("├── README.md          # This file\n")
            f.write("└── .gitignore         # Git ignore rules\n")
            f.write("```\n")
        
        Log.success(f"Initialized Clyp project '{project_name}'")
        Log.info(f"Created project structure in: {project_root}")
        Log.info("Project includes:")
        Log.info("  • clyp.json with metadata, scripts, and build config")
        Log.info("  • Source directory with main.clyp")
        Log.info("  • Tests directory with example test")
        Log.info("  • README.md with getting started guide")
        Log.info("  • .gitignore")
        Log.info(f"Run 'cd {project_name} && clyp run src/main.clyp' to get started!")
    elif args.command == "format":
        input_path = os.path.abspath(args.file)
        
        # Handle directory projects and regular directories
        if os.path.isdir(input_path):
            # Check if it's a directory project with clyp.json
            config_path = os.path.join(input_path, "clyp.json")
            if os.path.exists(config_path):
                # Directory project - format all .clyp files in the project
                formatted_count = 0
                for root, _, files in os.walk(input_path):
                    for file in files:
                        if file.endswith('.clyp'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    clyp_code = f.read()
                                formatted = format_clyp_code(clyp_code)
                                
                                if args.print or args.no_write:
                                    print(f"=== {os.path.relpath(file_path, input_path)} ===")
                                    print(formatted)
                                    print()
                                else:
                                    with open(file_path, "w", encoding="utf-8") as f:
                                        f.write(formatted)
                                    formatted_count += 1
                            except Exception as e:
                                code = get_error_code(e)
                                Log.error(f"[{code}] Error formatting {file_path}: {e}", file=sys.stderr)
                
                if not (args.print or args.no_write):
                    Log.success(f"Formatted {formatted_count} files in project directory.")
            else:
                # Regular directory - format all .clyp files
                formatted_count = 0
                for root, _, files in os.walk(input_path):
                    for file in files:
                        if file.endswith('.clyp'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    clyp_code = f.read()
                                formatted = format_clyp_code(clyp_code)
                                
                                if args.print or args.no_write:
                                    print(f"=== {os.path.relpath(file_path, input_path)} ===")
                                    print(formatted)
                                    print()
                                else:
                                    with open(file_path, "w", encoding="utf-8") as f:
                                        f.write(formatted)
                                    formatted_count += 1
                            except Exception as e:
                                code = get_error_code(e)
                                Log.error(f"[{code}] Error formatting {file_path}: {e}", file=sys.stderr)
                
                if not (args.print or args.no_write):
                    Log.success(f"Formatted {formatted_count} files in directory.")
        else:
            # Single file - original behavior
            file_path = input_path
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    clyp_code = f.read()
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Error reading file {args.file}: {e}", file=sys.stderr)
                sys.exit(1)
            try:
                if VERBOSE:
                    Log.info("Calling format_clyp_code()")
                    Log.info("=== ORIGINAL CLYP ===")
                    print(clyp_code)
                formatted = format_clyp_code(clyp_code)
                if VERBOSE:
                    Log.info("=== FORMATTED CLYP ===")
                    print(formatted)
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Formatting failed: {e}", file=sys.stderr)
                sys.exit(1)
            if args.print or args.no_write:
                print(formatted)
            else:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(formatted)
                    Log.success(f"Formatted {args.file} in place.")
                except Exception as e:
                    code = get_error_code(e)
                    Log.error(f"[{code}] Error writing file {args.file}: {e}", file=sys.stderr)
                    sys.exit(1)
    elif args.command == "py2clyp":
        from clyp.transpiler import transpile_to_clyp
        import difflib

        file_path = os.path.abspath(args.file)

        # If the target is a directory, handle it explicitly.
        if os.path.isdir(file_path):
            if not getattr(args, "recursive", False):
                # Provide a clear error rather than attempting to open the directory.
                Log.error(
                    f"[P100] {args.file} is a directory. "
                    "Use --recursive (-r) to transpile a directory of Python files "
                    "or provide a single Python file."
                )
                sys.exit(1)
            # Directory + recursive mode: walk and transpile .py files.
            if args.output:
                Log.error("[Z999] --output is not supported when transpiling a directory.")
                sys.exit(1)
            for dirpath, _, filenames in os.walk(file_path):
                for fname in filenames:
                    if not fname.endswith(".py"):
                        continue
                    src = os.path.join(dirpath, fname)
                    try:
                        with open(src, "r", encoding="utf-8") as f:
                            py_code = f.read()
                    except Exception as e:
                        code = get_error_code(e)
                        Log.error(f"[{code}] Error reading file {src}: {e}")
                        continue
                    try:
                        if VERBOSE:
                            Log.info(f"py2clyp (dir): transpiling {src}")
                        clyp_code = transpile_to_clyp(py_code)
                    except Exception as e:
                        code = get_error_code(e)
                        Log.error(f"[{code}] Transpilation failed for {src}: {e}")
                        continue
                    if args.format and not args.no_format:
                        try:
                            clyp_code = format_clyp_code(clyp_code)
                        except Exception as e:
                            code = get_error_code(e)
                            Log.warn(f"[{code}] Formatting failed for {src}: {e}")
                    out_path = os.path.splitext(src)[0] + ".clyp"
                    if args.print:
                        print(f"# Transpiled from {src}\n{clyp_code}")
                    else:
                        try:
                            with open(out_path, "w", encoding="utf-8") as f:
                                f.write(clyp_code)
                            if not args.quiet:
                                Log.success(f"Wrote transpiled Clyp code to {out_path}")
                        except Exception as e:
                            code = get_error_code(e)
                            Log.error(f"[{code}] Error writing to {out_path}: {e}")
            # Finished directory processing
            sys.exit(0)

        def python_to_clyp_transpile(py_code):
            if VERBOSE:
                Log.info("py2clyp: invoking transpile_to_clyp()")
            res = transpile_to_clyp(py_code)
            if VERBOSE:
                Log.info("py2clyp: transpile_to_clyp() finished")
            return res

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                py_code = f.read()
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        if args.check:
            # Just check if transpilation is possible
            try:
                clyp_code = python_to_clyp_transpile(py_code)
                if not clyp_code or not isinstance(clyp_code, str):
                    Log.error(
                        "[Z999] Transpilation failed: No output generated.", file=sys.stderr
                    )
                    sys.exit(1)
                if not args.quiet:
                    Log.success(f"{args.file} can be transpiled to Clyp.")
                sys.exit(0)
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Transpilation failed: {e}", file=sys.stderr)
                sys.exit(1)  # Ensure SystemExit is always raised on failure
            # Fallback: if we ever reach here, exit with error
            sys.exit(1)
        try:
            if VERBOSE:
                Log.info("py2clyp: starting transpilation")
                Log.info("=== INPUT PYTHON ===")
                print(py_code)
            clyp_code = python_to_clyp_transpile(py_code)
            if VERBOSE:
                Log.info("py2clyp: transpilation finished")
                Log.info("=== OUTPUT CLYP ===")
                print(clyp_code)
        except Exception as e:
            code = get_error_code(e)
            Log.error(f"[{code}] Transpilation failed: {e}", file=sys.stderr)
            sys.exit(1)
        if args.format and not args.no_format:
            try:
                if VERBOSE:
                    Log.info("py2clyp: formatting transpiled code")
                clyp_code = format_clyp_code(clyp_code)
                if VERBOSE:
                    Log.info("py2clyp: formatting complete")
            except Exception as e:
                code = get_error_code(e)
                Log.warn(f"[{code}] Formatting failed: {e}", file=sys.stderr)
        if args.stats:
            py_lines = len(py_code.splitlines())
            clyp_lines = len(clyp_code.splitlines())
            Log.info(f"Python lines: {py_lines}, Clyp lines: {clyp_lines}")
        if args.diff:
            diff = difflib.unified_diff(
                py_code.splitlines(),
                clyp_code.splitlines(),
                fromfile=args.file,
                tofile=args.output or "clyp_output.clyp",
                lineterm="",  # No extra newlines
            )
            print("\n".join(diff))
        if args.print:
            print(clyp_code)
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(clyp_code)
                if not args.quiet:
                    Log.success(f"Wrote transpiled Clyp code to {args.output}")
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Error writing to {args.output}: {e}", file=sys.stderr)
                sys.exit(1)
        if args.overwrite:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clyp_code)
                if not args.quiet:
                    Log.success(f"Overwrote {args.file} with transpiled Clyp code.")
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] Error overwriting {args.file}: {e}", file=sys.stderr)
                sys.exit(1)
        if not (args.print or args.output or args.overwrite or args.diff):
            # Default: print to stdout
            print(clyp_code)
    elif args.command == "clean":

        def remove_dirs(root, dirs):
            for d in dirs:
                path = os.path.join(root, d)
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)
                    Log.success(f"Removed {path}")

        if args.all:
            for dirpath, dirnames, _ in os.walk(os.getcwd()):
                remove_dirs(dirpath, ["build", "dist", ".clyp-cache"])
        else:
            remove_dirs(os.getcwd(), ["build", "dist", ".clyp-cache"])
    elif args.command == "check":

        def check_file(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    clyp_code = f.read()
                parse_clyp(clyp_code, file_path)
                Log.success(f"{file_path} OK")
            except Exception as e:
                code = get_error_code(e)
                Log.error(f"[{code}] {file_path}: {e}")
                return False
            return True

        if args.file:
            input_path = os.path.abspath(args.file)
            
            if os.path.isfile(input_path):
                # Single file
                if not check_file(input_path):
                    sys.exit(1)
            elif os.path.isdir(input_path):
                # Directory - check for project or all .clyp files
                config_path = os.path.join(input_path, "clyp.json")
                if os.path.exists(config_path):
                    # Directory project - check based on entry point and project structure
                    Log.info(f"Checking directory project: {input_path}")
                
                # Check all .clyp files in the directory
                ok = True
                checked_count = 0
                for dirpath, _, filenames in os.walk(input_path):
                    for f in filenames:
                        if f.endswith(".clyp"):
                            file_path = os.path.join(dirpath, f)
                            if not check_file(file_path):
                                ok = False
                            checked_count += 1
                
                if checked_count == 0:
                    Log.warn("No .clyp files found to check.")
                elif ok:
                    Log.success(f"All {checked_count} files OK.")
                else:
                    sys.exit(1)
            else:
                Log.error(f"[F100] Path not found: {args.file}")
                sys.exit(1)
        else:
            # Check all .clyp files in current directory project
            ok = True
            checked_count = 0
            for dirpath, _, filenames in os.walk(os.getcwd()):
                for f in filenames:
                    if f.endswith(".clyp"):
                        file_path = os.path.join(dirpath, f)
                        if not check_file(file_path):
                            ok = False
                        checked_count += 1
            
            if checked_count == 0:
                Log.warn("No .clyp files found to check.")
            elif ok:
                Log.success(f"All {checked_count} files OK.")
            else:
                sys.exit(1)
    elif args.command == "deps":
        from .importer import find_clyp_imports

        def print_deps(file_path, seen=None, level=0):
            # keep behavior similar to top-level print_deps but with verbose logging
            if seen is None:
                seen = set()
            abs_path = os.path.abspath(file_path)
            if abs_path in seen:
                print("  " * level + f"- {os.path.basename(file_path)} (already shown)")
                return
            seen.add(abs_path)
            print("  " * level + f"- {os.path.basename(file_path)}")
            try:
                imports = find_clyp_imports(abs_path)
                if VERBOSE:
                    Log.info(f"deps.print_deps: imports for {file_path}: {imports}")
                for imp in imports:
                    if VERBOSE and (imp.startswith("std") or imp.startswith("stdlib")):
                        Log.info(f"Detected standard library import: {imp}")
                    resolved = resolve_import_path(imp, abs_path)
                    if VERBOSE:
                        Log.info(f"deps.print_deps: resolved {imp} -> {resolved}")
                    if resolved:
                        print_deps(resolved, seen, level + 1)
            except Exception as e:
                print("  " * (level + 1) + f"[error: {e}]")

        if args.file:
            input_path = os.path.abspath(args.file)
            
            if os.path.isfile(input_path):
                # Single file
                print_deps(input_path)
            elif os.path.isdir(input_path):
                # Directory - check if it's a project directory
                entry_point = resolve_project_entry_point(input_path)
                if entry_point:
                    # Directory project - show deps for entry point
                    Log.info(f"Analyzing dependencies for project entry point: {entry_point}")
                    print_deps(entry_point)
                else:
                    # Regular directory - no specific entry point
                    Log.error(f"Directory {input_path} is not a Clyp project (no clyp.json with entry point).")
                    Log.info("💡 Tip: Specify a .clyp file or run from a directory with clyp.json", file=sys.stderr)
                    sys.exit(1)
            else:
                Log.error(f"[F100] Path not found: {args.file}")
                sys.exit(1)
        else:
            # Try to find entry from clyp.json with enhanced config loading
            config = get_project_config()
            if config:
                entry = config.get("entry")
                if entry:
                    entry_path = resolve_config_path(entry, config)
                    if os.path.exists(entry_path):
                        print_deps(entry_path)
                    else:
                        Log.error(f"Entry file '{entry}' not found at {entry_path}")
                        sys.exit(1)
                else:
                    Log.error("No entry found in clyp.json.")
                    Log.info("💡 Tip: Add an 'entry' field to your clyp.json file, e.g., \"entry\": \"src/main.clyp\"", file=sys.stderr)
                    sys.exit(1)
            else:
                Log.error("No file specified and no clyp.json found.")
                Log.info("💡 Tip: Either specify a file (clyp deps main.clyp) or run from a Clyp project directory", file=sys.stderr)
                sys.exit(1)
    elif args.command == "script":
        # Run a script from clyp.json
        config = get_project_config()
        if not config:
            Log.error("No clyp.json found in current directory or parent directories.")
            Log.info("💡 Tip: Run 'clyp init <project-name>' to create a new project", file=sys.stderr)
            sys.exit(1)
        
        if not run_project_script(args.name, config):
            sys.exit(1)
    elif args.command == "config":
        # Show or validate clyp.json configuration
        config = get_project_config()
        if not config:
            Log.error("No clyp.json found in current directory or parent directories.")
            sys.exit(1)
        
        if args.validate:
            Log.success("clyp.json is valid")
            # Additional validations
            entry = config.get("entry")
            if entry:
                entry_path = resolve_config_path(entry, config)
                if not os.path.exists(entry_path):
                    Log.warn(f"Entry file '{entry}' does not exist")
                else:
                    Log.success(f"Entry file '{entry}' exists")
            
            # Validate scripts
            scripts = config.get("scripts", {})
            if scripts:
                Log.info(f"Found {len(scripts)} script(s): {', '.join(scripts.keys())}")
            
            # Validate dependencies
            deps = config.get("dependencies", {})
            dev_deps = config.get("devDependencies", {})
            if deps:
                Log.info(f"Found {len(deps)} dependenc(ies)")
            if dev_deps:
                Log.info(f"Found {len(dev_deps)} dev dependenc(ies)")
                
        if args.show or not (args.validate):
            print(json.dumps(config, indent=2))
    elif args.command == "add":
        # Add a dependency to clyp.json
        config_path = find_config_file()
        if not config_path:
            Log.error("No clyp.json found in current directory or parent directories.")
            Log.info("💡 Tip: Run 'clyp init <project-name>' to create a new project", file=sys.stderr)
            sys.exit(1)
        
        config = load_clyp_config(config_path)
        if not config:
            sys.exit(1)
        
        if not add_dependency(args.dependency, config, config_path, args.dev):
            sys.exit(1)
    elif args.command == "remove":
        # Remove a dependency from clyp.json
        config_path = find_config_file()
        if not config_path:
            Log.error("No clyp.json found in current directory or parent directories.")
            sys.exit(1)
        
        config = load_clyp_config(config_path)
        if not config:
            sys.exit(1)
        
        if not remove_dependency(args.dependency, config, config_path, args.dev):
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
