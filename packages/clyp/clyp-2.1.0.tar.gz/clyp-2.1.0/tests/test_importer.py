import sys
import json
import zipfile
import pathlib
import pytest

from clyp import importer
from clyp.importer import find_clyp_imports, clyp_include, clyp_import


def test_find_clyp_imports(tmp_path):
	f = tmp_path / "example.clyp"
	f.write_text("import os\nimport math")

	imports = find_clyp_imports(str(f))
	assert "os" in imports
	assert "math" in imports


def make_clb(path: pathlib.Path, module_name: str, module_source: str, version: str):
	metadata = {
		"clyp_version": version,
		"platform": sys.platform,
		"module_filename": f"{module_name}.py",
	}
	with zipfile.ZipFile(path, "w") as zf:
		zf.writestr("metadata.json", json.dumps(metadata))
		zf.writestr(f"{module_name}.py", module_source)


def test_clyp_include_success(tmp_path):
	# Create a .clb file next to a fake caller file
	clb_path = tmp_path / "mymod.clb"
	caller = tmp_path / "caller.py"
	caller.write_text("# caller")

	make_clb(
		clb_path,
		module_name="mymod",
		module_source="VALUE = 123",
		version=importer.__version__,
	)

	# Use relative path as clyp_include expects (relative to calling file)
	module = clyp_include("mymod.clb", str(caller))
	assert hasattr(module, "VALUE")
	assert module.VALUE == 123

	# cleanup sys.modules and importer caches inserted by clyp_include
	module_key = f"clyp_module.{str(pathlib.Path(clb_path).resolve())}"
	for key in (module_key, "mymod"):
		if key in sys.modules:
			del sys.modules[key]
	if str(pathlib.Path(clb_path).resolve()) in importer._loaded_clb_modules:
		del importer._loaded_clb_modules[str(pathlib.Path(clb_path).resolve())]


def test_clyp_include_file_not_found(tmp_path):
	caller = tmp_path / "caller2.py"
	caller.write_text("# caller")

	with pytest.raises(FileNotFoundError):
		clyp_include("does_not_exist.clb", str(caller))


def test_clyp_import_missing_module(tmp_path):
	# Ensure ImportError is raised when clyp file can't be found
	with pytest.raises(ImportError):
		clyp_import("this_module_does_not_exist", current_file_path=str(tmp_path / "x.py"))
