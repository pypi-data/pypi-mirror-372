"""
CI/CD pipeline generator for DevOpsGenie
"""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Template


class CICDGenerator:
    """Generates CI/CD pipeline configurations"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Template]:
        """Load CI/CD templates"""
        return {
            "github_actions": Template(self._get_github_actions_template()),
            "gitlab_ci": Template(self._get_gitlab_ci_template()),
        }

    def generate(
        self,
        project_info: Dict[str, Any],
        output_path: str = None,
        ci_type: str = "github_actions",
    ) -> str:
        """Generate CI/CD configuration"""
        if ci_type not in self.templates:
            raise ValueError(f"Unsupported CI/CD type: {ci_type}")

        template = self.templates[ci_type]
        cicd_content = template.render(**project_info)

        if output_path:
            if ci_type == "github_actions":
                output_file = (
                    Path(output_path) / ".github" / "workflows" / "ci.yml"
                )
            else:
                output_file = Path(output_path) / ".gitlab-ci.yml"

            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                f.write(cicd_content)

        return cicd_content

    def _get_github_actions_template(self) -> str:
        return (
            "name: CI/CD Pipeline\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [ main, develop ]\n"
            "  pull_request:\n"
            "    branches: [ main ]\n\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "    - uses: actions/checkout@v4\n"
            "    {% if project_type == 'python' %}\n"
            "    - name: Set up Python\n"
            "      uses: actions/setup-python@v4\n"
            "      with:\n"
            "        python-version: '3.11'\n"
            "    - name: Install dependencies\n"
            "      run: |\n"
            "        pip install -r requirements.txt\n"
            "    - name: Run tests\n"
            "      run: |\n"
            "        {% if 'pytest' in test_frameworks %}\n"
            "        pytest\n"
            "        {% else %}\n"
            "        python -m unittest discover\n"
            "        {% endif %}\n"
            "    {% elif project_type == 'nodejs' %}\n"
            "    - name: Set up Node.js\n"
            "      uses: actions/setup-node@v4\n"
            "      with:\n"
            "        node-version: '18'\n"
            "    - name: Install dependencies\n"
            "      run: npm ci\n"
            "    - name: Run tests\n"
            "      run: npm test\n"
            "    {% endif %}\n\n"
            "  security:\n"
            "    runs-on: ubuntu-latest\n"
            "    needs: test\n"
            "    steps:\n"
            "    - uses: actions/checkout@v4\n"
            "    - name: Run Trivy vulnerability scanner\n"
            "      uses: aquasecurity/trivy-action@master\n"
            "      with:\n"
            "        scan-type: 'fs'\n"
            "        scan-ref: '.'\n"
            "        format: 'sarif'\n"
            "        output: 'trivy-results.sarif'\n\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    needs: [test, security]\n"
            "    if: github.ref == 'refs/heads/main'\n"
            "    steps:\n"
            "    - uses: actions/checkout@v4\n"
            "    - name: Build Docker image\n"
            "      run: docker build -t {{ project_name|default('app') }} .\n"
        )

    def _get_gitlab_ci_template(self) -> str:
        return (
            "stages:\n"
            "  - test\n"
            "  - security\n"
            "  - build\n"
            "  - deploy\n\n"
            "variables:\n"
            "  DOCKER_DRIVER: overlay2\n\n"
            "test:\n"
            "  stage: test\n"
            "  image: {% if project_type == 'python' %}python:3.11{% elif project_type == 'nodejs' %}node:18{% endif %}\n"
            "  script:\n"
            "    {% if project_type == 'python' %}\n"
            "    - pip install -r requirements.txt\n"
            "    - {% if 'pytest' in test_frameworks %}pytest{% else %}python -m unittest discover{% endif %}\n"
            "    {% elif project_type == 'nodejs' %}\n"
            "    - npm ci\n"
            "    - npm test\n"
            "    {% endif %}\n\n"
            "security:\n"
            "  stage: security\n"
            "  image: aquasec/trivy:latest\n"
            "  script:\n"
            "    - trivy fs --format sarif --output trivy-results.sarif .\n"
            "  artifacts:\n"
            "    reports:\n"
            "      sarif: trivy-results.sarif\n\n"
            "build:\n"
            "  stage: build\n"
            "  image: docker:latest\n"
            "  services:\n"
            "    - docker:dind\n"
            "  script:\n"
            "    - docker build -t {{ project_name|default('app') }} .\n"
        )
