import pytest
import json
import os
import tempfile
import shutil
from unittest.mock import patch
from clyp.cli import load_clyp_config, parse_json5, get_project_config, add_dependency, remove_dependency

def test_parse_json5_with_comments():
    """Test JSON5 parsing with comments."""
    json5_content = '''
    {
        // This is a comment
        "name": "test-project",
        "version": "1.0.0", // Another comment
        "dependencies": {
            "utils": "1.0.0"
        }
    }
    '''
    
    result = parse_json5(json5_content)
    expected = {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {
            "utils": "1.0.0"
        }
    }
    assert result == expected

def test_parse_json5_with_trailing_commas():
    """Test JSON5 parsing with trailing commas."""
    json5_content = '''
    {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {
            "utils": "1.0.0",
        },
    }
    '''
    
    result = parse_json5(json5_content)
    expected = {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {
            "utils": "1.0.0"
        }
    }
    assert result == expected

def test_load_clyp_config_valid():
    """Test loading a valid clyp.json file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_data = {
            "name": "test-project",
            "version": "1.0.0",
            "entry": "src/main.clyp"
        }
        json.dump(config_data, f)
        config_path = f.name
    
    try:
        result = load_clyp_config(config_path)
        assert result == config_data
    finally:
        os.unlink(config_path)

def test_load_clyp_config_with_json5():
    """Test loading a clyp.json file with JSON5 format."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        content = '''
        {
            // Project configuration
            "name": "test-project",
            "version": "1.0.0",
            "entry": "src/main.clyp",
        }
        '''
        f.write(content)
        config_path = f.name
    
    try:
        result = load_clyp_config(config_path)
        expected = {
            "name": "test-project",
            "version": "1.0.0",
            "entry": "src/main.clyp"
        }
        assert result == expected
    finally:
        os.unlink(config_path)

def test_add_dependency():
    """Test adding a dependency to config."""
    config = {
        "name": "test-project",
        "dependencies": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    
    try:
        result = add_dependency("utils@1.0.0", config, config_path, False)
        assert result == True
        assert config["dependencies"]["utils"] == "1.0.0"
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)

def test_add_dev_dependency():
    """Test adding a development dependency to config."""
    config = {
        "name": "test-project",
        "devDependencies": {}
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    
    try:
        result = add_dependency("pytest", config, config_path, True)
        assert result == True
        assert config["devDependencies"]["pytest"] == "*"
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)

def test_remove_dependency():
    """Test removing a dependency from config."""
    config = {
        "name": "test-project",
        "dependencies": {
            "utils": "1.0.0",
            "http": "2.0.0"
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
    
    try:
        result = remove_dependency("utils", config, config_path, False)
        assert result == True
        assert "utils" not in config["dependencies"]
        assert "http" in config["dependencies"]
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)

def test_get_project_config_hierarchy():
    """Test finding clyp.json in parent directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create nested directory structure
        project_dir = os.path.join(temp_dir, "project")
        sub_dir = os.path.join(project_dir, "src", "components")
        os.makedirs(sub_dir)
        
        # Create clyp.json in project root
        config_data = {"name": "test-project", "version": "1.0.0"}
        config_path = os.path.join(project_dir, "clyp.json")
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        # Test finding config from subdirectory
        result = get_project_config(sub_dir)
        assert result == config_data