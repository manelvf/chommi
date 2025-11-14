# GitHub Actions CI/CD

## Overview

This repository uses GitHub Actions for continuous integration and continuous deployment.

## Workflow: CI (`ci.yml`)

### Triggers

The CI workflow runs automatically on:
- **Push events** to branches: `main`, `master`, `develop`, `claude/**`
- **Pull request events** to branches: `main`, `master`, `develop`

### Jobs

#### 1. **Test Job**
Runs the Django test suite across multiple Python versions.

- **Python versions**: 3.11, 3.12
- **Services**: Redis 7 (for Celery testing)
- **Steps**:
  - Install dependencies using uv
  - Create required directories (logs, events)
  - Run Django migrations
  - Execute test suite
  - Validate no missing migrations

#### 2. **Lint Job**
Performs code quality checks.

- **Tools**:
  - `black` - Code formatting
  - `isort` - Import sorting
  - `flake8` - Python linting
- **Behavior**: Continues on error (non-blocking)

#### 3. **Security Job**
Scans for security vulnerabilities.

- **Tools**:
  - `bandit` - Security issue scanner
  - `safety` - Dependency vulnerability checker
- **Behavior**: Continues on error (non-blocking)

## Viewing Results

### Via GitHub UI
Visit: https://github.com/manelvf/chommi/actions

### Via Badge
The README includes a status badge showing the current CI status:
[![CI](https://github.com/manelvf/chommi/actions/workflows/ci.yml/badge.svg)](https://github.com/manelvf/chommi/actions/workflows/ci.yml)

### Via GitHub CLI
```bash
gh run list --branch your-branch-name
gh run view <run-id>
```

## Environment Variables

The CI workflow uses these environment variables for testing:
- `SECRET_KEY`: Test-only secret key
- `DEBUG`: Set to 'False'
- `ALLOWED_HOSTS`: 'localhost,127.0.0.1'

## Local Testing

To run the same checks locally:

```bash
# Install dependencies
uv sync

# Run tests
source .venv/bin/activate
python manage.py test

# Check formatting
black --check .
isort --check-only .
flake8 .

# Security checks
bandit -r bets/ chommies/ -ll
safety check
```

## Troubleshooting

### Tests Failing
1. Check the Actions tab for detailed logs
2. Ensure all migrations are committed
3. Verify dependencies are up to date

### Workflow Not Triggering
1. Verify branch name matches trigger patterns
2. Check workflow file syntax
3. Ensure Actions are enabled in repository settings

## Adding New Checks

To add new checks to the CI pipeline:
1. Edit `.github/workflows/ci.yml`
2. Add new steps or jobs
3. Commit and push changes
4. Workflow updates automatically
