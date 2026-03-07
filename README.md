# CI/CD Flask Application

A production-ready Flask application with a complete CI/CD pipeline using GitHub Actions, Docker, and AWS EC2.

## Features

- **Flask** web application with app factory pattern
- **Gunicorn** WSGI server for production
- **Security headers** (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- **Dockerized** with non-root user and health checks
- **CI pipeline** — lint, test, build, security scan, and push
- **CD pipeline** — automatic deployment to EC2 on successful CI

## Project Structure

```
├── .github/workflows/
│   ├── ci.yml              # CI pipeline (lint, test, build, scan, push)
│   └── cd.yml              # CD pipeline (deploy to EC2)
├── tests/
│   └── test_app.py         # Unit tests
├── .dockerignore
├── .flake8                 # Flake8 linting config
├── .gitignore
├── .trivyignore            # Trivy vulnerability exceptions
├── Dockerfile
├── app.py                  # Flask application
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Development dependencies
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized usage)

### Local Setup

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run the application
python app.py
```

The app will be available at `http://localhost:5000`.

### Endpoints

| Endpoint  | Method | Description          |
|-----------|--------|----------------------|
| `/`       | GET    | Home page            |
| `/health` | GET    | Health check (JSON)  |

## Development

### Linting

```bash
flake8 app.py tests/
```

### Testing

```bash
pytest tests/ -v
```

### Configuration

| Environment Variable | Default | Description              |
|----------------------|---------|--------------------------|
| `LOG_LEVEL`          | `INFO`  | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

## Docker

### Build and Run

```bash
docker build -t ci-cd-clean-app .
docker run -d -p 5000:5000 --name ci-cd-clean-app ci-cd-clean-app
```

The container runs as a non-root user and includes a health check on the `/health` endpoint.

## CI/CD Pipeline

### CI (`.github/workflows/ci.yml`)

Triggered on every push to `main`:

1. **Lint** — Flake8 static analysis
2. **Test** — Pytest unit tests
3. **Build** — Docker image with layer caching (tagged `latest` and commit SHA)
4. **Smoke test** — Run container and verify `/health` endpoint
5. **Scan** — Trivy vulnerability scanner (fails on CRITICAL/HIGH)
6. **Push** — Publish image to Docker Hub

### CD (`.github/workflows/cd.yml`)

Triggered automatically when the CI pipeline succeeds on `main`. Uses a **zero-downtime deployment** strategy:

1. Pull the new Docker image while the old container is still serving traffic
2. Start the new container on a temporary port (`5001`)
3. Run health checks against the new container (up to 30 attempts)
4. If healthy — stop old container, launch new container on production port (`5000`)
5. If unhealthy — remove new container, keep old container running (automatic rollback)
6. Verify the production container is healthy after the swap

### Required Secrets

| Secret            | Description                  |
|-------------------|------------------------------|
| `DOCKER_USERNAME` | Docker Hub username          |
| `DOCKER_PASSWORD` | Docker Hub password or token |
| `EC2_HOST`        | EC2 instance hostname/IP     |
| `EC2_USER`        | EC2 SSH username             |
| `EC2_KEY`         | EC2 SSH private key          |
