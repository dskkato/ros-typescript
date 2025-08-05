# Python ROS Packages

This directory contains Python ports of selected ROS utilities.

## Setup

Use a virtual environment with Python 3.10 or newer, then install the project in editable mode with its development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Pre-commit hooks

This project uses [pre-commit](https://pre-commit.com/) to run code quality checks:

```bash
pre-commit install
pre-commit run --files $(git ls-files '*.py')
```

## Testing

Run the unit tests with `pytest`:

```bash
pytest
```
