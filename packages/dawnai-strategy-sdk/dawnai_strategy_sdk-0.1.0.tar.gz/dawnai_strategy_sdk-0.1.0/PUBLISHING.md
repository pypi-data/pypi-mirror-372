# SDK Publishing Guide

## Automated Publishing

The SDK is automatically published to PyPI when changes are detected in the `sdk/` directory and pushed to the main or develop branches.

### Workflow

1. **Develop Branch** → Test PyPI
   - Changes pushed to `develop` branch trigger tests
   - If tests pass and version is new, publishes to Test PyPI
   - Test package: https://test.pypi.org/project/dawnai-strategy-sdk/

2. **Main Branch** → PyPI
   - Changes pushed to `main` branch trigger tests
   - If tests pass and version is new, publishes to PyPI
   - Production package: https://pypi.org/project/dawnai-strategy-sdk/
   - Creates a Git tag: `sdk-vX.Y.Z`

### Version Management

Before publishing, ensure you've bumped the version in `pyproject.toml`:

```bash
# Bump version (patch/minor/major)
cd sdk
python scripts/bump_version.py patch  # or minor/major

# Check what will change
python scripts/bump_version.py patch --dry-run
```

### Manual Publishing (if needed)

```bash
cd sdk

# Build the package
python -m build

# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### Required Secrets

The following secrets need to be configured in GitHub repository settings:

- `PYPI_TOKEN`: PyPI API token for publishing to PyPI
- `TEST_PYPI_TOKEN`: Test PyPI API token for publishing to Test PyPI

### Testing Changes

1. Make changes to SDK code
2. Update version in `pyproject.toml`
3. Push to `develop` branch
4. Check Test PyPI for the new version
5. Test installation: `pip install -i https://test.pypi.org/simple/ dawnai-strategy-sdk==X.Y.Z`
6. If successful, create PR to `main` branch
7. After merge, package will be published to PyPI

### Troubleshooting

- **Version already exists**: The workflow checks if a version already exists on PyPI and skips publishing if it does
- **No changes detected**: The workflow only runs when files in `sdk/` directory are modified
- **Test failures**: Publishing is blocked if tests fail; fix the tests before attempting to publish