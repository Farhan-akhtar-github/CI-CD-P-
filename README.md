# CI/CD Flask Application

![CI Pipeline](https://github.com/Farhan-akhtar-github/CI-CD-P-/actions/workflows/ci.yml/badge.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

A production-ready Flask application with a complete CI/CD pipeline using GitHub Actions, Docker, and AWS EC2.

## Highlights

- Production-style CI/CD pipeline with parallel jobs for faster feedback
- Dockerized Flask application using Gunicorn
- Security scanning using Trivy
- Docker image artifact sharing across CI jobs
- Automatic deployment to AWS EC2
- Zero-downtime deployment with health checks
- Container auto-restart using Docker restart policies

## Architecture

```
Developer Push
      │
      ▼
GitHub Repository
      │
      ▼
GitHub Actions CI
 ├ Lint ──────┐
 │            ├──▶ Build ──┬──▶ Scan ─────────┐
 └ Test ──────┘            │                   ├──▶ Push
                           └──▶ Smoke Test ────┘
      │
      ▼
Docker Hub
      │
      ▼
GitHub Actions CD
      │
      ▼
AWS EC2
      │
      ▼
Docker Container
      │
      ▼
Health Check
```

## Features

- **Flask** web application with app factory pattern
- **Gunicorn** WSGI server for production
- **Security headers** (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- **Dockerized** with non-root user and health checks
- **CI pipeline** — parallel lint & test, build, parallel scan & smoke test, and push
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

Triggered on every push to `main`. The pipeline is organized into **four stages** with **parallel jobs** to maximize speed without sacrificing safety:

```
┌─────────────────────────────────────────────────────┐
│  Stage 1 (parallel)  │  lint ───┐                   │
│                      │          ├──▶ Stage 2: build  │
│                      │  test ───┘         │          │
│                      │              ┌─────┴──────┐   │
│  Stage 3 (parallel)  │           scan       smoke-test│
│                      │              └─────┬──────┘   │
│  Stage 4             │                  push         │
└─────────────────────────────────────────────────────┘
```

| Stage | Jobs | Runs | Description |
|-------|------|------|-------------|
| 1 | **Lint** and **Test** | In parallel | Flake8 static analysis and Pytest unit tests run simultaneously |
| 2 | **Build** | After Stage 1 | Docker image built with layer caching, tagged `latest` and commit SHA, saved as an artifact |
| 3 | **Scan** and **Smoke Test** | In parallel | Trivy vulnerability scan (fails on CRITICAL/HIGH) and container health-check run simultaneously, both loading the artifact from Stage 2 |
| 4 | **Push** | After Stage 3 | Publish image to Docker Hub once scan and smoke test both pass |

#### Why parallel jobs?

- **Faster feedback** — Lint and test run at the same time, so developers get results sooner.
- **Independent checks** — Security scanning and smoke testing have no dependency on each other, so they run concurrently after the build.
- **Artifact sharing** — The Docker image is built once in Stage 2 and shared via `actions/upload-artifact` / `actions/download-artifact`, avoiding redundant builds while still enabling parallel consumers.
- **Fail-fast safety** — If either parallel job in a stage fails, the subsequent stage is skipped entirely.

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
