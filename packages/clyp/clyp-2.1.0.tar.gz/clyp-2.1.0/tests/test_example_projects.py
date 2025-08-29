"""
Test suite for example projects in /examples/

This module contains tests that run the example projects to ensure they work correctly.
Each example project contains a clyp.json file and demonstrates specific features.
"""

import pytest
import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Tuple


class TestExampleProjects:
    """Test class for all example projects in the /examples/ directory."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment."""
        cls.repo_root = Path(__file__).parent.parent
        cls.examples_dir = cls.repo_root / "examples"
        cls.clyp_cli = cls.repo_root / "clyp" / "cli.py"
        
        # Ensure examples directory exists
        assert cls.examples_dir.exists(), f"Examples directory not found: {cls.examples_dir}"
        
        # Find all example projects (directories with clyp.json)
        cls.example_projects = []
        for item in cls.examples_dir.iterdir():
            if item.is_dir() and (item / "clyp.json").exists():
                cls.example_projects.append(item)
        
        assert len(cls.example_projects) > 0, "No example projects found with clyp.json files"
    
    def run_clyp_command(self, args: List[str], cwd: Path = None) -> Tuple[int, str, str]:
        """Run a clyp CLI command and return exit code, stdout, stderr."""
        if cwd is None:
            cwd = self.repo_root
            
        # Set up environment to include the repo root in Python path
        env = os.environ.copy()
        pythonpath = str(self.repo_root)
        if 'PYTHONPATH' in env:
            pythonpath = str(self.repo_root) + os.pathsep + env['PYTHONPATH']
        env['PYTHONPATH'] = pythonpath
        
        cmd = ["python", "-m", "clyp.cli"] + args
            
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                env=env
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out after 30 seconds"
        except Exception as e:
            return -1, "", str(e)
    
    def load_project_config(self, project_dir: Path) -> Dict:
        """Load and parse the clyp.json configuration file."""
        config_file = project_dir / "clyp.json"
        assert config_file.exists(), f"clyp.json not found in {project_dir}"
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def test_example_projects_structure(self):
        """Test that all example projects have proper structure."""
        for project_dir in self.example_projects:
            config = self.load_project_config(project_dir)
            
            # Check required fields
            assert "name" in config, f"Project {project_dir.name} missing 'name' field"
            assert "main" in config, f"Project {project_dir.name} missing 'main' field"
            assert "scripts" in config, f"Project {project_dir.name} missing 'scripts' field"
            
            # Check that main file exists
            main_file = project_dir / config["main"]
            assert main_file.exists(), f"Main file {config['main']} not found in {project_dir.name}"
            
            # Check that it's a .clyp file
            assert main_file.suffix == ".clyp", f"Main file must be .clyp file in {project_dir.name}"
    
    def test_hello_world_project(self):
        """Test the hello-world-project specifically."""
        project_dir = self.examples_dir / "hello-world-project"
        assert project_dir.exists(), "hello-world-project not found"
        
        config = self.load_project_config(project_dir)
        assert config["name"] == "hello-world-project"
        assert config["main"] == "main.clyp"
        
        # Test running the project
        exit_code, stdout, stderr = self.run_clyp_command(["run", "."], cwd=project_dir)
        assert exit_code == 0, f"hello-world-project failed: {stderr}"
        
        # Check expected output
        assert "Hello, World!" in stdout
        assert "Greetings, Clyp Developer!" in stdout
    
    def test_advanced_features_project(self):
        """Test the advanced-features-project."""
        project_dir = self.examples_dir / "advanced-features-project"
        assert project_dir.exists(), "advanced-features-project not found"
        
        config = self.load_project_config(project_dir)
        assert config["name"] == "advanced-features-project"
        assert config["main"] == "advanced_demo.clyp"
        
        # Test running the project
        exit_code, stdout, stderr = self.run_clyp_command(["run", "."], cwd=project_dir)
        assert exit_code == 0, f"advanced-features-project failed: {stderr}"
        
        # Check for key feature demonstrations
        assert "Basic Clyp Features Demo" in stdout
        assert "Hello, Alice!" in stdout
        assert "Greetings, Bob!" in stdout
        assert "Alice == 25 years old!" in stdout
        assert "Basic Features Demo Complete" in stdout
    
    def test_data_structures_project(self):
        """Test the data-structures-project."""
        project_dir = self.examples_dir / "data-structures-project"
        assert project_dir.exists(), "data-structures-project not found"
        
        config = self.load_project_config(project_dir)
        assert config["name"] == "data-structures-project"
        assert config["main"] == "data_demo.clyp"
        
        # Test running the project
        exit_code, stdout, stderr = self.run_clyp_command(["run", "."], cwd=project_dir)
        assert exit_code == 0, f"data-structures-project failed: {stderr}"
        
        # Check for key demonstrations
        assert "Clyp Data Structures Demo" in stdout
        assert "List Operations:" in stdout
        assert "Variable Operations:" in stdout
        assert "Basic Functions:" in stdout
        assert "Data Structures Demo Complete" in stdout
    
    def test_stdlib_showcase_project(self):
        """Test the stdlib-showcase-project."""
        project_dir = self.examples_dir / "stdlib-showcase-project"
        assert project_dir.exists(), "stdlib-showcase-project not found"
        
        config = self.load_project_config(project_dir)
        assert config["name"] == "stdlib-showcase-project"
        assert config["main"] == "stdlib_demo.clyp"
        
        # Test running the project
        exit_code, stdout, stderr = self.run_clyp_command(["run", "."], cwd=project_dir)
        assert exit_code == 0, f"stdlib-showcase-project failed: {stderr}"
        
        # Check for standard library demonstrations
        assert "Clyp Standard Library Demo" in stdout
        assert "Basic Operations:" in stdout
        assert "String Operations:" in stdout
        assert "Math Operations:" in stdout
        assert "Standard Library Demo Complete" in stdout
    
    def test_all_projects_check_command(self):
        """Test that all projects pass the check command."""
        for project_dir in self.example_projects:
            config = self.load_project_config(project_dir)
            
            # Run clyp check on the project
            exit_code, stdout, stderr = self.run_clyp_command(["check", "."], cwd=project_dir)
            assert exit_code == 0, f"Project {config['name']} failed check: {stderr}"
    
    def test_all_projects_run_successfully(self):
        """Test that all projects can be run without errors."""
        for project_dir in self.example_projects:
            config = self.load_project_config(project_dir)
            
            # Run the project
            exit_code, stdout, stderr = self.run_clyp_command(["run", "."], cwd=project_dir)
            assert exit_code == 0, f"Project {config['name']} failed to run: {stderr}"
            
            # Ensure some output was produced
            assert len(stdout.strip()) > 0, f"Project {config['name']} produced no output"
    
    def test_project_scripts(self):
        """Test that project scripts defined in clyp.json work."""
        for project_dir in self.example_projects:
            config = self.load_project_config(project_dir)
            scripts = config.get("scripts", {})
            
            # Test common scripts if they exist
            if "test" in scripts:
                exit_code, stdout, stderr = self.run_clyp_command(["script", "test"], cwd=project_dir)
                # Allow script to fail if it's a check command and there are no test files
                # but it should not crash
                assert exit_code in [0, 1], f"Script 'test' crashed in {config['name']}: {stderr}"
            
            # Skip format script test since it requires clyp to be in PATH
            # which is not available in the test environment
            # if "format" in scripts:
            #     exit_code, stdout, stderr = self.run_clyp_command(["script", "format"], cwd=project_dir)
            #     assert exit_code == 0, f"Script 'format' failed in {config['name']}: {stderr}"
    
    def test_project_config_validation(self):
        """Test that all project configurations are valid."""
        for project_dir in self.example_projects:
            # Test config validation
            exit_code, stdout, stderr = self.run_clyp_command(["config", "--validate"], cwd=project_dir)
            assert exit_code == 0, f"Config validation failed for {project_dir.name}: {stderr}"
    
    def test_project_readme_files(self):
        """Test that all projects have README files with proper content."""
        for project_dir in self.example_projects:
            readme_file = project_dir / "README.md"
            assert readme_file.exists(), f"README.md not found in {project_dir.name}"
            
            with open(readme_file, 'r') as f:
                content = f.read()
            
            # Check that README contains basic information
            assert len(content) > 100, f"README.md too short in {project_dir.name}"
            assert "Running" in content or "running" in content, f"README.md missing running instructions in {project_dir.name}"
    
    def test_output_expectations(self):
        """Test that projects produce expected outputs."""
        # Test hello-world-project specific outputs
        project_dir = self.examples_dir / "hello-world-project"
        if project_dir.exists():
            exit_code, stdout, stderr = self.run_clyp_command(["run", "."], cwd=project_dir)
            assert exit_code == 0
            lines = stdout.strip().split('\n')
            assert len(lines) >= 2, "hello-world-project should produce at least 2 lines of output"
            assert any("Hello, World!" in line for line in lines)
            assert any("Greetings, Clyp Developer!" in line for line in lines)
        
        # Test that advanced features project demonstrates multiple features
        project_dir = self.examples_dir / "advanced-features-project"
        if project_dir.exists():
            exit_code, stdout, stderr = self.run_clyp_command(["run", "."], cwd=project_dir)
            assert exit_code == 0
            
            # Should demonstrate at least 3 different features
            feature_keywords = [
                "Basic Clyp Features Demo",
                "Hello, Alice!", 
                "Greetings, Bob!",
                "Alice == 25 years old!",
                "Basic Features Demo Complete"
            ]
            found_features = sum(1 for keyword in feature_keywords if keyword in stdout)
            assert found_features >= 3, f"Advanced features project only demonstrated {found_features} features"


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])