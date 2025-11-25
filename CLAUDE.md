# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python playground for experimenting with AWS services. The project uses Python 3.13.9 managed by pyenv and uv for package management.

## Development Commands

### Package Management
```bash
# Install/sync dependencies
uv sync

# Add new dependencies
uv add <package-name>

# Run Python scripts (uv automatically uses .venv)
uv run python scripts/your_script.py
# or
uv run scripts/your_script.py

# Interactive Python with project dependencies
uv run python
```

**Important:** Do NOT manually activate `.venv`. The `uv run` command automatically uses the virtual environment.

### Running Code
```bash
# Run the main entry point
uv run python main.py

# Run any script in the scripts/ directory
uv run python scripts/<script_name>.py
```

## Project Architecture

### Directory Structure
- `scripts/` - Example scripts for AWS experiments
- `main.py` - Main entry point (currently a placeholder)
- `.venv/` - Virtual environment (managed by uv, do not modify manually)
- `pyproject.toml` - Project configuration and dependencies

### Dependencies
- `boto3` (>=1.41.3) - AWS SDK for Python, used for interacting with AWS services
- `awscli-local` (>=0.22.2) - LocalStack AWS CLI wrapper for local AWS testing

## Code Conventions

Since this is an experimental playground:
- Scripts should be self-contained and placed in the `scripts/` directory
- Use boto3 for AWS service interactions
- Scripts should handle AWS credentials gracefully (boto3 will use default AWS credential chain)
