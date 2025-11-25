# AWS Experiments

Playground for experimenting with AWS services using Python.

## Setup

**Python Version:** 3.13.9 (managed by pyenv)
**Package Manager:** uv (no activation needed!)

```bash
# Install/sync dependencies
uv sync

# Add new dependencies
uv add <package-name>

# Run scripts (uv automatically uses the virtual environment)
uv run python scripts/your_script.py

# Or simply
uv run scripts/your_script.py

# Run Python interactively with project dependencies
uv run python
```

**Note:** With `uv`, you don't need to activate `.venv` manually. The `uv run` command automatically uses the project's virtual environment.

## Dependencies

- boto3 - AWS SDK for Python
- awscli-local - LocalStack AWS CLI wrapper

## Project Structure

```
aws-experiments/
├── scripts/         # Example scripts
├── .venv/          # Virtual environment (uv managed)
├── .python-version # Python 3.13.9
└── pyproject.toml  # Project dependencies
```
