"""
Tests for template generators
"""

import pytest

from devopsforge.templates.cicd_generator import CICDGenerator
from devopsforge.templates.dockerfile_generator import DockerfileGenerator


class TestDockerfileGenerator:
    """Test cases for DockerfileGenerator"""

    def test_init(self):
        """Test generator initialization"""
        generator = DockerfileGenerator()
        assert generator is not None

    def test_generate_python_dockerfile(self, project_info_dict):
        """Test Python Dockerfile generation"""
        generator = DockerfileGenerator()
        dockerfile = generator.generate(project_info_dict)

        assert dockerfile is not None
        assert isinstance(dockerfile, str)
        assert "FROM python:" in dockerfile
        assert "pip install" in dockerfile
        assert "CMD" in dockerfile

    def test_generate_nodejs_dockerfile(self):
        """Test Node.js Dockerfile generation"""
        generator = DockerfileGenerator()
        project_info = {
            "project_type": "nodejs",
            "language": "javascript",
            "dependencies": ["express"],
            "build_tools": ["npm"],
            "test_frameworks": ["jest"],
            "framework": "express",
            "project_name": "test-nodejs",
        }

        dockerfile = generator.generate(project_info)
        assert "FROM node:" in dockerfile
        assert "npm ci" in dockerfile

    def test_generate_java_dockerfile(self):
        """Test Java Dockerfile generation"""
        generator = DockerfileGenerator()
        project_info = {
            "project_type": "java",
            "language": "java",
            "dependencies": ["spring-boot"],
            "build_tools": ["maven"],
            "test_frameworks": ["junit"],
            "framework": "spring-boot",
            "project_name": "test-java",
        }

        dockerfile = generator.generate(project_info)
        assert "FROM openjdk:" in dockerfile
        assert "mvn" in dockerfile

    def test_generate_go_dockerfile(self):
        """Test Go Dockerfile generation"""
        generator = DockerfileGenerator()
        project_info = {
            "project_type": "go",
            "language": "go",
            "dependencies": [],
            "build_tools": ["go"],
            "test_frameworks": [],
            "framework": None,
            "project_name": "test-go",
        }

        dockerfile = generator.generate(project_info)
        assert "FROM golang:" in dockerfile
        assert "go build" in dockerfile

    def test_generate_rust_dockerfile(self):
        """Test Rust Dockerfile generation"""
        generator = DockerfileGenerator()
        project_info = {
            "project_type": "rust",
            "language": "rust",
            "dependencies": [],
            "build_tools": ["cargo"],
            "test_frameworks": [],
            "framework": None,
            "project_name": "test-rust",
        }

        dockerfile = generator.generate(project_info)
        assert "FROM rust:" in dockerfile
        assert "cargo build" in dockerfile


class TestCICDGenerator:
    """Test cases for CICDGenerator"""

    def test_init(self):
        """Test generator initialization"""
        generator = CICDGenerator()
        assert generator is not None

    def test_generate_github_actions(self, project_info_dict):
        """Test GitHub Actions generation"""
        generator = CICDGenerator()
        workflow = generator.generate(
            project_info_dict, ci_type="github_actions"
        )

        assert workflow is not None
        assert isinstance(workflow, str)
        assert "name: CI" in workflow
        assert "on:" in workflow
        assert "jobs:" in workflow
        assert "runs-on: ubuntu-latest" in workflow

    def test_generate_gitlab_ci(self, project_info_dict):
        """Test GitLab CI generation"""
        generator = CICDGenerator()
        pipeline = generator.generate(project_info_dict, ci_type="gitlab_ci")

        assert pipeline is not None
        assert isinstance(pipeline, str)
        assert "stages:" in pipeline
        assert "test:" in pipeline
        assert "build:" in pipeline

    def test_generate_invalid_ci_type(self, project_info_dict):
        """Test invalid CI type handling"""
        generator = CICDGenerator()

        with pytest.raises(ValueError):
            generator.generate(project_info_dict, ci_type="invalid_type")

    def test_github_actions_structure(self, project_info_dict):
        """Test GitHub Actions workflow structure"""
        generator = CICDGenerator()
        workflow = generator.generate(
            project_info_dict, ci_type="github_actions"
        )

        # Check for essential sections
        assert "name: CI" in workflow
        assert "on:" in workflow
        assert "jobs:" in workflow
        assert "test:" in workflow
        assert "build:" in workflow

        # Check for Python-specific steps
        assert "Set up Python" in workflow
        assert "pip install" in workflow
        assert "pytest" in workflow

    def test_gitlab_ci_structure(self, project_info_dict):
        """Test GitLab CI pipeline structure"""
        generator = CICDGenerator()
        pipeline = generator.generate(project_info_dict, ci_type="gitlab_ci")

        # Check for essential sections
        assert "stages:" in pipeline
        assert "test:" in pipeline
        assert "build:" in pipeline

        # Check for Python-specific steps
        assert "pip install" in pipeline
        assert "pytest" in pipeline
