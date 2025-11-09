# CI/CD Setup Guide

## 🎯 Overview

GitHub Actions workflows have been configured for automated linting and testing across all SpendSense components.

## 📋 Workflows Created

### 1. **CI Pipeline** (`ci.yml`)
**Purpose:** Main continuous integration pipeline
**Triggers:** Push and PR to `main` or `develop`
**Features:**
- Matrix strategy for parallel execution
- Backend: Black, Pylint, MyPy
- Frontend: ESLint, TypeScript, Build verification

### 2. **Lint Pipeline** (`lint.yml`)  
**Purpose:** Comprehensive linting across all services
**Includes:**
- Backend Python linting
- Frontend TypeScript/React linting
- Service layer Python linting

### 3. **Test Pipeline** (`test.yml`)
**Purpose:** Automated testing with service dependencies
**Services:**
- PostgreSQL 15 (backend tests)
- Redis 7 (caching tests)
**Coverage:** pytest and jest with coverage reporting

## 🚀 Usage

### Automatic Triggers
Workflows run automatically on:
- ✅ Push to `main` branch
- ✅ Push to `develop` branch
- ✅ Pull requests to `main` or `develop`

### Manual Trigger
Run workflows manually from GitHub Actions tab:
1. Go to repository → Actions
2. Select workflow
3. Click "Run workflow"

## 📊 What Gets Checked

### Backend (Python)
```bash
# Code formatting
black --check app/ scripts/ tests/

# Code quality
pylint app/ --rcfile=.pylintrc

# Type checking
mypy app/ --ignore-missing-imports

# Tests
pytest tests/ -v --cov=app
```

### Frontend (TypeScript/React)
```bash
# Linting
npm run lint

# Type checking
npx tsc --noEmit

# Build verification
npx vite build --mode production

# Tests
npm test
```

### Service (Python)
```bash
# Code formatting
black --check app/ tests/

# Code quality
pylint app/ --rcfile=.pylintrc
```

## ⚙️ Configuration Files

### `.pylintrc` (Root)
- Max line length: 120
- Disabled overly strict rules
- Optimized for FastAPI/SQLAlchemy

### `frontend/.eslintrc.cjs`
- React hooks rules
- TypeScript parser
- React Refresh plugin

## 🔧 Local Development

### Run linting locally before committing:

**Backend:**
```bash
cd backend
black app/ scripts/ tests/
pylint app/
mypy app/ --ignore-missing-imports
pytest tests/ -v
```

**Frontend:**
```bash
cd frontend
npm run lint
npx tsc --noEmit
npm test
```

## 📈 Viewing Results

### In GitHub
1. Navigate to **Actions** tab
2. Click on workflow run
3. View job details and logs
4. Check annotations on files

### In Pull Requests
- Checks appear at bottom of PR
- Red ❌ = failing checks
- Yellow ⚠️ = warnings
- Green ✅ = all passed

## 🎯 Best Practices

1. **Always run linting locally** before pushing
2. **Fix linting errors** before requesting review
3. **Check CI status** before merging PRs
4. **Review warnings** even if checks pass

## ⚡ Performance

- **Caching enabled** for pip and npm (faster runs)
- **Matrix strategy** runs jobs in parallel
- **Continue-on-error** prevents blocking on warnings
- Average runtime: 3-5 minutes

## 🔄 Future Enhancements

Consider adding:
- [ ] Automated deployment on merge to main
- [ ] Security scanning (Snyk, Dependabot)
- [ ] E2E tests with Playwright
- [ ] Performance benchmarking
- [ ] Docker image building and pushing to ECR
- [ ] Auto-versioning and changelog generation

## 📝 Notes

- All workflows use latest GitHub Actions (v4-v5)
- Python 3.11 and Node.js 18 match production
- Service dependencies match production stack
- Tests run in isolated containers

---

**Setup Date:** November 9, 2025  
**Status:** ✅ Active and Ready

