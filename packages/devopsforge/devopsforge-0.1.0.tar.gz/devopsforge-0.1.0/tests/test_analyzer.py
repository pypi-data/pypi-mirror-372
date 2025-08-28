"""
Tests for the RepositoryAnalyzer class
"""

from pathlib import Path

from devopsforge.core.analyzer import ProjectInfo, RepositoryAnalyzer


class TestRepositoryAnalyzer:
    """Test cases for RepositoryAnalyzer"""

    def test_init(self):
        """Test analyzer initialization"""
        analyzer = RepositoryAnalyzer("test_path")
        assert analyzer.repo_path == Path("test_path")
        assert analyzer.project_info is None

    def test_detect_project_type_python(self, sample_python_project):
        """Test Python project type detection"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        project_type = analyzer._detect_project_type()
        assert project_type == "python"

    def test_detect_language_python(self, sample_python_project):
        """Test Python language detection"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        language = analyzer._detect_language()
        assert language == "python"

    def test_detect_dependencies(self, sample_python_project):
        """Test dependency detection"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        dependencies = analyzer._detect_dependencies()
        assert "flask" in dependencies
        assert "pytest" in dependencies

    def test_detect_build_tools(self, sample_python_project):
        """Test build tool detection"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        build_tools = analyzer._detect_build_tools()
        assert "pip" in build_tools

    def test_detect_test_frameworks(self, sample_python_project):
        """Test test framework detection"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        test_frameworks = analyzer._detect_test_frameworks()
        assert "pytest" in test_frameworks

    def test_detect_framework(self, sample_python_project):
        """Test framework detection"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        framework = analyzer._detect_framework()
        assert framework == "flask"

    def test_has_file(self, sample_python_project):
        """Test file existence checking"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        assert analyzer._has_file("requirements.txt")
        assert analyzer._has_file("main.py")
        assert not analyzer._has_file("nonexistent.py")

    def test_analyze_complete(self, sample_python_project):
        """Test complete analysis"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        project_info = analyzer.analyze()

        assert isinstance(project_info, ProjectInfo)
        assert project_info.project_type == "python"
        assert project_info.language == "python"
        assert project_info.framework == "flask"
        assert "flask" in project_info.dependencies
        assert "pip" in project_info.build_tools
        assert "pytest" in project_info.test_frameworks

    def test_get_summary(self, sample_python_project):
        """Test summary generation"""
        analyzer = RepositoryAnalyzer(str(sample_python_project))
        summary = analyzer.get_summary()

        assert "project_type" in summary
        assert "language" in summary
        assert "framework" in summary
        assert summary["project_type"] == "python"
        assert summary["language"] == "python"


class TestProjectInfo:
    """Test cases for ProjectInfo dataclass"""

    def test_project_info_creation(self):
        """Test ProjectInfo object creation"""
        info = ProjectInfo(
            project_type="python",
            language="python",
            version="3.11",
            dependencies=["flask"],
            build_tools=["pip"],
            test_frameworks=["pytest"],
            framework="flask",
            web_framework="flask",
            database=None,
            has_docker=False,
            has_kubernetes=False,
            has_ci_cd=False,
        )

        assert info.project_type == "python"
        assert info.language == "python"
        assert info.version == "3.11"
        assert info.dependencies == ["flask"]
        assert info.build_tools == ["pip"]
        assert info.test_frameworks == ["pytest"]
        assert info.framework == "flask"
        assert info.database is None
        assert info.has_docker is False
        assert info.has_kubernetes is False
        assert info.has_ci_cd is False
