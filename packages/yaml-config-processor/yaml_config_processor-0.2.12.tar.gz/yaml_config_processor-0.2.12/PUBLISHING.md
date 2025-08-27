# Publishing to PyPI

This guide provides instructions for publishing the yaml-config-processor package to PyPI.

## Prerequisites

1. Create accounts on both [PyPI](https://pypi.org) and [TestPyPI](https://test.pypi.org)
2. Install required tools:
   ```bash
   pip install build twine
   ```

## Preparing for Release

1. Update version number in:
    - `yaml_config_processor/__init__.py`
    - `setup.py`

2. Update the CHANGELOG.md file with the latest changes

3. Make sure all tests pass:
   ```bash
   pytest
   ```

## Building the Package

1. Clean previous builds:
   ```bash
   rm -rf build/ dist/ *.egg-info/
   ```

2. Build the package:
   ```bash
   python -m build
   ```

This will create both source distribution and wheel in the `dist/` directory.

## Testing on TestPyPI (Recommended)

1. Upload to TestPyPI:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. Install from TestPyPI in a new environment:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ yaml-config-processor
   ```

3. Verify that the package works correctly

## Publishing to PyPI

Once you've verified the package works correctly on TestPyPI:

```bash
python -m twine upload dist/*
```

## Verifying Installation

```bash
pip install yaml-config-processor
```

Try importing and using the package:

```python
from yaml_config_processor import ConfigProcessor
processor = ConfigProcessor()
# Use the package...
```

## Setting Up Automated Publishing (Optional)

Consider setting up GitHub Actions to automate the testing and publishing process.
