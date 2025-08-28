"""
Tests for the CLI interface
"""

from click.testing import CliRunner

from devopsforge.cli.main import cli


class TestCLI:
    """Test cases for CLI commands"""

    def test_cli_help(self):
        """Test CLI help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "DevOpsForge" in result.output
        assert "analyze" in result.output
        assert "generate" in result.output
        assert "suggest" in result.output

    def test_analyze_command_help(self):
        """Test analyze command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "analyze" in result.output
        assert "REPO_PATH" in result.output

    def test_generate_command_help(self):
        """Test generate command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "--help"])
        assert result.exit_code == 0
        assert "generate" in result.output
        assert "output" in result.output

    def test_suggest_command_help(self):
        """Test suggest command help"""
        runner = CliRunner()
        result = runner.invoke(cli, ["suggest", "--help"])
        assert result.exit_code == 0
        assert "suggest" in result.output
        assert "REPO_PATH" in result.output

    def test_analyze_command_missing_path(self):
        """Test analyze command with missing path"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze"])
        assert result.exit_code != 0  # Should fail without path

    def test_generate_command_missing_path(self):
        """Test generate command with missing path"""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate"])
        assert result.exit_code != 0  # Should fail without path

    def test_generate_command_missing_output(self):
        """Test generate command with missing output"""
        runner = CliRunner()
        result = runner.invoke(cli, ["generate", "test_path"])
        assert result.exit_code != 0  # Should fail without output

    def test_suggest_command_missing_path(self):
        """Test suggest command with missing path"""
        runner = CliRunner()
        result = runner.invoke(cli, ["suggest"])
        assert result.exit_code != 0  # Should fail without path


class TestCLIWithMockProject:
    """Test CLI with mock project (integration tests)"""

    def test_analyze_real_project(self, sample_python_project):
        """Test analyze command with real project"""
        runner = CliRunner()
        result = runner.invoke(cli, ["analyze", str(sample_python_project)])

        # Should succeed
        assert result.exit_code == 0
        assert "Project Type" in result.output
        assert "Language" in result.output
        assert "Framework" in result.output

    def test_generate_real_project(
        self, sample_python_project, temp_project_dir
    ):
        """Test generate command with real project"""
        output_dir = temp_project_dir / "output"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["generate", str(sample_python_project), "-o", str(output_dir)],
        )

        # Should succeed
        assert result.exit_code == 0
        assert "Successfully generated" in result.output

        # Check if files were created
        assert (output_dir / "Dockerfile").exists()
        assert (output_dir / ".github" / "workflows" / "ci.yml").exists()

    def test_suggest_real_project(self, sample_python_project):
        """Test suggest command with real project"""
        runner = CliRunner()
        result = runner.invoke(cli, ["suggest", str(sample_python_project)])

        # Should succeed
        assert result.exit_code == 0
        assert (
            "Suggestions" in result.output
            or "recommendations" in result.output.lower()
        )
