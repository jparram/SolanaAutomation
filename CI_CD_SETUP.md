# CI/CD Setup Documentation

## Overview

This repository now includes a comprehensive CI/CD pipeline with security scanning, linting, formatting, and automated dependency updates.

## Workflows

### 1. Main CI Workflow (`ci.yml`)

**Triggers:** Push and PR to main branches  
**Purpose:** Quick smoke tests for both Python and TypeScript code

This workflow provides a fast overview of code health with:
- Python quick check (ruff, black)
- TypeScript quick check (build verification)
- Summary report in GitHub Actions UI

### 2. Python CI Workflow (`python-ci.yml`)

**Triggers:** Push/PR affecting Python files  
**Purpose:** Comprehensive Python code quality checks

#### Jobs:
- **Lint**
  - `ruff` - Fast Python linter
  - `black` - Code formatter
  - `isort` - Import statement sorter
  - `mypy` - Static type checker

- **Security**
  - `pip-audit` - Vulnerability scanner for Python dependencies
  - Scans both root and `solana-agent-kit-py-main` directories

- **Test**
  - `pytest` - Unit testing framework
  - Runs on Python 3.9, 3.10, 3.11, and 3.12
  - Includes coverage reporting (when configured)

### 3. TypeScript CI Workflow (`typescript-ci.yml`)

**Triggers:** Push/PR affecting TypeScript files  
**Purpose:** TypeScript/JavaScript code quality and security

#### Jobs:
- **Lint & Build**
  - TypeScript compilation check (`tsc`)
  - ESLint (linting)
  - Prettier (formatting)

- **Security**
  - `npm audit` - Vulnerability scanner for npm packages
  - Reports moderate and high-level vulnerabilities

- **Test**
  - Runs configured npm tests

### 4. CodeQL Analysis (`codeql-analysis.yml`)

**Triggers:** Push/PR to main branches, weekly schedule (Mondays at 2:30 AM UTC)  
**Purpose:** Advanced security vulnerability detection

- Analyzes Python and JavaScript/TypeScript code
- Detects:
  - SQL injection
  - Cross-site scripting (XSS)
  - Path traversal
  - Command injection
  - And many other security issues
- Results appear in GitHub Security tab

### 5. OSSF Scorecard (`scorecard.yml`)

**Triggers:** Push to main, weekly schedule (Mondays at 3:00 AM UTC)  
**Purpose:** Repository security posture assessment

Evaluates:
- Branch protection
- Code review practices
- Dependency update practices
- Security policy presence
- And 18+ other security checks

Results available at: https://securityscorecards.dev/

### 6. Dependabot (`dependabot.yml`)

**Triggers:** Weekly schedule (Mondays at 3:00 AM UTC)  
**Purpose:** Automated dependency updates

Monitors:
- Python dependencies (root)
- Python dependencies (solana-agent-kit-py-main)
- npm dependencies (mcp-server)
- GitHub Actions versions

Creates PRs automatically for:
- Security updates
- Version updates
- Grouped by ecosystem

## Configuration Files

### Python Configuration

#### `.ruff.toml`
Ruff linter configuration with:
- Line length: 88 (Black compatible)
- Target: Python 3.9+
- Enabled rules: pycodestyle, Pyflakes, import sorting, naming conventions, etc.

#### `pyproject.toml`
Configuration for:
- **Black**: Code formatter (88 char line length)
- **isort**: Import sorter (Black profile)
- **mypy**: Type checker
- **pytest**: Test framework

### TypeScript Configuration

#### `mcp-server/.eslintrc.json`
ESLint configuration with:
- TypeScript support
- Recommended rules
- Node.js environment

#### `mcp-server/.prettierrc`
Prettier configuration with:
- Single quotes
- 100 char print width
- 2 space indentation
- Trailing commas (ES5)

## Running Locally

### Python

```bash
# Install dev dependencies
pip install ruff black isort mypy pytest pytest-cov pip-audit

# Run linting
ruff check .
black --check .
isort --check-only .
mypy .

# Run security scan
pip-audit

# Run tests
pytest
```

### TypeScript

```bash
cd mcp-server

# Install dependencies
npm install

# Run linting
npm run lint

# Run formatting check
npm run format:check

# Build
npm run build

# Run security scan
npm audit

# Run tests
npm test
```

## CI Status Badges

Add these badges to your README.md to show CI status:

```markdown
![CI](https://github.com/jparram/SolanaAutomation/workflows/CI/badge.svg)
![Python CI](https://github.com/jparram/SolanaAutomation/workflows/Python%20CI/badge.svg)
![TypeScript CI](https://github.com/jparram/SolanaAutomation/workflows/TypeScript%20CI/badge.svg)
![CodeQL](https://github.com/jparram/SolanaAutomation/workflows/CodeQL%20Security%20Analysis/badge.svg)
![OSSF Scorecard](https://github.com/jparram/SolanaAutomation/workflows/OSSF%20Scorecard/badge.svg)
```

## Security Features Summary

### Free GitHub Security Features Enabled:

1. **CodeQL** - SAST (Static Application Security Testing)
   - Automatically scans code for vulnerabilities
   - Supports 7+ languages
   - Results in Security tab

2. **Dependabot** - Dependency Updates
   - Automated security updates
   - Version updates
   - Pull requests created automatically

3. **pip-audit** - Python Dependency Vulnerabilities
   - Scans Python packages
   - Uses PyPI Advisory Database
   - Runs on every push/PR

4. **npm audit** - JavaScript Dependency Vulnerabilities
   - Scans npm packages
   - Uses npm Advisory Database
   - Runs on every push/PR

5. **OSSF Scorecard** - Repository Security Rating
   - Comprehensive security assessment
   - 18+ security checks
   - Public scorecard badge

## Maintenance

### Weekly Automated Tasks:
- CodeQL security scan (Mondays 2:30 AM UTC)
- OSSF Scorecard update (Mondays 3:00 AM UTC)
- Dependabot dependency checks (Mondays 3:00 AM UTC)

### Manual Actions:
- Review and merge Dependabot PRs
- Review security alerts in GitHub Security tab
- Update workflow files as needed

## Best Practices

1. **Always review Dependabot PRs** before merging
2. **Address CodeQL findings** promptly
3. **Keep GitHub Actions up to date** via Dependabot
4. **Monitor OSSF Scorecard** for security improvements
5. **Run linters locally** before pushing
6. **Fix security vulnerabilities** as they're discovered

## Continuous Improvement

Consider adding:
- [ ] More comprehensive test coverage
- [ ] Integration tests
- [ ] Performance testing
- [ ] Container scanning (if using Docker)
- [ ] License compliance checking
- [ ] Code coverage reporting
- [ ] Deployment workflows

## Support

For issues with CI/CD:
1. Check workflow run logs in Actions tab
2. Verify configuration files are valid
3. Ensure dependencies are properly installed
4. Review GitHub documentation for specific actions

## License

Same as parent project.
