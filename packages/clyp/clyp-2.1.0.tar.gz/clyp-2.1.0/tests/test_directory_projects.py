import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import patch
from clyp.cli import resolve_project_entry_point, resolve_input_path

def test_resolve_project_entry_point():
    """Test resolving entry point from a directory with clyp.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create clyp.json
        config = {
            "name": "test-project",
            "version": "1.0.0",
            "entry": "src/main.clyp"
        }
        config_path = os.path.join(tmpdir, "clyp.json")
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        # Create entry point file
        src_dir = os.path.join(tmpdir, "src")
        os.makedirs(src_dir)
        entry_path = os.path.join(src_dir, "main.clyp")
        with open(entry_path, "w") as f:
            f.write('print("Hello, World!")\n')
        
        # Test resolution
        result = resolve_project_entry_point(tmpdir)
        assert result == os.path.abspath(entry_path)

def test_resolve_project_entry_point_missing_file():
    """Test resolving entry point when entry file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create clyp.json with non-existent entry
        config = {
            "name": "test-project",
            "version": "1.0.0",
            "entry": "src/missing.clyp"
        }
        config_path = os.path.join(tmpdir, "clyp.json")
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        # Test resolution
        result = resolve_project_entry_point(tmpdir)
        assert result is None

def test_resolve_project_entry_point_no_config():
    """Test resolving entry point when no clyp.json exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = resolve_project_entry_point(tmpdir)
        assert result is None

def test_resolve_input_path_file():
    """Test resolving input path for a regular file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, "test.clyp")
        with open(file_path, "w") as f:
            f.write('print("test")\n')
        
        resolved, is_project = resolve_input_path(file_path)
        assert resolved == os.path.abspath(file_path)
        assert not is_project

def test_resolve_input_path_directory_project():
    """Test resolving input path for a directory project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create project structure
        config = {
            "name": "test-project",
            "version": "1.0.0",
            "entry": "main.clyp"
        }
        config_path = os.path.join(tmpdir, "clyp.json")
        with open(config_path, "w") as f:
            json.dump(config, f)
        
        entry_path = os.path.join(tmpdir, "main.clyp")
        with open(entry_path, "w") as f:
            f.write('print("Hello from project!")\n')
        
        resolved, is_project = resolve_input_path(tmpdir)
        assert resolved == os.path.abspath(entry_path)
        assert is_project

def test_resolve_input_path_regular_directory():
    """Test resolving input path for a regular directory (no clyp.json)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        resolved, is_project = resolve_input_path(tmpdir)
        assert resolved == os.path.abspath(tmpdir)
        assert not is_project

def test_resolve_input_path_nonexistent():
    """Test resolving input path for non-existent path."""
    nonexistent = "/path/that/does/not/exist"
    resolved, is_project = resolve_input_path(nonexistent)
    assert resolved == os.path.abspath(nonexistent)
    assert not is_project