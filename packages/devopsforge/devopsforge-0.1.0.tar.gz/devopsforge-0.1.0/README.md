# DevOpsForge 🔨

[![PyPI version](https://badge.fury.io/py/devopsforge.svg)](https://badge.fury.io/py/devopsforge)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)

> Professional DevOps automation tool that automatically generates production-ready CI/CD pipelines, Dockerfiles, and Kubernetes configurations.

## ✨ Features

- 🔍 **Smart Repository Analysis** - Automatically detects project type, language, framework, and dependencies
- 🐳 **Intelligent Dockerfile Generation** - Creates optimized, multi-stage Dockerfiles with security best practices
- 🔄 **Automated CI/CD Creation** - Generates GitHub Actions and GitLab CI pipelines with security scanning
- 🛡️ **DevSecOps Integration** - Built-in Trivy vulnerability scanning and security best practices
- 💡 **Optimization Engine** - Provides tailored recommendations for performance and security improvements
- 🌍 **Multi-Language Support** - Python, Node.js, Java, Go, Rust, and more

## 🚀 Quick Start

### Installation

```bash
pip install devopsforge
```

### Basic Usage

```bash
# Analyze a repository
devopsforge analyze /path/to/project

# Generate DevOps configurations
devopsforge generate /path/to/project -o ./devops

# Get optimization suggestions
devopsforge suggest /path/to/project
```

## 📋 Commands

### `analyze` Command

Analyzes a repository and detects project characteristics.

```bash
devopsforge analyze <repo_path> [options]
```

**Options:**
- `--output, -o`: Output directory for analysis results
- `--format, -f`: Output format (json, table, summary)

**Examples:**
```bash
# Basic analysis
devopsforge analyze my-project

# Save analysis to file
devopsforge analyze my-project -o ./results -f json

# Get summary format
devopsforge analyze my-project -f summary
```

### `generate` Command

Generates DevOps configurations based on repository analysis.

```bash
devopsforge generate <repo_path> -o <output_dir> [options]
```

**Options:**
- `--output, -o`: Output directory (required)
- `--ci-type`: CI/CD type (github_actions, gitlab_ci)
- `--dockerfile/--no-dockerfile`: Generate Dockerfile
- `--cicd/--no-cicd`: Generate CI/CD pipeline

**Examples:**
```bash
# Generate everything
devopsforge generate my-project -o ./devops

# Generate only Dockerfile
devopsforge generate my-project -o ./devops --no-cicd

# Generate GitLab CI instead of GitHub Actions
devopsforge generate my-project -o ./devops --ci-type gitlab_ci
```

### `suggest` Command

Provides optimization suggestions for a repository.

```bash
devopsforge suggest <repo_path>
```

## 🔧 Supported Technologies

### Programming Languages
- **Python**: Django, Flask, FastAPI, pip, poetry, pytest
- **Node.js**: Express, Next.js, React, Vue.js, npm, yarn, pnpm, Jest
- **Java**: Maven, Gradle, JUnit
- **Go**: Go modules
- **Rust**: Cargo

### DevOps Tools
- **Containers**: Docker, multi-stage builds
- **CI/CD**: GitHub Actions, GitLab CI
- **Security**: Trivy vulnerability scanner
- **Orchestration**: Kubernetes-ready configurations

## 🏗️ Architecture

```
devopsforge/
├── core/                    # Core analysis engine
│   └── analyzer.py         # Repository analyzer
├── templates/               # Jinja2 template system
│   ├── dockerfile_generator.py    # Dockerfile templates
│   └── cicd_generator.py          # CI/CD templates
├── cli/                     # Command-line interface
│   └── main.py             # CLI commands
└── __main__.py             # Package entry point
```

## 🛠️ Technology Stack

- **Language**: Python 3.8+
- **Template Engine**: Jinja2
- **CLI Framework**: Click
- **UI Enhancement**: Rich (for beautiful terminal output)
- **Security**: Trivy integration
- **Testing**: pytest, unittest support

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install devopsforge
```

### From Source

```bash
git clone https://github.com/devopsforge/devopsforge.git
cd devopsforge
pip install -e .
```

## 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Run the test script
python test_devopsforge.py
```

## 📚 Documentation

- **[Usage Guide](USAGE.md)** - Comprehensive usage examples and configuration options
- **[Contributing Guidelines](CONTRIBUTING.md)** - How to contribute to the project
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines
- **[Changelog](CHANGELOG.md)** - Version history and changes

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/devopsforge/devopsforge.git
cd devopsforge
pip install -r requirements.txt
pip install -e .
```

### Adding New Project Types

1. Update `RepositoryAnalyzer` in `core/analyzer.py`
2. Create Jinja2 templates in `templates/` directory
3. Add CLI support and tests
4. Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Jinja2](https://jinja.palletsprojects.com/) - Template engine
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [Trivy](https://trivy.dev/) - Security scanning

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/devopsforge/devopsforge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/devopsforge/devopsforge/discussions)
- **Documentation**: [USAGE.md](USAGE.md)

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=devopsforge/devopsforge&type=Date)](https://star-history.com/#devopsforge/devopsforge&Date)

---

**Made with ❤️ by the DevOpsForge community**
