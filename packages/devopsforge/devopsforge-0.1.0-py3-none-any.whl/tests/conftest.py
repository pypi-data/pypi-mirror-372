"""Pytest fixtures for DevOpsForge tests."""

import pytest
from pathlib import Path
from devopsforge.core.analyzer import ProjectInfo


@pytest.fixture
def sample_python_project(tmp_path):
    """Create a sample Python project structure for testing."""
    project_dir = tmp_path / "sample_python_project"
    project_dir.mkdir()
    
    # Create Python files
    (project_dir / "main.py").write_text("print('Hello, World!')")
    (project_dir / "requirements.txt").write_text("flask==2.3.0\npytest==7.4.0")
    (project_dir / "setup.py").write_text("from setuptools import setup\nsetup(name='test-project')")
    (project_dir / "pytest.ini").write_text("[pytest]\ntestpaths = tests")
    (project_dir / "tests").mkdir()
    (project_dir / "tests" / "test_main.py").write_text("def test_hello():\n    assert True")
    
    return project_dir


@pytest.fixture
def project_info_dict():
    """Create a sample project info dictionary for testing."""
    return {
        "project_type": "python",
        "language": "python",
        "version": "3.11",
        "dependencies": ["flask"],
        "build_tools": ["pip"],
        "test_frameworks": ["pytest"],
        "framework": "flask",
        "web_framework": "flask",  # Added this field
        "database": None,
        "has_docker": False,
        "has_kubernetes": False,
        "has_ci_cd": False,
        "project_name": "test-project"
    }


@pytest.fixture
def project_info_object(project_info_dict):
    """Create a ProjectInfo object for testing."""
    return ProjectInfo(**project_info_dict)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    return tmp_path / "temp_project"
