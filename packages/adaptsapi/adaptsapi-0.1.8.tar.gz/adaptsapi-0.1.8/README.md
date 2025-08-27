# AdaptsAPI Client

A Python client library and CLI for the Adapts API, designed for triggering documentation generation via API Gateway → SNS.

[![PyPI version](https://badge.fury.io/py/adaptsapi.svg)](https://badge.fury.io/py/adaptsapi)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-98%25-green.svg)](https://github.com/adaptsai/adaptsapi)

## Features

- 🚀 **Simple Python Client** for making API calls to Adapts services
- 🔑 **Secure token management** with environment variables or local config
- 📄 **Flexible payload support** via JSON files or inline data
- 🔧 **Configurable endpoints** with default endpoint support
- ✅ **Built-in payload validation** for documentation generation requests
- 🧪 **Comprehensive test suite** with 98% code coverage
- 🤖 **GitHub Actions integration** for automated wiki documentation
- 📦 **CLI tool** for command-line usage

## Installation

### From PyPI

```bash
pip install adaptsapi
```

### From Source

```bash
git clone https://github.com/adaptsai/adaptsapi.git
cd adaptsapi
pip install -e .
```

## Quick Start

### 1. Set up your API token

You can provide your API token in three ways (in order of precedence):

1. **Environment variable** (recommended for CI/CD):
   ```bash
   export ADAPTS_API_KEY="your-api-token-here"
   ```

2. **Local config file** (`config.json` in current directory):
   ```json
   {
     "token": "your-api-token-here",
     "endpoint": "https://your-api-endpoint.com/prod/generate_wiki_docs"
   }
   ```

3. **Interactive prompt** (first-time setup):
   ```bash
   adaptsapi --data '{"test": "payload"}'
   # CLI will prompt for token and save to config.json
   ```

### 2. Using the Python Client

```python
from adaptsapi.generate_docs import post, PayloadValidationError

# Create your payload
payload = {
    "email_address": "user@example.com",
    "user_name": "john_doe",
    "repo_object": {
        "repository_name": "my-repo",
        "source": "github",
        "repository_url": "https://github.com/user/my-repo",
        "branch": "main",
        "size": "12345",
        "language": "python",
        "is_private": False,
        "git_provider_type": "github",
        "refresh_token": "github_token_here"
    }
}

# Make the API call
try:
    response = post(
        "https://api.adapts.ai/prod/generate_wiki_docs",
        "your-api-token",
        payload
    )
    response.raise_for_status()
    result = response.json()
    print("✅ Success:", result)
except PayloadValidationError as e:
    print(f"❌ Validation error: {e}")
except Exception as e:
    print(f"❌ API error: {e}")
```

### 3. Using the CLI

**Using inline JSON data:**
```bash
adaptsapi \
  --endpoint "https://api.adapts.ai/prod/generate_wiki_docs" \
  --data '{"email_address": "user@example.com", "user_name": "john_doe", "repo_object": {...}}'
```

**Using a JSON payload file:**
```bash
adaptsapi \
  --endpoint "https://api.adapts.ai/prod/generate_wiki_docs" \
  --payload-file payload.json
```

## Testing

The library includes a comprehensive test suite with 98% code coverage.

### Running Tests

#### Quick Test Run
```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_generate_docs.py

# Run with coverage report
python -m pytest --cov=src/adaptsapi --cov-report=html
```

#### Using the Test Runner
```bash
# Run unit tests only (fast, no external dependencies)
python run_tests.py --type unit

# Run integration tests (requires API key)
python run_tests.py --type integration

# Run all tests with coverage
python run_tests.py --type coverage

# Run with custom API key
python run_tests.py --type integration --api-key "your-api-key"
```

#### Test Categories

- **Unit Tests**: Fast tests that mock external dependencies
- **Integration Tests**: Tests that make real API calls (marked with `@pytest.mark.integration`)
- **CLI Tests**: Tests for command-line interface functionality
- **Config Tests**: Tests for configuration management

### Test Coverage

The test suite covers:

- ✅ **Payload Validation**: All validation logic and error cases
- ✅ **Metadata Population**: Automatic metadata generation
- ✅ **API Calls**: HTTP request handling and error management
- ✅ **CLI Functionality**: Command-line argument parsing and file handling
- ✅ **Configuration**: Token loading and config file management

### Demo Script

Run the demonstration script to see the library in action:

```bash
python test_generate_docs_demo.py
```

This script shows:
- Payload validation examples
- Metadata population demonstration
- API call structure
- Real API testing (if API key is available)

## Usage

### Command Line Options

```bash
adaptsapi [OPTIONS]
```

| Option | Description | Required |
|--------|-------------|----------|
| `--endpoint URL` | Full URL of the API endpoint | Yes (unless set in config.json) |
| `--data JSON` | Inline JSON payload string | Yes (or --payload-file) |
| `--payload-file FILE` | Path to JSON payload file | Yes (or --data) |
| `--timeout SECONDS` | Request timeout in seconds (default: 30) | No |

### Payload Structure

For documentation generation, your payload should follow this structure:

```json
{
  "email_address": "user@example.com",
  "user_name": "github_username",
  "repo_object": {
    "repository_name": "my-repo",
    "source": "github",
    "repository_url": "https://github.com/user/my-repo",
    "branch": "main",
    "size": "12345",
    "language": "python",
    "is_private": false,
    "git_provider_type": "github",
    "refresh_token": "github_token_here"
  }
}
```

#### Required Fields

- `email_address`: Valid email address
- `user_name`: Username string
- `repo_object.repository_name`: Repository name
- `repo_object.repository_url`: Full repository URL
- `repo_object.branch`: Branch name
- `repo_object.size`: Repository size as string
- `repo_object.language`: Primary programming language
- `repo_object.source`: Source platform (e.g., "github")

#### Optional Fields

- `repo_object.is_private`: Boolean indicating if repo is private
- `repo_object.git_provider_type`: Git provider type
- `repo_object.installation_id`: Installation ID (for GitHub Apps)
- `repo_object.refresh_token`: Refresh token for authentication
- `repo_object.commit_hash`: Specific commit hash
- `repo_object.commit_message`: Commit message
- `repo_object.commit_author`: Commit author
- `repo_object.directory_name`: Specific directory to process

## GitHub Actions Integration

This package is designed to work seamlessly with GitHub Actions for automated documentation generation. Here's an example workflow:

```yaml
name: Generate Wiki Docs

on:
  pull_request:
    branches: [ main ]
    types: [ closed ]

jobs:
  call-adapts-api:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          
      - name: Install adaptsapi
        run: pip install adaptsapi
        
      - name: Generate documentation
        env:
          ADAPTS_API_KEY: ${{ secrets.ADAPTS_API_KEY }}
        run: |
          python -c "
          import os
          from adaptsapi.generate_docs import post
          
          payload = {
              'email_address': '${{ github.actor }}@users.noreply.github.com',
              'user_name': '${{ github.actor }}',
              'repo_object': {
                  'repository_name': '${{ github.event.repository.name }}',
                  'source': 'github',
                  'repository_url': '${{ github.event.repository.html_url }}',
                  'branch': 'main',
                  'size': '0',
                  'language': 'python',
                  'is_private': False,
                  'git_provider_type': 'github',
                  'refresh_token': '${{ secrets.GITHUB_TOKEN }}'
              }
          }
          
          resp = post(
              'https://your-api-endpoint.com/prod/generate_wiki_docs',
              os.environ['ADAPTS_API_KEY'],
              payload
          )
          resp.raise_for_status()
          print('✅ Documentation generated successfully')
          "
```

### Setting up GitHub Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add `ADAPTS_API_KEY` with your API token value

## Configuration

### Config File Format

The `config.json` file in your current working directory can contain:

```json
{
  "token": "your-api-token-here",
  "endpoint": "https://your-default-endpoint.com/prod/generate_wiki_docs"
}
```

### Environment Variables

- `ADAPTS_API_KEY`: Your API authentication token (used by the library)
- `ADAPTS_API_TOKEN`: Alternative token variable (used by CLI)

## Error Handling

The library provides comprehensive error handling:

- **PayloadValidationError**: Raised when payload validation fails
- **ConfigError**: Raised when no token can be found or loaded
- **requests.RequestException**: Raised on network failures
- **JSONDecodeError**: Raised for invalid JSON in config files

### Common Error Scenarios

- **Missing token**: CLI prompts for interactive token input
- **Invalid JSON**: Shows JSON parsing errors
- **API errors**: Displays HTTP status codes and error messages
- **Payload validation**: Shows specific validation failures with field names

## Development

### Prerequisites

- Python 3.10+
- pip

### Setup Development Environment

```bash
git clone https://github.com/adaptsai/adaptsapi.git
cd adaptsapi
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

### Development Dependencies

Install development dependencies for testing and code quality:

```bash
pip install -r requirements-dev.txt
```

This includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `flake8` - Code linting
- `mypy` - Type checking
- `black` - Code formatting
- `isort` - Import sorting

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/adaptsapi --cov-report=html

# Run specific test categories
python -m pytest -m "not integration"  # Unit tests only
python -m pytest -m "integration"      # Integration tests only

# Run the test runner
python run_tests.py --type all
```

### Code Quality

```bash
# Lint code
flake8 src/adaptsapi tests/

# Type checking
mypy src/adaptsapi/

# Format code
black src/adaptsapi tests/
isort src/adaptsapi tests/
```

## Publishing to PyPI

### Prerequisites

Before publishing to PyPI, ensure you have:

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account at [test.pypi.org](https://test.pypi.org/account/register/)
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI
4. **Build Tools**: Install required build tools

```bash
pip install build twine
```

### Build Configuration

The project uses `pyproject.toml` for build configuration. Key settings:

```toml
[project]
name = "adaptsapi"
version = "0.1.4"
description = "CLI to enqueue triggers via internal API Gateway → SNS"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.10"
authors = [
  { name = "VerifyAI Inc.", email = "dev@adapts.ai" }
]
dependencies = [
  "requests",
]
```

### Publishing Steps

#### 1. Prepare for Release

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info src/*.egg-info

# Update version in pyproject.toml and setup.py
# Edit version numbers in both files

# Run all tests to ensure everything works
python run_tests.py --type all

# Check code quality
flake8 src/adaptsapi tests/
mypy src/adaptsapi/
```

#### 2. Build Distribution Packages

```bash
# Build source distribution and wheel
python -m build

# Verify the built packages
ls -la dist/
# Should show: adaptsapi-0.1.4.tar.gz and adaptsapi-0.1.4-py3-none-any.whl
```

#### 3. Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ adaptsapi

# Test the installed package
python -c "from adaptsapi.generate_docs import post; print('✅ Package works!')"
```

#### 4. Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Verify installation from PyPI
pip install adaptsapi

# Test the installed package
python -c "from adaptsapi.generate_docs import post; print('✅ Package published successfully!')"
```

### Automated Publishing with GitHub Actions

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
          
      - name: Install dependencies
        run: |
          pip install build twine
          pip install -r requirements-dev.txt
          
      - name: Run tests
        run: |
          python run_tests.py --type unit
          
      - name: Build package
        run: python -m build
        
      - name: Publish to TestPyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
        run: |
          python -m twine upload --repository testpypi dist/*
          
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          python -m twine upload dist/*
```

### Environment Variables for CI/CD

Set these secrets in your GitHub repository:

- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your TestPyPI API token

### Version Management

#### Semantic Versioning

Follow [semantic versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 0.1.4)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

#### Update Version Numbers

Update version in these files:

1. **pyproject.toml**:
   ```toml
   [project]
   version = "0.1.5"  # Update this
   ```

2. **setup.py**:
   ```python
   setup(
       name="adaptsapi",
       version="0.1.5",  # Update this
       # ...
   )
   ```

### Pre-release Checklist

Before publishing, ensure:

- [ ] All tests pass: `python run_tests.py --type all`
- [ ] Code is linted: `flake8 src/adaptsapi tests/`
- [ ] Type checking passes: `mypy src/adaptsapi/`
- [ ] Documentation is updated
- [ ] Version numbers are updated in both `pyproject.toml` and `setup.py`
- [ ] CHANGELOG is updated
- [ ] Package builds successfully: `python -m build`
- [ ] Package installs correctly: `pip install dist/*.whl`

### Troubleshooting

#### Common Issues

1. **"File already exists" error**:
   ```bash
   # Clean previous builds
   rm -rf build/ dist/ *.egg-info src/*.egg-info
   python -m build
   ```

2. **Authentication errors**:
   ```bash
   # Check your API token
   python -m twine check dist/*
   ```

3. **Package not found after upload**:
   - Wait a few minutes for PyPI to process
   - Check the package page: https://pypi.org/project/adaptsapi/

4. **Import errors after installation**:
   ```bash
   # Verify package structure
   pip show adaptsapi
   python -c "import adaptsapi; print(adaptsapi.__file__)"
   ```

#### Rollback Strategy

If you need to rollback a release:

1. **Delete the release** (if within 24 hours):
   ```bash
   # Use PyPI web interface to delete the release
   # Go to: https://pypi.org/manage/project/adaptsapi/releases/
   ```

2. **Yank the release** (recommended):
   ```bash
   python -m twine delete --username __token__ --password $PYPI_API_TOKEN adaptsapi 0.1.4
   ```

3. **Publish a new patch version** with fixes

### Security Best Practices

1. **Use API tokens** instead of username/password
2. **Store tokens securely** in environment variables or secrets
3. **Use TestPyPI** for testing before production
4. **Verify package contents** before uploading
5. **Keep dependencies updated** and secure

### Package Verification

After publishing, verify the package:

```bash
# Install from PyPI
pip install adaptsapi

# Test imports
python -c "
from adaptsapi.generate_docs import post, PayloadValidationError
from adaptsapi.cli import main
from adaptsapi.config import load_token
print('✅ All imports successful!')
"

# Test CLI
adaptsapi --help

# Run tests
python -m pytest tests/test_generate_docs.py -v
```

## API Reference

### Core Functions

#### `post(endpoint, auth_token, payload, timeout=30)`

Make a POST request to the Adapts API with automatic payload validation and metadata population.

**Parameters:**
- `endpoint` (str): The API endpoint URL
- `auth_token` (str): Authentication token
- `payload` (dict): JSON payload to send
- `timeout` (int): Request timeout in seconds (default: 30)

**Returns:**
- `requests.Response`: The HTTP response object

**Raises:**
- `PayloadValidationError`: If payload validation fails
- `requests.RequestException`: If the HTTP request fails

#### `_validate_payload(payload)`

Validate the payload structure and data types.

**Parameters:**
- `payload` (dict): The payload to validate

**Raises:**
- `PayloadValidationError`: If validation fails

#### `_populate_metadata(payload)`

Automatically populate metadata fields in the payload.

**Parameters:**
- `payload` (dict): The payload to populate with metadata

### CLI Functions

#### `main()`

Main CLI entry point that handles argument parsing and API calls.

### Configuration Functions

#### `load_token()`

Load authentication token from environment variables or config file.

**Returns:**
- `str`: The authentication token

**Raises:**
- `ConfigError`: If no token can be found

#### `load_default_endpoint()`

Load default endpoint from config file.

**Returns:**
- `str | None`: The default endpoint URL or None

## Project Structure

```
adaptsapi/
├── src/adaptsapi/
│   ├── __init__.py
│   ├── generate_docs.py    # Main API client functionality
│   ├── cli.py             # Command-line interface
│   └── config.py          # Configuration management
├── tests/
│   ├── conftest.py        # Test fixtures and configuration
│   ├── test_generate_docs.py  # Tests for generate_docs module
│   ├── test_cli.py        # Tests for CLI functionality
│   └── test_config.py     # Tests for configuration management
├── run_tests.py           # Test runner script
├── test_generate_docs_demo.py  # Demonstration script
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Development dependencies
├── pytest.ini           # Pytest configuration
└── TESTING.md           # Detailed testing guide
```

## License

This software is licensed under the Adapts API Use-Only License v1.0. See [LICENSE](LICENSE) for details.

**Key restrictions:**
- ✅ Use the software as-is
- ❌ No modifications allowed
- ❌ No redistribution allowed
- ❌ Commercial use restrictions apply

## Support

- 📧 Email: dev@adapts.ai
- 🐛 Issues: [GitHub Issues](https://github.com/adaptsai/adaptsapi/issues)
- 📖 Documentation: This README and [TESTING.md](TESTING.md)

## Changelog

### v0.1.4 (Latest)
- ✅ Comprehensive test suite with 98% coverage
- ✅ Improved error handling and validation
- ✅ Enhanced CLI functionality
- ✅ Better configuration management
- ✅ Development tools and documentation

### v0.1.3
- Patch updates

### v0.1.2
- Initial stable release

---

© 2025 AdaptsAI All rights reserved.