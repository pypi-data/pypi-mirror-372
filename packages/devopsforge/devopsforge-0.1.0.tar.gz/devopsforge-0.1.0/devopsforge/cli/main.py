"""
Main CLI interface for DevOpsGenie
"""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..core.analyzer import RepositoryAnalyzer
from ..templates.cicd_generator import CICDGenerator
from ..templates.dockerfile_generator import DockerfileGenerator

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="DevOpsForge")
def cli():
    """🧞‍♂️ DevOpsForge - AI-powered DevOps companion"""
    pass


@cli.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output directory for analysis results",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "table", "summary"]),
    default="table",
    help="Output format",
)
def analyze(repo_path, output, format):
    """Analyze a repository and detect project characteristics"""
    console.print(Panel.fit("🔍 Analyzing Repository", style="bold blue"))

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing repository...", total=None)

            analyzer = RepositoryAnalyzer(repo_path)
            project_info = analyzer.analyze()

            progress.update(task, completed=True)

        if format == "json":
            result = {
                "repository_path": str(repo_path),
                "analysis": analyzer.get_summary(),
                "detailed_info": {
                    "project_type": project_info.project_type,
                    "language": project_info.language,
                    "version": project_info.version,
                    "dependencies": project_info.dependencies,
                    "build_tools": project_info.build_tools,
                    "test_frameworks": project_info.test_frameworks,
                    "framework": project_info.framework,
                    "database": project_info.database,
                    "has_docker": project_info.has_docker,
                    "has_kubernetes": project_info.has_kubernetes,
                    "has_ci_cd": project_info.has_ci_cd,
                },
            }

            if output:
                output_file = Path(output) / "analysis.json"
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, "w") as f:
                    json.dump(result, f, indent=2)
                console.print(f"✅ Analysis saved to {output_file}")
            else:
                console.print_json(data=result)

        elif format == "table":
            table = Table(title="Repository Analysis Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            summary = analyzer.get_summary()
            for key, value in summary.items():
                if isinstance(value, list):
                    value = ", ".join(map(str, value)) if value else "None"
                table.add_row(
                    key.replace("_", " ").title(),
                    str(value) if value else "None",
                )

            console.print(table)

        else:  # summary format
            summary = analyzer.get_summary()
            console.print(f"📁 Repository: {repo_path}")
            console.print(f"🔧 Project Type: {summary['project_type']}")
            console.print(f"💻 Language: {summary['language']}")
            console.print(f"📦 Dependencies: {summary['dependencies_count']}")
            console.print(
                f"🛠️ Build Tools: {', '.join(summary['build_tools']) if summary['build_tools'] else 'None'}"
            )
            console.print(
                f"🧪 Test Frameworks: {', '.join(summary['test_frameworks']) if summary['test_frameworks'] else 'None'}"
            )
            console.print(f"🚀 Framework: {summary['framework'] or 'None'}")
            console.print(f"🗄️ Database: {summary['database'] or 'None'}")
            console.print(
                f"🐳 Has Docker: {'✅' if summary['has_docker'] else '❌'}"
            )
            console.print(
                f"☸️ Has Kubernetes: {'✅' if summary['has_kubernetes'] else '❌'}"
            )
            console.print(
                f"🔄 Has CI/CD: {'✅' if summary['has_ci_cd'] else '❌'}"
            )

    except Exception as e:
        console.print(f"❌ Error analyzing repository: {e}", style="bold red")
        raise click.Abort()


@cli.command()
@click.argument("repo_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    required=True,
    help="Output directory for generated files",
)
@click.option(
    "--ci-type",
    type=click.Choice(["github_actions", "gitlab_ci"]),
    default="github_actions",
    help="CI/CD type to generate",
)
@click.option(
    "--dockerfile/--no-dockerfile", default=True, help="Generate Dockerfile"
)
@click.option("--cicd/--no-cicd", default=True, help="Generate CI/CD pipeline")
def generate(repo_path, output, ci_type, dockerfile, cicd):
    """Generate DevOps configurations for a repository"""
    console.print(
        Panel.fit("🚀 Generating DevOps Configurations", style="bold green")
    )

    try:
        # Analyze repository first
        analyzer = RepositoryAnalyzer(repo_path)
        project_info = analyzer.analyze()

        # Convert to dict for template rendering
        project_dict = {
            "project_type": project_info.project_type,
            "language": project_info.language,
            "version": project_info.version,
            "dependencies": project_info.dependencies,
            "build_tools": project_info.build_tools,
            "test_frameworks": project_info.test_frameworks,
            "framework": project_info.framework,
            "database": project_info.database,
            "project_name": Path(repo_path).name,
        }

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # Generate Dockerfile
        if dockerfile:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "Generating Dockerfile...", total=None
                )

                dockerfile_gen = DockerfileGenerator()
                dockerfile_gen.generate(project_dict, str(output_path))

                progress.update(task, completed=True)

            generated_files.append("Dockerfile")
            console.print("✅ Dockerfile generated")

        # Generate CI/CD pipeline
        if cicd:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Generating {ci_type} pipeline...", total=None
                )

                cicd_gen = CICDGenerator()
                cicd_gen.generate(project_dict, str(output_path), ci_type)

                progress.update(task, completed=True)

            if ci_type == "github_actions":
                generated_files.append(".github/workflows/ci.yml")
            else:
                generated_files.append(".gitlab-ci.yml")

            console.print(f"✅ {ci_type} pipeline generated")

        # Summary
        console.print(
            f"\n🎉 Successfully generated {len(generated_files)} file(s) in {output_path}"
        )
        for file in generated_files:
            console.print(f"   📄 {file}")

        # Optimization suggestions
        console.print("\n💡 Optimization Suggestions:")
        if project_info.project_type == "python":
            console.print(
                "   • Use multi-stage Docker builds to reduce image size"
            )
            console.print(
                "   • Consider using .dockerignore to exclude unnecessary files"
            )
            console.print("   • Use Alpine-based images for smaller footprint")
        elif project_info.project_type == "nodejs":
            console.print("   • Use npm ci instead of npm install in CI/CD")
            console.print(
                "   • Consider using yarn for faster dependency installation"
            )
            console.print("   • Use .dockerignore to exclude node_modules")

        if not project_info.has_docker:
            console.print(
                "   • Add .dockerignore file to optimize Docker builds"
            )

        if not project_info.has_ci_cd:
            console.print(
                "   • Consider setting up automated testing in CI/CD"
            )

    except Exception as e:
        console.print(
            f"❌ Error generating configurations: {e}", style="bold red"
        )
        raise click.Abort()


@cli.command()
@click.argument("repo_path", type=click.Path(exists=True))
def suggest(repo_path):
    """Get optimization suggestions for a repository"""
    console.print(
        Panel.fit("💡 Optimization Suggestions", style="bold yellow")
    )

    try:
        analyzer = RepositoryAnalyzer(repo_path)
        project_info = analyzer.analyze()

        console.print(f"📁 Repository: {repo_path}")
        console.print(f"🔧 Project Type: {project_info.project_type}")
        console.print()

        # Docker optimizations
        if not project_info.has_docker:
            console.print("🐳 Docker Optimizations:")
            console.print(
                "   • Create a multi-stage Dockerfile for smaller images"
            )
            console.print(
                "   • Use .dockerignore to exclude unnecessary files"
            )
            console.print(
                "   • Consider using distroless images for production"
            )

        # CI/CD optimizations
        if not project_info.has_ci_cd:
            console.print("🔄 CI/CD Optimizations:")
            console.print("   • Set up automated testing pipeline")
            console.print("   • Add security scanning with Trivy")
            console.print("   • Implement automated dependency updates")

        # Language-specific suggestions
        if project_info.project_type == "python":
            console.print("🐍 Python Optimizations:")
            console.print("   • Use virtual environments in CI/CD")
            console.print(
                "   • Consider using Poetry for dependency management"
            )
            console.print("   • Add type checking with mypy")

        elif project_info.project_type == "nodejs":
            console.print("🟢 Node.js Optimizations:")
            console.print("   • Use npm ci in CI/CD for faster builds")
            console.print("   • Consider using pnpm for smaller node_modules")
            console.print("   • Add ESLint and Prettier for code quality")

        # Security suggestions
        console.print("🛡️ Security Optimizations:")
        console.print("   • Regular dependency vulnerability scanning")
        console.print("   • Container image scanning with Trivy")
        console.print("   • Implement least privilege principle in containers")

        # Performance suggestions
        console.print("⚡ Performance Optimizations:")
        console.print("   • Use dependency caching in CI/CD")
        console.print("   • Implement parallel testing")
        console.print("   • Use build caching for Docker images")

    except Exception as e:
        console.print(f"❌ Error analyzing repository: {e}", style="bold red")
        raise click.Abort()


if __name__ == "__main__":
    cli()
