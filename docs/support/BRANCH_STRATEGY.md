# Git Branch Strategy

## Overview

This document outlines the Git branch strategy for the SpendSense project, following a Git Flow-like model optimized for our development workflow.

---

## Branch Types

### Main Branches

#### `main`
- **Purpose**: Production-ready code
- **Protection**: Protected branch (requires PR approval)
- **Merge Policy**: Only from `release/*` or `hotfix/*` branches
- **Deployment**: Auto-deploys to production environment
- **Status**: Always stable and deployable

#### `develop`
- **Purpose**: Integration branch for completed features
- **Protection**: Protected branch (requires PR approval)
- **Merge Policy**: Only from `feature/*` branches
- **Deployment**: Auto-deploys to staging environment
- **Status**: Integration branch, may be unstable

---

### Supporting Branches

#### `feature/*`
- **Purpose**: New features and enhancements
- **Naming**: `feature/task-X.Y-short-description` (e.g., `feature/1.1-project-setup`)
- **Source**: Always branch from `develop`
- **Target**: Always merge back to `develop`
- **Lifecycle**: Delete after merge
- **Examples**:
  - `feature/1.1-project-setup`
  - `feature/2.1-authentication-foundation`
  - `feature/10.1-frontend-project-setup`

#### `hotfix/*`
- **Purpose**: Critical production fixes
- **Naming**: `hotfix/short-description` (e.g., `hotfix/security-patch`)
- **Source**: Branch from `main`
- **Target**: Merge to both `main` and `develop`
- **Lifecycle**: Delete after merge
- **Use Case**: Fixes for production issues that can't wait for release

#### `release/*`
- **Purpose**: Release preparation and final testing
- **Naming**: `release/vX.Y.Z` (e.g., `release/v1.0.0`)
- **Source**: Branch from `develop`
- **Target**: Merge to both `main` and `develop`
- **Lifecycle**: Delete after merge and tag creation
- **Use Case**: Final testing, bug fixes, and version bumping before production

---

## Workflow Examples

### Feature Development

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/1.1-project-setup

# 3. Work on feature (commits, pushes)
git add .
git commit -m "feat: initialize project structure"
git push origin feature/1.1-project-setup

# 4. Create PR to develop
# (via GitHub/GitLab UI)

# 5. After PR approval and merge, delete local branch
git checkout develop
git pull origin develop
git branch -d feature/1.1-project-setup
```

### Hotfix Workflow

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b hotfix/critical-security-patch

# 3. Fix the issue
git add .
git commit -m "fix: critical security vulnerability"

# 4. Create PRs to both main and develop
# 5. Merge to main first, then to develop
```

### Release Workflow

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create release branch
git checkout -b release/v1.0.0

# 3. Final testing, version bumping
git add .
git commit -m "chore: bump version to 1.0.0"

# 4. Create PR to main
# 5. After merge, tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## Commit Message Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config, etc.)

### Examples
```
feat(auth): implement JWT token generation
fix(api): resolve database connection pool issue
docs(readme): update setup instructions
test(backend): add unit tests for authentication
chore(deps): update FastAPI to 0.109.0
```

---

## Branch Naming Conventions

### Feature Branches
- Format: `feature/task-X.Y-short-description`
- Examples:
  - `feature/1.1-project-setup`
  - `feature/2.2-email-password-auth`
  - `feature/10.1-frontend-project-setup`

### Hotfix Branches
- Format: `hotfix/short-description`
- Examples:
  - `hotfix/security-patch`
  - `hotfix/database-connection-issue`

### Release Branches
- Format: `release/vX.Y.Z`
- Examples:
  - `release/v1.0.0`
  - `release/v1.1.0`

---

## Branch Protection Rules

### `main` Branch
- ✅ Require pull request reviews (at least 1 approval)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date before merging
- ✅ Include administrators
- ✅ No force push
- ✅ No deletion

### `develop` Branch
- ✅ Require pull request reviews (at least 1 approval)
- ✅ Require status checks to pass
- ✅ Include administrators
- ✅ No force push (except administrators)
- ✅ No deletion

---

## Pull Request Process

### PR Creation
1. **Title**: Use conventional commit format
   - Example: `feat(auth): implement JWT token generation`

2. **Description Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Related Task
   Closes #TASK_NUMBER or Addresses #TASK_NUMBER

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   ```

3. **Labels**: Add appropriate labels (backend, frontend, service, infrastructure, etc.)

### PR Review
- At least 1 approval required
- All CI checks must pass
- Resolve all review comments before merging
- Use "Squash and merge" for feature branches
- Use "Merge commit" for release/hotfix branches

---

## Git Configuration

### Recommended Settings

```bash
# Set default branch name
git config --global init.defaultBranch main

# Set default pull strategy
git config --global pull.rebase false

# Set default editor (optional)
git config --global core.editor "code --wait"  # VS Code
```

### Useful Aliases

```bash
# Add to ~/.gitconfig

[alias]
  co = checkout
  br = branch
  ci = commit
  st = status
  unstage = reset HEAD --
  last = log -1 HEAD
  visual = !gitk
```

---

## Initial Setup (What You Need to Do)

1. **Initialize Git Repository**
   ```bash
   cd "/Users/andychuong/Documents/GauntletAI/Week 4/Plat Projects/SpendSense"
   git init
   ```

2. **Create Initial Commit**
   ```bash
   git add .
   git commit -m "chore: initial project setup - Task 1.1"
   ```

3. **Create Main and Develop Branches**
   ```bash
   git checkout -b main
   git checkout -b develop
   git checkout main
   ```

4. **Set Up Remote (if applicable)**
   ```bash
   git remote add origin <your-repository-url>
   ```

5. **Push Initial Branches**
   ```bash
   git push -u origin main
   git push -u origin develop
   ```

6. **Set Up Branch Protection** (via GitHub/GitLab UI)
   - Protect `main` branch
   - Protect `develop` branch
   - Configure protection rules as described above

---

## Task-Based Branch Naming

For this project, branch names should reference the task number from PROJECT-PLAN.md:

- **Task 1.1**: `feature/1.1-project-setup`
- **Task 1.2**: `feature/1.2-database-design-setup`
- **Task 2.1**: `feature/2.1-authentication-foundation`
- **Task 10.1**: `feature/10.1-frontend-project-setup`

This makes it easy to track which task a branch relates to.

---

## Questions or Issues?

If you have questions about this branch strategy, please discuss with the team before making changes. Consistency is key to a smooth development workflow.


