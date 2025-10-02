# GitHub Actions Workflows

This directory contains all CI/CD workflows for the Solana Automation project.

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GitHub Actions Workflows                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │   Main CI    │  │  Python CI   │  │TypeScript CI │
          │   (ci.yml)   │  │(python-ci.yml)│ │(typescript-  │
          │              │  │              │  │   ci.yml)    │
          │ Quick checks │  │ Comprehensive│  │ Comprehensive│
          │ & overview   │  │ Python tests │  │ TS/JS tests  │
          └──────────────┘  └──────────────┘  └──────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │   CodeQL     │  │OSSF Scorecard│  │ Dependabot   │
          │  Analysis    │  │(scorecard.yml)│ │(dependabot.yml)│
          │(codeql-      │  │              │  │              │
          │analysis.yml) │  │ Security     │  │ Dependency   │
          │              │  │ posture      │  │ updates      │
          │ SAST scan    │  │ assessment   │  │              │
          └──────────────┘  └──────────────┘  └──────────────┘
```

## Workflow Files

### 1. `ci.yml` - Main CI
**Triggers:** Push/PR to main branches  
**Duration:** ~2-3 minutes  
**Purpose:** Fast smoke tests and overview

**Jobs:**
- Overview generation
- Python quick check (ruff, black)
- TypeScript quick check (build)
- Status reporting

### 2. `python-ci.yml` - Python CI
**Triggers:** Push/PR affecting Python files  
**Duration:** ~5-10 minutes  
**Purpose:** Comprehensive Python quality checks

**Jobs:**
1. **Lint**
   - ruff (linter)
   - black (formatter)
   - isort (import sorter)
   - mypy (type checker)

2. **Security**
   - pip-audit (vulnerability scanner)
   - Root directory scan
   - solana-agent-kit-py-main scan

3. **Test**
   - pytest on Python 3.9, 3.10, 3.11, 3.12
   - Matrix testing across versions

### 3. `typescript-ci.yml` - TypeScript CI
**Triggers:** Push/PR affecting TS/JS files  
**Duration:** ~3-5 minutes  
**Purpose:** TypeScript/JavaScript quality checks

**Jobs:**
1. **Lint & Build**
   - TypeScript compilation (tsc)
   - ESLint (when configured)
   - Prettier (when configured)

2. **Security**
   - npm audit (vulnerability scanner)
   - JSON output for analysis

3. **Test**
   - npm test (when configured)

### 4. `codeql-analysis.yml` - CodeQL Security
**Triggers:**
- Push/PR to main branches
- Weekly schedule (Mondays 2:30 AM UTC)

**Duration:** ~5-10 minutes  
**Purpose:** Advanced security vulnerability detection

**Languages:**
- Python
- JavaScript/TypeScript

**Features:**
- 200+ security patterns
- SQL injection detection
- XSS detection
- Command injection detection
- Path traversal detection
- Results in Security tab

### 5. `scorecard.yml` - OSSF Scorecard
**Triggers:**
- Push to main
- Weekly schedule (Mondays 3:00 AM UTC)
- Manual dispatch

**Duration:** ~2-3 minutes  
**Purpose:** Repository security posture

**Checks:**
- Branch protection
- Code review practices
- Dependency updates
- Security policy
- And 14+ more checks

### 6. `dependabot.yml` - Dependabot Config
**Triggers:** Weekly schedule (Mondays 3:00 AM UTC)  
**Purpose:** Automated dependency updates

**Coverage:**
- Python (pip) - root directory
- Python (pip) - solana-agent-kit-py-main
- npm - mcp-server
- GitHub Actions

## Workflow Status

You can check the status of all workflows:
- In the [Actions tab](https://github.com/jparram/SolanaAutomation/actions)
- Via badges in the README
- In the Security tab (for security workflows)

## Local Testing

Before pushing, you can run the same checks locally:

### Python
```bash
# Install tools
pip install ruff black isort mypy pytest pip-audit

# Run checks
ruff check .
black --check .
isort --check-only .
mypy .
pip-audit
pytest
```

### TypeScript
```bash
cd mcp-server

# Install dependencies
npm install

# Run checks
npm run lint
npm run format:check
npm run build
npm audit
npm test
```

## Workflow Configuration

### Common Patterns

All workflows use:
- `actions/checkout@v4` - Latest checkout action
- `actions/setup-python@v5` - Latest Python setup
- `actions/setup-node@v4` - Latest Node.js setup
- `continue-on-error: true` - Non-blocking for gradual improvement

### Caching

Workflows use caching to speed up runs:
- Python: pip cache
- TypeScript: npm cache
- CodeQL: database cache

### Scheduling

Weekly scheduled workflows run at:
- **2:30 AM UTC Monday:** CodeQL analysis
- **3:00 AM UTC Monday:** OSSF Scorecard
- **3:00 AM UTC Monday:** Dependabot checks

## Troubleshooting

### Workflow Failures

1. **Check the Actions tab** for detailed logs
2. **Review the specific job** that failed
3. **Run the check locally** to reproduce
4. **Fix the issue** and push again

### Common Issues

**Python linting failures:**
- Run `ruff check . --fix` to auto-fix
- Run `black .` to format
- Run `isort .` to sort imports

**TypeScript build failures:**
- Check `tsc` output for type errors
- Ensure dependencies are installed
- Verify TypeScript configuration

**Security alerts:**
- Review in Security tab
- Update vulnerable dependencies
- Check Dependabot PRs

## Maintenance

### Weekly Tasks
- Review Dependabot PRs
- Check security alerts
- Review CodeQL findings
- Monitor OSSF Scorecard

### Monthly Tasks
- Review workflow performance
- Update workflow versions
- Optimize caching strategies
- Review security policies

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [CodeQL Documentation](https://codeql.github.com/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [OSSF Scorecard](https://github.com/ossf/scorecard)
- [CI_CD_SETUP.md](../../CI_CD_SETUP.md) - Detailed setup guide
- [PROJECT_ANALYSIS.md](../../PROJECT_ANALYSIS.md) - Project analysis

## Support

For questions or issues with workflows:
1. Check workflow run logs
2. Review [CI_CD_SETUP.md](../../CI_CD_SETUP.md)
3. Consult GitHub documentation
4. Open an issue in the repository
