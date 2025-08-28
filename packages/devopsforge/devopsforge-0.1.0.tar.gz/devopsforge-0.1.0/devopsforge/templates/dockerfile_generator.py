"""
Dockerfile template generator for DevOpsGenie
"""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Template


class DockerfileGenerator:
    """Generates Dockerfiles based on project analysis"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Template]:
        """Load Jinja2 templates for different project types"""
        return {
            "python": Template(self._get_python_template()),
            "nodejs": Template(self._get_nodejs_template()),
            "java": Template(self._get_java_template()),
            "go": Template(self._get_go_template()),
            "rust": Template(self._get_rust_template()),
        }

    def generate(
        self, project_info: Dict[str, Any], output_path: str = None
    ) -> str:
        """Generate a Dockerfile based on project information"""
        project_type = project_info.get("project_type", "unknown")

        if project_type not in self.templates:
            raise ValueError(f"Unsupported project type: {project_type}")

        template = self.templates[project_type]
        dockerfile_content = template.render(**project_info)

        if output_path:
            output_file = Path(output_path) / "Dockerfile"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                f.write(dockerfile_content)

        return dockerfile_content

    def _get_python_template(self) -> str:
        return (
            "# Multi-stage Python Dockerfile\n"
            "FROM python:{{ python_version|default('3.11-slim') }} as builder\n\n"
            "# Set environment variables\n"
            "ENV PYTHONDONTWRITEBYTECODE=1\n"
            "ENV PYTHONUNBUFFERED=1\n\n"
            "# Install system dependencies\n"
            "RUN apt-get update && apt-get install -y \\\n"
            "    gcc \\\n"
            "    g++ \\\n"
            "    && rm -rf /var/lib/apt/lists/*\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Install Python dependencies\n"
            "{% if build_tools and 'poetry' in build_tools %}\n"
            "COPY pyproject.toml poetry.lock ./\n"
            "RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev\n"
            "{% else %}\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "{% endif %}\n\n"
            "# Production stage\n"
            "FROM python:{{ python_version|default('3.11-slim') }}\n\n"
            "# Set environment variables\n"
            "ENV PYTHONDONTWRITEBYTECODE=1\n"
            "ENV PYTHONUNBUFFERED=1\n\n"
            "# Create non-root user\n"
            "RUN adduser --disabled-password --gecos '' appuser\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy Python dependencies from builder\n"
            "COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages\n"
            "COPY --from=builder /usr/local/bin /usr/local/bin\n\n"
            "# Copy application code\n"
            "COPY . .\n\n"
            "# Change ownership\n"
            "RUN chown -R appuser:appuser /app\n"
            "USER appuser\n\n"
            "# Expose port\n"
            "{% if framework == 'django' or framework == 'flask' or framework == 'fastapi' %}\n"
            "EXPOSE 8000\n"
            "{% endif %}\n\n"
            "# Health check\n"
            "HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\\n"
            "    CMD python -c \"import requests; requests.get('http://localhost:8000/health')\" || exit 1\n\n"
            "# Run the application\n"
            "{% if framework == 'django' %}\n"
            'CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]\n'
            "{% elif framework == 'flask' %}\n"
            'CMD ["python", "app.py"]\n'
            "{% elif framework == 'fastapi' %}\n"
            'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]\n'
            "{% else %}\n"
            'CMD ["python", "main.py"]\n'
            "{% endif %}\n"
        )

    def _get_nodejs_template(self) -> str:
        return (
            "# Multi-stage Node.js Dockerfile\n"
            "FROM node:{{ node_version|default('18-alpine') }} as builder\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy package files\n"
            "COPY package*.json ./\n"
            "{% if build_tools and 'yarn' in build_tools %}\n"
            "COPY yarn.lock ./\n"
            "{% elif build_tools and 'pnpm' in build_tools %}\n"
            "COPY pnpm-lock.yaml ./\n\n"
            "# Install pnpm\n"
            "RUN npm install -g pnpm\n"
            "{% endif %}\n\n"
            "# Install dependencies\n"
            "{% if build_tools and 'yarn' in build_tools %}\n"
            "RUN yarn install --frozen-lockfile\n"
            "{% elif build_tools and 'pnpm' in build_tools %}\n"
            "RUN pnpm install --frozen-lockfile\n"
            "{% else %}\n"
            "RUN npm ci --only=production\n"
            "{% endif %}\n\n"
            "# Production stage\n"
            "FROM node:{{ node_version|default('18-alpine') }}\n\n"
            "# Install dumb-init for proper signal handling\n"
            "RUN apk add --no-cache dumb-init\n\n"
            "# Create non-root user\n"
            "RUN addgroup -g 1001 -S nodejs\n"
            "RUN adduser -S nodejs -u 1001\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy dependencies from builder\n"
            "COPY --from=builder /app/node_modules ./node_modules\n\n"
            "# Copy application code\n"
            "COPY . .\n\n"
            "# Change ownership\n"
            "RUN chown -R nodejs:nodejs /app\n"
            "USER nodejs\n\n"
            "# Expose port\n"
            "{% if framework == 'express' or framework == 'next.js' %}\n"
            "EXPOSE 3000\n"
            "{% endif %}\n\n"
            "# Health check\n"
            "HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\\n"
            "    CMD node -e \"require('http').get('http://localhost:3000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })\" || exit 1\n\n"
            "# Run the application\n"
            "{% if framework == 'next.js' %}\n"
            'CMD ["dumb-init", "npm", "start"]\n'
            "{% else %}\n"
            'CMD ["dumb-init", "node", "index.js"]\n'
            "{% endif %}\n"
        )

    def _get_java_template(self) -> str:
        return (
            "# Multi-stage Java Dockerfile\n"
            "FROM maven:{{ maven_version|default('3.8.6-openjdk-17') }} as builder\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy pom.xml\n"
            "COPY pom.xml .\n\n"
            "# Download dependencies\n"
            "RUN mvn dependency:go-offline -B\n\n"
            "# Copy source code\n"
            "COPY src ./src\n\n"
            "# Build the application\n"
            "RUN mvn clean package -DskipTests\n\n"
            "# Production stage\n"
            "FROM openjdk:{{ java_version|default('17-jre-slim') }}\n\n"
            "# Install dumb-init\n"
            "RUN apt-get update && apt-get install -y dumb-init && \\\n"
            "    rm -rf /var/lib/apt/lists/*\n\n"
            "# Create non-root user\n"
            "RUN groupadd -r appuser && useradd -r -g appuser appuser\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy JAR file from builder\n"
            "COPY --from=builder /app/target/*.jar app.jar\n\n"
            "# Change ownership\n"
            "RUN chown -R appuser:appuser /app\n"
            "USER appuser\n\n"
            "# Expose port\n"
            "EXPOSE 8080\n\n"
            "# Health check\n"
            "HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\\n"
            "    CMD java -cp app.jar org.springframework.boot.loader.JarLauncher --spring.profiles.active=docker || exit 1\n\n"
            "# Run the application\n"
            'ENTRYPOINT ["dumb-init", "java", "-jar", "app.jar"]\n'
        )

    def _get_go_template(self) -> str:
        return (
            "# Multi-stage Go Dockerfile\n"
            "FROM golang:{{ go_version|default('1.21-alpine') }} as builder\n\n"
            "# Install build dependencies\n"
            "RUN apk add --no-cache git ca-certificates \\\n"
            "    tzdata\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy go mod files\n"
            "COPY go.mod go.sum ./\n\n"
            "# Download dependencies\n"
            "RUN go mod download\n\n"
            "# Copy source code\n"
            "COPY . .\n\n"
            "# Build the application\n"
            "RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo \\\n"
            "    -o main .\n\n"
            "# Production stage\n"
            "FROM alpine:latest\n\n"
            "# Install dumb-init and ca-certificates\n"
            "RUN apk --no-cache add dumb-init ca-certificates \\\n"
            "    tzdata\n\n"
            "# Create non-root user\n"
            "RUN addgroup -g 1001 -S appuser\n"
            "RUN adduser -S appuser -u 1001\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy binary from builder\n"
            "COPY --from=builder /app/main .\n\n"
            "# Change ownership\n"
            "RUN chown -R appuser:appuser /app\n"
            "USER appuser\n\n"
            "# Expose port\n"
            "EXPOSE 8080\n\n"
            "# Health check\n"
            "HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\\n"
            "    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1\n\n"
            "# Run the application\n"
            'ENTRYPOINT ["dumb-init", "./main"]\n'
        )

    def _get_rust_template(self) -> str:
        return (
            "# Multi-stage Rust Dockerfile\n"
            "FROM rust:{{ rust_version|default('1.75-slim') }} as builder\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy Cargo files\n"
            "COPY Cargo.toml Cargo.lock ./\n\n"
            "# Create dummy main.rs to build dependencies\n"
            'RUN mkdir src && echo "fn main() {}" > src/main.rs\n'
            "RUN cargo build --release\n"
            "RUN rm -rf src\n\n"
            "# Copy source code\n"
            "COPY . .\n\n"
            "# Build the application\n"
            "RUN cargo build --release\n\n"
            "# Production stage\n"
            "FROM debian:bookworm-slim\n\n"
            "# Install dumb-init and ca-certificates\n"
            "RUN apt-get update && apt-get install -y dumb-init \\\n"
            "    ca-certificates && rm -rf /var/lib/apt/lists/*\n\n"
            "# Create non-root user\n"
            "RUN groupadd -r appuser && useradd -r -g appuser appuser\n\n"
            "# Set work directory\n"
            "WORKDIR /app\n\n"
            "# Copy binary from builder\n"
            "COPY --from=builder /app/target/release/\\\n"
            "    {{ project_name|default('app') }} .\n\n"
            "# Change ownership\n"
            "RUN chown -R appuser:appuser /app\n"
            "USER appuser\n\n"
            "# Expose port\n"
            "EXPOSE 8080\n\n"
            "# Health check\n"
            "HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\\n"
            "    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1\n\n"
            "# Run the application\n"
            'ENTRYPOINT ["dumb-init", \\\n'
            "    \"./{{ project_name|default('app') }}\"]\n"
        )
