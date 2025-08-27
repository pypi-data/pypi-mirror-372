# Contributing Guide

## Quick Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the project in development mode
pip install -e ".[dev]"
```

## Development Commands

```bash
check                     # Run all checks (format, lint, tests)
check --fix               # Auto-fix issues and run all checks
check --fast              # Format + lint only (skip tests)

gen-models                # Generate models from API spec
```

## Workflow

1. **Before committing:** Run `check --fix` to auto-fix issues
2. **During development:** Use `check --fast` for quick validation
3. **Update models:** Run `gen-models` when API changes

## Release Process

### GitHub Actions Release

1. Go to the **Actions** tab in GitHub
2. Select the **Release** workflow
3. Click **Run workflow** and choose:
   - **Version type**: `patch` (default), `minor`, or `major`
   - **Dry run**: Test the release process without publishing
   - **Production**: Upload to PyPI instead of TestPyPI

The workflow will automatically:

- ✅ Run all tests, linting, and formatting checks (reuses existing test workflow)
- 🔄 Generate fresh models from the API spec
- 📈 Increment the version using Hatch
- 📦 Build the package
- 🚀 Upload to TestPyPI (or PyPI if production mode)
- 🏷️ Create a Git tag and GitHub release
- 📋 Provide detailed summary with links

### Required Repository Secrets

Configure these secrets in your GitHub repository settings:

- `TEST_PYPI_API_TOKEN`: Token for https://test.pypi.org/
- `PYPI_API_TOKEN`: Token for https://pypi.org/ (production releases)

### Getting API Tokens

1. **TestPyPI**: Go to https://test.pypi.org/manage/account/token/
2. **PyPI**: Go to https://pypi.org/manage/account/token/
3. Create a token with upload permissions
4. Add the token to your repository secrets

## IDE Setup (VS Code)

Install extensions:

- [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

## Troubleshooting

- **Command not found:** Activate virtual environment with `source .venv/bin/activate`
- **Linting failures:** Run `check --fix` to auto-fix issues
- **Model import errors:** Run `gen-models` to regenerate models
- **Release failures:** Check API tokens are configured in repository secrets and try a dry run first
