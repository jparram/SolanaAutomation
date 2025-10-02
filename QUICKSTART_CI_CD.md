# CI/CD Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide will help you understand and use the new CI/CD system immediately.

## What You Get Out of the Box

✅ **Automatic Quality Checks** - Every push is automatically tested  
✅ **Security Scanning** - Vulnerabilities detected automatically  
✅ **Dependency Updates** - Weekly PRs with updates  
✅ **Code Formatting** - Standardized code style  
✅ **Type Safety** - Catch type errors before runtime  

## For Contributors

### Before You Push

Run these commands locally to catch issues early:

#### Python Code
```bash
# Install tools (one time)
pip install ruff black isort mypy

# Check your code
ruff check .          # Fast linting
black --check .       # Format checking
isort --check-only .  # Import sorting

# Auto-fix issues
ruff check . --fix
black .
isort .
```

#### TypeScript Code
```bash
cd mcp-server

# Install tools (one time)
npm install

# Check your code
npm run lint          # ESLint
npm run format:check  # Prettier
npm run build        # TypeScript compilation

# Auto-fix issues
npm run lint:fix
npm run format
```

### After You Push

1. **Check GitHub Actions Tab**
   - Go to: https://github.com/jparram/SolanaAutomation/actions
   - Look for your commit
   - Green checkmark = all good ✅
   - Red X = issues to fix ❌

2. **View Results**
   - Click on the workflow run
   - Expand failed jobs to see errors
   - Fix issues and push again

## For Maintainers

### Daily Tasks

1. **Monitor Actions Tab**
   - Check for failed workflows
   - Review error messages
   - Merge passing PRs

### Weekly Tasks

1. **Review Dependabot PRs**
   - Go to Pull Requests tab
   - Look for PRs from `dependabot[bot]`
   - Review changes
   - Merge if safe

2. **Check Security Tab**
   - Go to: https://github.com/jparram/SolanaAutomation/security
   - Review CodeQL findings
   - Address security issues

3. **Review OSSF Scorecard**
   - Check scorecard badge
   - Implement recommendations

## Workflow Triggers

### What Triggers Workflows?

| Workflow | Trigger |
|----------|---------|
| CI | Every push/PR |
| Python CI | Push/PR affecting `.py` files |
| TypeScript CI | Push/PR affecting `.ts`/`.js` files |
| CodeQL | Push/PR + weekly (Monday 2:30 AM UTC) |
| OSSF Scorecard | Push to main + weekly (Monday 3:00 AM UTC) |
| Dependabot | Weekly (Monday 3:00 AM UTC) |

## Understanding Results

### CI Status Badges

At the top of README.md, you'll see badges like:

![CI](https://github.com/jparram/SolanaAutomation/workflows/CI/badge.svg)

- **Green** ✅ = Passing
- **Red** ❌ = Failing
- **Yellow** ⚠️ = In progress

Click badges to see detailed results.

### Common Issues

#### Python Linting Errors
```bash
# Error: Line too long
ruff check . --fix

# Error: Imports not sorted
isort .

# Error: Code not formatted
black .
```

#### TypeScript Build Errors
```bash
cd mcp-server

# Error: Type errors
npm run build
# Fix type errors in code

# Error: Linting issues
npm run lint:fix
```

#### Security Vulnerabilities
```bash
# Python: Update vulnerable package
pip install --upgrade package-name

# TypeScript: Update vulnerable package
cd mcp-server
npm update package-name
```

## Configuration Files

You don't need to edit these unless you want to customize:

| File | Purpose |
|------|---------|
| `.github/workflows/*.yml` | Workflow definitions |
| `.github/dependabot.yml` | Dependency update config |
| `.ruff.toml` | Python linting rules |
| `pyproject.toml` | Python tool config |
| `mcp-server/.eslintrc.json` | TypeScript linting rules |
| `mcp-server/.prettierrc` | TypeScript formatting rules |

## Getting Help

### Documentation

- **Detailed Setup:** [CI_CD_SETUP.md](CI_CD_SETUP.md)
- **Project Analysis:** [PROJECT_ANALYSIS.md](PROJECT_ANALYSIS.md)
- **Implementation Summary:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Workflows Overview:** [.github/workflows/README.md](.github/workflows/README.md)

### Troubleshooting Steps

1. **Check workflow logs** - Actions tab → Click workflow → Click job
2. **Run locally** - Use commands above to reproduce
3. **Review documentation** - Check the docs mentioned above
4. **Check GitHub docs** - https://docs.github.com/en/actions

### Common Questions

**Q: Why is my workflow failing?**  
A: Click the red X to see detailed error logs.

**Q: Can I skip CI checks?**  
A: No, but you can fix issues and push again. CI runs fast!

**Q: How do I add more checks?**  
A: Edit the workflow files in `.github/workflows/`.

**Q: What if I want to disable a check?**  
A: Comment out the job in the workflow file or remove the file.

**Q: Are these checks blocking?**  
A: No! They use `continue-on-error: true` to allow development while improving.

## Best Practices

### ✅ DO

- Run checks locally before pushing
- Fix linting issues as you code
- Review Dependabot PRs weekly
- Keep dependencies up to date
- Address security findings promptly

### ❌ DON'T

- Ignore failing workflows
- Skip local testing
- Disable security checks
- Let Dependabot PRs pile up
- Push without running linters

## Quick Reference

### Python Commands
```bash
# Check everything
ruff check . && black --check . && isort --check-only . && mypy .

# Fix everything
ruff check . --fix && black . && isort .

# Security scan
pip-audit

# Run tests
pytest
```

### TypeScript Commands
```bash
cd mcp-server

# Check everything
npm run lint && npm run format:check && npm run build

# Fix everything
npm run lint:fix && npm run format

# Security scan
npm audit

# Run tests
npm test
```

### Git Workflow
```bash
# 1. Make changes
# 2. Run local checks
# 3. Commit
git add .
git commit -m "Your message"

# 4. Push
git push

# 5. Check Actions tab
# 6. Fix issues if any
# 7. Repeat
```

## Success Metrics

After using this system, you should see:

- ✅ Faster code reviews
- ✅ Fewer bugs in production
- ✅ Better code consistency
- ✅ Improved security posture
- ✅ Up-to-date dependencies

## Next Steps

1. **Try it out** - Make a small change and push
2. **Watch the workflows** - See them run in Actions tab
3. **Review the docs** - Read CI_CD_SETUP.md for details
4. **Customize** - Adjust workflows to your needs
5. **Share feedback** - Let maintainers know what works!

## Summary

The CI/CD system is designed to help, not hinder. It:
- Runs automatically on every push
- Provides fast feedback
- Catches issues early
- Improves code quality
- Costs $0.00

Start using it today! 🚀

---

**Need more help?** Check out:
- [CI_CD_SETUP.md](CI_CD_SETUP.md) - Full documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Repository Actions Tab](https://github.com/jparram/SolanaAutomation/actions)
