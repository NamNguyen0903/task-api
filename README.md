# Task API — Automated CI/CD Pipeline

A Python FastAPI backend project demonstrating an end-to-end CI/CD workflow using GitHub Actions, Docker, GitHub Container Registry (GHCR), and Render.

The project focuses on automated testing, multi-platform container builds, continuous deployment, deployment monitoring, health verification, and rollback decision testing.

## 1. Project Overview

**Task API** is a backend development and DevOps practice project built with Python and FastAPI.

The primary objective is to automate the software delivery process, from code integration to cloud deployment, while introducing deployment verification and safe recovery practices.

### Key Features

- REST API built with FastAPI
- Automated testing with Pytest
- CI/CD pipelines using GitHub Actions
- Docker containerization
- Multi-platform Docker images (AMD64 and ARM64)
- Docker image publishing to GHCR
- Automated cloud deployment to Render
- Deployment monitoring through the Render API
- Health checks and Docker image verification
- Python-based rollback decision logic
- Automated failure scenario testing

## 2. Technology Stack

| Category | Technology |
|---|---|
| Language | Python 3.11 |
| Backend Framework | FastAPI |
| ASGI Server | Uvicorn |
| Testing | Pytest, HTTPX |
| Version Control | Git, GitHub |
| CI/CD | GitHub Actions |
| Containerization | Docker, Docker Buildx |
| Container Registry | GitHub Container Registry |
| Cloud Hosting | Render |
| Deployment Verification | Render API, cURL, jq |
| Rollback Decision | Python |

## 3. CI/CD Architecture

```text
Developer
    |
    v
Git Push / Pull Request
    |
    v
GitHub Actions
    |
    +-- Run Pytest
    |
    +-- Build Docker Image
    |
    v
Merge into main
    |
    v
Publish Docker Image to GHCR
    |
    v
Trigger Render Deployment
    |
    v
Monitor Deployment Status
    |
    v
Verify Docker Image and Health Check
    |
    +-- Success: Deployment verified
    |
    +-- Failure: Evaluate rollback decision
                    |
                    +-- NO_ROLLBACK
                    +-- ROLLBACK_CANDIDATE
                    +-- MANUAL_REVIEW
```

**Note:** Automated rollback execution is not yet enabled. The rollback decision logic is implemented and tested using simulated deployment scenarios.

## 4. Project Structure

```text
task-api/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── verify-render.yml
│       └── test-failure.yml
│
├── rollback/
│   ├── __init__.py
│   └── decision.py
│
├── tests/
│   ├── test_health.py
│   ├── test_login.py
│   └── test_rollback.py
│
├── main.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

The project also includes backend login validation exercises and their corresponding automated tests.

## 5. Installation and Local Development

### Prerequisites

- Python 3.11 or compatible version
- Git
- Docker
- pip

### Clone the repository

```bash
git clone https://github.com/NamNguyen0903/task-api.git
cd task-api
```

### Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```powershell
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the API

```bash
uvicorn main:app --reload
```

Access the application:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/health

## 6. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Application health check |
| GET | `/docs` | Interactive API documentation |

### Health Check Example

Request:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## 7. Automated Testing

This project uses Pytest for automated backend testing.

The test suite covers:

- Health endpoint responses
- HTTP status code validation
- Login input validation
- Login credential validation
- Missing and invalid login configuration
- Rollback decision scenarios

### Run All Tests

```bash
python -m pytest -v
```

### Run Rollback Tests

```bash
python -m pytest tests/test_rollback.py -v
```

### Latest Verified Local Test Result

```text
23 passed in 1.00s
```

Tests are also configured to run automatically through GitHub Actions.

## 8. Docker

The application is containerized using Docker.

### Build Docker Image

```bash
docker build -t task-api:latest .
```

### Run Docker Container

```bash
docker run -d \
  --name task-api \
  -p 127.0.0.1:8000:8000 \
  task-api:latest
```

### Verify Container

```bash
docker ps
curl http://127.0.0.1:8000/health
```

### View Logs

```bash
docker logs task-api
```

### Multi-Platform Support

The GitHub Actions pipeline builds Docker images for:

```text
linux/amd64
linux/arm64
```

This supports both common x86-64 servers and ARM64 systems, including Apple Silicon Macs.

## 9. Continuous Integration

GitHub Actions automatically runs validation when code is pushed or a Pull Request is created.

The CI pipeline performs:

1. Checkout source code
2. Configure Python environment
3. Install dependencies
4. Execute Pytest
5. Build Docker image

Docker builds depend on successful test execution.

A failed required check can prevent merging when GitHub branch protection is configured accordingly.

## 10. Continuous Delivery

After code is merged into the `main` branch, the workflow:

1. Runs the automated tests.
2. Builds the Docker image.
3. Authenticates to GHCR.
4. Publishes the image with a commit SHA tag.

Example image naming convention:

```text
ghcr.io/namnguyen0903/task-api:sha-<commit-sha>
```

Using a commit-specific tag improves release traceability and helps identify the correct image for recovery.

## 11. Automated Deployment to Render

The application is hosted using Render.

**Live Application:**  
https://task-api-sha.onrender.com

**Health Check:**  
https://task-api-sha.onrender.com/health

The deployment workflow:

1. Saves the current live deployment ID.
2. Triggers a new Render deployment using a Deploy Hook.
3. Captures the new deployment ID.
4. Monitors the deployment through the Render API.
5. Confirms that the deployment reaches `live`.
6. Verifies the deployed Docker image against the expected commit SHA.
7. Checks that `/health` returns the expected healthy response.

The pipeline reports failure when deployment verification does not pass.

Render Free instances may enter an idle state, resulting in additional startup latency.

## 12. Deployment Monitoring

Deployment monitoring uses the Render REST API.

The workflow tracks deployment statuses such as:

```text
queued
update_in_progress
live
update_failed
build_failed
canceled
```

A successful deployment must reach the expected status and pass application verification checks.

The workflow also compares the expected and actual Docker image references to confirm the intended version was deployed.

## 13. Rollback Decision System

The project implements rollback decision logic in:

```text
rollback/decision.py
```

The decision function evaluates:

- Previous good deployment ID
- Newly triggered deployment ID
- Current live deployment
- Deployment status information

### Supported Decisions

| Decision | Meaning |
|---|---|
| `NO_ROLLBACK` | Previous good deployment is still live |
| `ROLLBACK_CANDIDATE` | New deployment is live but requires recovery evaluation |
| `MANUAL_REVIEW` | Deployment state is ambiguous or unsafe to act upon |

### Tested Scenarios

**Scenario 1 — Previous Deployment Still Live**

The new release fails, but the previous good deployment remains live.

Expected decision:

```text
no_rollback
```

**Scenario 2 — New Deployment Live but Verification Fails**

The new release becomes live, but verification fails.

Expected decision:

```text
rollback_candidate
```

**Scenario 3 — No Unique Live Deployment**

The system cannot reliably determine the active deployment.

Expected decision:

```text
manual_review
```

### Failure Simulation

A dedicated GitHub Actions workflow tests failure handling using mock deployment data.

Expected output:

```text
Rollback decision: rollback_candidate
Failure path test passed
DRY RUN: No actual rollback
```

**Current limitation:** The rollback decision and simulation workflows are implemented, but automated rollback execution against the live Render service has not yet been enabled or validated.

## 14. GitHub Actions Secrets and Variables

Sensitive credentials are configured through GitHub Actions settings rather than committed to the repository.

### Secrets

| Secret | Purpose |
|---|---|
| `RENDER_DEPLOY_HOOK_URL` | Trigger Render deployments |
| `RENDER_API_KEY` | Authenticate Render API requests |
| `GITHUB_TOKEN` | Authenticate GitHub Actions and GHCR |

`GITHUB_TOKEN` is provided automatically by GitHub Actions.

### Variables

| Variable | Purpose |
|---|---|
| `RENDER_SERVICE_ID` | Identify the Render Web Service |

Never commit API keys, deployment hooks, passwords, or private credentials into source control.

## 15. Git Workflow

Development follows a feature-branch workflow:

```text
main
  |
  +-- feature/*
        |
        +-- Develop
        +-- Test
        +-- Commit
        +-- Push
        +-- Pull Request
        +-- CI Validation
        +-- Code Review
        +-- Merge into main
```

Deployment publishing is restricted to the `main` branch.

## 16. Future Improvements

- Enable automated rollback with additional safety checks
- Validate rollback through controlled deployment experiments
- Improve deployment concurrency controls
- Add monitoring and alerting
- Expand integration and API testing
- Introduce persistent database storage
- Add production-oriented container hardening
- Implement blue-green or zero-downtime deployment
- Move to VPS or managed cloud infrastructure when needed

## 17. Learning Outcomes

Through this project, I practiced:

- Git branching and Pull Request workflows
- Writing automated tests using Pytest
- Creating and maintaining GitHub Actions pipelines
- Building multi-platform Docker images
- Publishing container images to GHCR
- Deploying containerized applications to Render
- Using cloud APIs for deployment monitoring
- Implementing health checks and release verification
- Designing and testing rollback decision logic
- Debugging CI/CD failures

## 18. Project Links

**GitHub Repository:**  
https://github.com/NamNguyen0903/task-api

**Live API:**  
https://task-api-sha.onrender.com

**Health Check:**  
https://task-api-sha.onrender.com/health

---

**Project Type:** Backend Development & DevOps Practice  
**Technologies:** Python, FastAPI, Pytest, Docker, GitHub Actions, GHCR, Render  
**Status:** Automated CI/CD and deployment verification implemented; automated rollback decision tested in dry-run mode.