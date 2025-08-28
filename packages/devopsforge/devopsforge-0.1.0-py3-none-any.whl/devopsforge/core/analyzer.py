"""
Core repository analyzer for DevOpsGenie
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ProjectInfo:
    """Information about a detected project"""

    project_type: str
    language: str
    version: Optional[str]
    dependencies: List[str]
    build_tools: List[str]
    test_frameworks: List[str]
    has_docker: bool
    has_kubernetes: bool
    has_ci_cd: bool
    framework: Optional[str]
    database: Optional[str]
    web_framework: Optional[str]


class RepositoryAnalyzer:
    """Analyzes repository structure and detects project characteristics"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.project_info = None

    def analyze(self) -> ProjectInfo:
        """Analyze the repository and return project information"""
        if not self.repo_path.exists():
            raise ValueError(
                f"Repository path does not exist: {self.repo_path}"
            )

        # Detect project type
        project_type = self._detect_project_type()
        language = self._detect_language()
        version = self._detect_version()
        dependencies = self._detect_dependencies()
        build_tools = self._detect_build_tools()
        test_frameworks = self._detect_test_frameworks()
        has_docker = self._has_docker_files()
        has_kubernetes = self._has_kubernetes_files()
        has_ci_cd = self._has_ci_cd_files()
        framework = self._detect_framework()
        database = self._detect_database()
        web_framework = self._detect_web_framework()

        self.project_info = ProjectInfo(
            project_type=project_type,
            language=language,
            version=version,
            dependencies=dependencies,
            build_tools=build_tools,
            test_frameworks=test_frameworks,
            has_docker=has_docker,
            has_kubernetes=has_kubernetes,
            has_ci_cd=has_ci_cd,
            framework=framework,
            database=database,
            web_framework=web_framework,
        )

        return self.project_info

    def _detect_project_type(self) -> str:
        """Detect the main project type"""
        if self._has_file("package.json"):
            return "nodejs"
        elif self._has_file("requirements.txt") or self._has_file(
            "pyproject.toml"
        ):
            return "python"
        elif self._has_file("pom.xml"):
            return "java"
        elif self._has_file("go.mod"):
            return "go"
        elif self._has_file("Cargo.toml"):
            return "rust"
        elif self._has_file("Makefile"):
            return "make"
        else:
            return "unknown"

    def _detect_language(self) -> str:
        """Detect the primary programming language"""
        type_mapping = {
            "nodejs": "javascript",
            "python": "python",
            "java": "java",
            "go": "go",
            "rust": "rust",
        }
        return type_mapping.get(self._detect_project_type(), "unknown")

    def _detect_version(self) -> Optional[str]:
        """Detect project version from various sources"""
        # Check package.json
        if self._has_file("package.json"):
            try:
                with open(self.repo_path / "package.json") as f:
                    data = json.load(f)
                    return data.get("version")
            except:
                pass

        # Check pyproject.toml
        if self._has_file("pyproject.toml"):
            try:
                with open(self.repo_path / "pyproject.toml") as f:
                    content = f.read()
                    # Simple regex-like search for version
                    import re

                    match = re.search(
                        r'version\s*=\s*["\']([^"\']+)["\']', content
                    )
                    if match:
                        return match.group(1)
            except:
                pass

        # Check pom.xml
        if self._has_file("pom.xml"):
            try:
                with open(self.repo_path / "pom.xml") as f:
                    content = f.read()
                    import re

                    match = re.search(r"<version>([^<]+)</version>", content)
                    if match:
                        return match.group(1)
            except:
                pass

        return None

    def _detect_dependencies(self) -> List[str]:
        """Detect project dependencies"""
        deps = []

        if self._has_file("requirements.txt"):
            try:
                with open(self.repo_path / "requirements.txt") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            deps.append(
                                line.split("==")[0]
                                .split(">=")[0]
                                .split("<=")[0]
                            )
            except:
                pass

        if self._has_file("package.json"):
            try:
                with open(self.repo_path / "package.json") as f:
                    data = json.load(f)
                    deps.extend(data.get("dependencies", {}).keys())
                    deps.extend(data.get("devDependencies", {}).keys())
            except:
                pass

        return list(set(deps))

    def _detect_build_tools(self) -> List[str]:
        """Detect build tools and package managers"""
        tools = []

        if self._has_file("package.json"):
            tools.append("npm")
        if self._has_file("yarn.lock"):
            tools.append("yarn")
        if self._has_file("pnpm-lock.yaml"):
            tools.append("pnpm")
        if self._has_file("requirements.txt"):
            tools.append("pip")
        if self._has_file("pyproject.toml"):
            tools.append("poetry")
        if self._has_file("pom.xml"):
            tools.append("maven")
        if self._has_file("build.gradle"):
            tools.append("gradle")
        if self._has_file("go.mod"):
            tools.append("go modules")
        if self._has_file("Cargo.toml"):
            tools.append("cargo")

        return tools

    def _detect_test_frameworks(self) -> List[str]:
        """Detect testing frameworks"""
        frameworks = []

        # Python
        if self._has_file("pytest.ini") or self._has_file("pyproject.toml"):
            frameworks.append("pytest")
        if self._has_file("tox.ini"):
            frameworks.append("tox")

        # Node.js
        if self._has_file("jest.config.js") or self._has_file(
            "jest.config.json"
        ):
            frameworks.append("jest")
        if self._has_file("mocha.opts") or self._has_file(".mocharc.json"):
            frameworks.append("mocha")

        # Java
        if self._has_file("pom.xml"):
            frameworks.append("junit")

        return frameworks

    def _detect_framework(self) -> Optional[str]:
        """Detect the main framework being used"""
        deps = self._detect_dependencies()

        # Python frameworks
        if "django" in deps:
            return "django"
        elif "flask" in deps:
            return "flask"
        elif "fastapi" in deps:
            return "fastapi"

        # Node.js frameworks
        if "express" in deps:
            return "express"
        elif "next" in deps:
            return "next.js"
        elif "react" in deps:
            return "react"
        elif "vue" in deps:
            return "vue.js"

        return None

    def _detect_database(self) -> Optional[str]:
        """Detect database dependencies"""
        deps = self._detect_dependencies()

        if "psycopg2" in deps or "postgresql" in deps:
            return "postgresql"
        elif "mysql-connector" in deps or "mysql" in deps:
            return "mysql"
        elif "sqlite3" in deps:
            return "sqlite"
        elif "redis" in deps:
            return "redis"
        elif "mongodb" in deps or "pymongo" in deps:
            return "mongodb"

        return None

    def _detect_web_framework(self) -> Optional[str]:
        """Detect web framework (alias for framework)"""
        return self._detect_framework()

    def _has_docker_files(self) -> bool:
        """Check if repository has Docker-related files"""
        return any(
            [
                self._has_file("Dockerfile"),
                self._has_file("docker-compose.yml"),
                self._has_file("docker-compose.yaml"),
                self._has_file(".dockerignore"),
            ]
        )

    def _has_kubernetes_files(self) -> bool:
        """Check if repository has Kubernetes-related files"""
        return any(
            [
                self._has_file("k8s"),
                self._has_file("kubernetes"),
                self._has_file("helm"),
                self._has_file("deployment.yaml"),
                self._has_file("service.yaml"),
            ]
        )

    def _has_ci_cd_files(self) -> bool:
        """Check if repository has CI/CD configuration files"""
        return any(
            [
                self._has_file(".github/workflows"),
                self._has_file(".gitlab-ci.yml"),
                self._has_file("Jenkinsfile"),
                self._has_file(".travis.yml"),
                self._has_file("azure-pipelines.yml"),
            ]
        )

    def _has_file(self, filename: str) -> bool:
        """Check if a file or directory exists"""
        return (self.repo_path / filename).exists()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the analysis"""
        if not self.project_info:
            self.analyze()

        return {
            "project_type": self.project_info.project_type,
            "language": self.project_info.language,
            "version": self.project_info.version,
            "dependencies_count": len(self.project_info.dependencies),
            "build_tools": self.project_info.build_tools,
            "test_frameworks": self.project_info.test_frameworks,
            "framework": self.project_info.framework,
            "database": self.project_info.database,
            "has_docker": self.project_info.has_docker,
            "has_kubernetes": self.project_info.has_kubernetes,
            "has_ci_cd": self.project_info.has_ci_cd,
        }
