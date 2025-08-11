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

## Benchmarking

Run the benchmark suite with [`pytest-benchmark`](https://pytest-benchmark.readthedocs.io/):

```bash
python -m python_ros.bench.benny
```

Example output:

```
test_new_reader[int8 array]                                2.6280 (1.00)         52.4570 (1.0)          3.1941 (1.02)
test_new_reader[std_msgs/Header]                           2.6290 (1.00)        648.8670 (12.37)        3.2809 (1.05)
...
15 passed in 8.45s
```
