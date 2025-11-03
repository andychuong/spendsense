# Security Guidelines

## Secrets Management

**NEVER commit secrets, credentials, or API keys to the repository.**

### What Should NEVER Be Committed

1. **Environment Files** (`.env`, `.env.*`)
   - All `.env` files are ignored
   - Only commit `.env.example` files with dummy values
   - Never include real API keys, passwords, or secrets in example files

2. **AWS Credentials**
   - `.aws/` directory
   - `aws-credentials.json`
   - AWS access keys and secret keys
   - Use AWS IAM roles or AWS Secrets Manager instead

3. **OAuth Credentials**
   - Google OAuth client ID/secret
   - GitHub OAuth client ID/secret
   - Facebook App ID/secret
   - Apple Sign In credentials (Service ID, Key ID, Team ID, Private Key)
   - Store in AWS Secrets Manager or environment variables

4. **JWT Secrets**
   - Private keys for JWT signing
   - Secret keys for token generation
   - Store in AWS Secrets Manager

5. **OpenAI API Keys**
   - OpenAI API keys
   - Store in AWS Secrets Manager or environment variables

6. **Database Credentials**
   - Database passwords
   - Database connection strings with credentials
   - Use connection strings from environment variables or AWS Secrets Manager

7. **Terraform Variables**
   - `*.tfvars` files containing secrets
   - Terraform state files (`*.tfstate`)
   - Only commit `.tfvars.example` files

8. **Docker Secrets**
   - `docker-compose.override.yml` (may contain secrets)
   - Environment files used in Docker

### Recommended Practices

1. **Use AWS Secrets Manager**
   - Store all production secrets in AWS Secrets Manager
   - Reference secrets in application code via AWS SDK

2. **Use Environment Variables for Development**
   - Use `.env` files locally (already in .gitignore)
   - Never commit `.env` files
   - Use `.env.example` as templates

3. **Use Example Files**
   - Create `.env.example` files with placeholder values
   - Create `*.tfvars.example` files for Terraform
   - Document what values are needed

4. **Pre-commit Hooks** (Optional)
   - Consider adding a pre-commit hook to scan for secrets
   - Tools: `git-secrets`, `truffleHog`, `detect-secrets`

5. **Code Review**
   - Always review PRs for potential secrets
   - Use automated secret scanning tools in CI/CD

### Security Checklist Before Committing

- [ ] No `.env` files in staging area
- [ ] No API keys or secrets in code
- [ ] No hardcoded passwords
- [ ] No AWS credentials
- [ ] No OAuth client secrets
- [ ] No JWT signing keys
- [ ] No database credentials in code
- [ ] No Terraform state files
- [ ] No `*.tfvars` files with real values

### What IS Safe to Commit

- `.env.example` files (with placeholder values)
- `*.tfvars.example` files (with placeholder values)
- Configuration templates
- Public keys (if needed)
- Documentation (without real credentials)

### Example Files

When creating example files, use clear placeholders:

```env
# .env.example
DATABASE_URL=postgresql://user:password@localhost:5432/spendsense
OPENAI_API_KEY=sk-placeholder-key-here
JWT_SECRET_KEY=your-secret-key-here
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
```

### Emergency: If You Accidentally Commit Secrets

1. **DO NOT** just delete the commit - the secrets are still in git history
2. **IMMEDIATE ACTION**:
   - Rotate/revoke all exposed credentials immediately
   - Use `git filter-branch` or BFG Repo-Cleaner to remove from history
   - Force push to remove from remote (coordinate with team)
   - Notify security team if applicable
3. **Prevention**: Set up secret scanning in CI/CD to prevent future commits

---

**Remember: When in doubt, don't commit it. Use AWS Secrets Manager or environment variables instead.**


