# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for continuous integration and deployment.

## Workflows

### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
Runs on every push and pull request to `main` and `develop` branches.

**Jobs:**
- **Backend Linting:**
  - Black (code formatting)
  - Pylint (code quality)
  - Runs in parallel matrix job

- **Frontend Linting:**
  - ESLint (code quality)
  - TypeScript type checking
  - Vite build verification
  - Runs in parallel matrix job

**Triggers:**
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
```

### 2. **Lint Pipeline** (`.github/workflows/lint.yml`)
Separate comprehensive linting for all components.

**Jobs:**
- **Backend (Python):** Black, Pylint, MyPy
- **Frontend (TypeScript):** ESLint, TypeScript compiler
- **Service (Python):** Black, Pylint

### 3. **Test Pipeline** (`.github/workflows/test.yml`)
Runs automated tests with service dependencies.

**Services:**
- PostgreSQL 15 (for backend tests)
- Redis 7 (for caching tests)

**Jobs:**
- Backend: pytest with coverage reporting
- Frontend: jest with coverage reporting

## Configuration Files

### `.pylintrc` (Root)
Pylint configuration for Python backend and service:
- Max line length: 120 characters
- Disabled strict docstring requirements
- Optimized for FastAPI/SQLAlchemy patterns

### `frontend/.eslintrc.cjs`
ESLint configuration for TypeScript/React:
- React hooks linting
- TypeScript strict mode
- React Refresh plugin

## Running Locally

### Backend Linting
```bash
cd backend
black --check app/ scripts/ tests/
pylint app/ --rcfile=../.pylintrc
mypy app/ --ignore-missing-imports
```

### Frontend Linting
```bash
cd frontend
npm run lint
npx tsc --noEmit
```

### Service Linting
```bash
cd service
black --check app/ tests/
pylint app/ --rcfile=../.pylintrc
```

## Workflow Status

Check workflow status:
- GitHub Repository → Actions tab
- View results per commit/PR
- Failing checks will show inline annotations

## Notes

- All linting jobs use `continue-on-error: true` to not block deployments
- Warnings are surfaced in PR reviews
- Caching enabled for pip and npm for faster runs
- Matrix strategy runs jobs in parallel for speed

