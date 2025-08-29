import os
import pathlib
import sys
import importlib.util
import zipfile
import tempfile
import json
import shutil
import atexit
from typing import Optional, List
from . import __version__
from .transpiler import parse_clyp

_loaded_clb_modules = {}
_temp_dirs = []


def cleanup_clb_temps():
    for temp_dir in _temp_dirs:
        shutil.rmtree(temp_dir, ignore_errors=True)
    _temp_dirs.clear()


atexit.register(cleanup_clb_temps)


def clyp_include(clb_path: str, calling_file: str):
    """
    Loads a .clb file, checks for compatibility, and imports the module.
    """
    base_dir = pathlib.Path(calling_file).parent
    clb_file_path = base_dir / clb_path

    if not clb_file_path.exists():
        raise FileNotFoundError(f"CLB file not found: {clb_file_path}")

    clb_abs_path = str(clb_file_path.resolve())
    if clb_abs_path in _loaded_clb_modules:
        return _loaded_clb_modules[clb_abs_path]

    temp_dir = tempfile.mkdtemp()
    _temp_dirs.append(temp_dir)

    try:
        with zipfile.ZipFile(clb_file_path, "r") as zf:
            zf.extract("metadata.json", temp_dir)
            with open(pathlib.Path(temp_dir) / "metadata.json", "r") as f:
                metadata = json.load(f)

            if metadata.get("clyp_version") != __version__:
                print(
                    f"Warning: Clyp version mismatch. File was built with {metadata.get('clyp_version')}, running {__version__}.",
                    file=sys.stderr,
                )
            if metadata.get("platform") != sys.platform:
                print(
                    f"Warning: Platform mismatch. File was built for {metadata.get('platform')}, running on {sys.platform}.",
                    file=sys.stderr,
                )

            module_filename = metadata["module_filename"]
            zf.extract(module_filename, temp_dir)

            module_path = pathlib.Path(temp_dir) / module_filename
            module_name = module_path.stem.split(".")[0]

            sys.path.insert(0, temp_dir)

            spec = importlib.util.spec_from_file_location(module_name, str(module_path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not find compiled module spec in {clb_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            _loaded_clb_modules[clb_abs_path] = module
            # Make the module available globally
            globals()[module_name] = module
            return module

    except Exception as e:
        shutil.rmtree(temp_dir)
        if temp_dir in _temp_dirs:
            _temp_dirs.remove(temp_dir)
        raise ImportError(f"Failed to load CLB file {clb_path}: {e}")


def clyp_import(module_name: str, current_file_path: Optional[str] = None) -> object:
    """
    Imports a .clyp file as a Python module.
    Supports importing standard modules from the 'std' folder.
    """
    mod_rel = module_name.replace(".", os.path.sep)

    # Build ordered search paths: std -> caller dir -> sys.path
    search_paths: List[pathlib.Path] = []
    std_folder = pathlib.Path(__file__).parent.parent.joinpath("std").resolve()

    # Normalize lookups into the std folder so we support:
    #   - import math       -> std/math.py
    #   - import std        -> std/__init__.py
    #   - import std.math   -> std/math.py or std/math/__init__.py
    #   - import clyp.std.math -> std/math.py
    if std_folder.exists():
        # derive the parts that correspond to files under clyp/std
        lookup_parts = module_name.split(".")
        if lookup_parts and lookup_parts[0] == "clyp":
            lookup_parts = lookup_parts[1:]
        # If the caller included a leading "std", drop it so we don't get std/std/...
        if lookup_parts and lookup_parts[0] == "std":
            lookup_parts = lookup_parts[1:]

        # canonical module name to register when loading from std folder
        canonical_name = ".".join(["clyp", "std"] + lookup_parts) if lookup_parts else "clyp.std"

        # If user requested the top-level std package (module_name == "std" or
        # module_name == "clyp.std"), load std/__init__.py
        init_at_root = std_folder.joinpath("__init__.py")
        if (not lookup_parts) and init_at_root.exists():
            file_to_load = init_at_root
            spec = importlib.util.spec_from_file_location(canonical_name, str(file_to_load))
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load std Python module '{module_name}'")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if canonical_name not in sys.modules:
                sys.modules[canonical_name] = module
            if module_name not in sys.modules:
                sys.modules[module_name] = module
            return module

        # For non-root lookups (e.g. math or math.submod) check file or package inside std
        if lookup_parts:
            py_candidate = std_folder.joinpath(*lookup_parts).with_suffix(".py")
            pkg_dir = std_folder.joinpath(*lookup_parts)
            pkg_init = pkg_dir.joinpath("__init__.py")

            if py_candidate.exists() or pkg_init.exists():
                file_to_load = py_candidate if py_candidate.exists() else pkg_init
                spec = importlib.util.spec_from_file_location(canonical_name, str(file_to_load))
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not load std Python module '{module_name}'")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if canonical_name not in sys.modules:
                    sys.modules[canonical_name] = module
                if module_name not in sys.modules:
                    sys.modules[module_name] = module
                return module

        # fall back to adding std_folder to the search path for later resolution
        search_paths.append(std_folder)
    if current_file_path:
        search_paths.append(pathlib.Path(current_file_path).parent.resolve())
    for p in sys.path:
        try:
            search_paths.append(pathlib.Path(p).resolve())
        except Exception:
            # ignore entries that can't be resolved
            continue

    found_path: Optional[str] = None
    for base in search_paths:
        # check for package directory: prefer __init__.clyp, but accept
        # standard Python packages (__init__.py) as well
        pkg_dir = base.joinpath(*module_name.split("."))
        init_clyp = pkg_dir.joinpath("__init__.clyp")
        init_py = pkg_dir.joinpath("__init__.py")
        if pkg_dir.is_dir():
            if init_clyp.exists():
                found_path = str(init_clyp.resolve())
                break
            if init_py.exists():
                # Load as a normal Python package/module and return it
                file_to_load = init_py
                spec = importlib.util.spec_from_file_location(
                    module_name, str(file_to_load)
                )
                if spec is None or spec.loader is None:
                    raise ImportError(
                        f"Could not load Python package '{module_name}' from "
                        f"{file_to_load}"
                    )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if module_name not in sys.modules:
                    sys.modules[module_name] = module

                # If loaded file lives under std_folder, also register
                # a canonical clyp.std.* name so plain imports (e.g. "fs")
                # map to "clyp.std.fs".
                try:
                    if std_folder.exists():
                        fp = pathlib.Path(file_to_load).resolve()
                        rel = fp.relative_to(std_folder)
                        # for __init__.py, the package parts are the parent parts
                        if fp.name == "__init__.py":
                            parts = rel.parent.parts
                        else:
                            parts = rel.with_suffix("").parts
                        canonical = (
                            ".".join(["clyp", "std"] + list(parts))
                            if parts
                            else "clyp.std"
                        )
                        if canonical not in sys.modules:
                            sys.modules[canonical] = module
                except Exception:
                    # ignore if relative_to fails or std_folder not applicable
                    pass

                return module

        # check for single-file module: prefer .clyp, but accept .py too
        candidate = base.joinpath(*module_name.split("."))  # handles dotted names
        candidate_clyp = candidate.with_suffix(".clyp") if not candidate.suffix else candidate
        candidate_py = candidate.with_suffix(".py") if not candidate.suffix else candidate
        if candidate_clyp.exists():
            found_path = str(candidate_clyp.resolve())
            break
        if candidate_py.exists():
            # Load as a normal Python module and return it
            file_to_load = candidate_py
            spec = importlib.util.spec_from_file_location(
                module_name, str(file_to_load)
            )
            if spec is None or spec.loader is None:
                raise ImportError(
                    f"Could not load Python module '{module_name}' from "
                    f"{file_to_load}"
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if module_name not in sys.modules:
                sys.modules[module_name] = module

            # If this module file is inside the std folder, also register
            # it under clyp.std.<name> so imports like "fs" map to
            # "clyp.std.fs".
            try:
                if std_folder.exists():
                    fp = pathlib.Path(file_to_load).resolve()
                    rel = fp.relative_to(std_folder)
                    # for single-file modules, drop suffix to get parts
                    parts = rel.with_suffix("").parts
                    canonical = (
                        ".".join(["clyp", "std"] + list(parts))
                        if parts
                        else "clyp.std"
                    )
                    if canonical not in sys.modules:
                        sys.modules[canonical] = module
            except Exception:
                pass

            return module

    if not found_path:
        raise ImportError(
            f"Could not find clyp module '{module_name}' at '{mod_rel}'"
        )
    module_key = f"clyp_module.{found_path}"

    if module_key in sys.modules:
        return sys.modules[module_key]

    with open(found_path, "r", encoding="utf-8") as f:
        clyp_code = f.read()

    python_code = parse_clyp(clyp_code, file_path=found_path)

    # create a unique spec/name to avoid clobbering existing modules
    spec = importlib.util.spec_from_loader(module_key, loader=None, origin=found_path)
    if spec is None:
        raise ImportError(f"Could not create spec for clyp module '{module_name}'")

    module = importlib.util.module_from_spec(spec)
    # set common attributes
    module.__file__ = found_path
    module.__package__ = module_name.rpartition(".")[0]

    # register under the unique key; only install canonical name if not present
    sys.modules[module_key] = module
    if module_name not in sys.modules:
        sys.modules[module_name] = module

    exec(python_code, module.__dict__)

    return module


def find_clyp_imports(file_path: str):
    """
    Parses a .clyp file and returns a list of imported modules.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        clyp_code = f.read()

    imports = []
    for line in clyp_code.split("\n"):
        if line.strip().startswith("import "):
            parts = line.strip().split()
            if len(parts) > 1:
                imports.append(parts[1])
    return imports
