# BlazeMetrics: Release and Publishing Guide

This guide documents how to create new versions, push updates to GitHub, and publish releases to PyPI using our automated CI/CD pipeline.

## 🚀 Quick Release Process

For a new version release, follow these steps:

### 1. Update Version
```bash
# Edit pyproject.toml and update version
# Example: version = "0.1.1"
```

### 2. Commit and Tag
```bash
git add pyproject.toml
git commit -m "Bump version to 0.1.1"
git tag v0.1.1
git push origin main
git push origin v0.1.1
```

### 3. Automated Publishing
The CI workflow will automatically:
- Build wheels for Windows, macOS, and Linux
- Run tests on all supported Python versions
- Publish to PyPI (if tag starts with 'v')
- Update GitHub releases

## 📋 Prerequisites

- Python 3.8+
- Rust toolchain with `cargo` (install via https://rustup.rs/)
- Tools: `maturin`, `twine`, `setuptools`, `wheel`
- PyPI account and an API token
- GitHub account (`2796gaurav`) and repository `blazemetrics`

Install tools:
```powershell
python -m pip install --upgrade pip setuptools wheel maturin twine
```

## 🔧 Repository Configuration

### GitHub Secrets Setup
1. Go to https://pypi.org/manage/account/token/
2. Create a new API token with "Entire account" scope
3. Copy the token
4. Go to your GitHub repo: https://github.com/2796gaurav/blazemetrics/settings/secrets/actions
5. Click "New repository secret"
6. Name: `PYPI_API_TOKEN`
7. Value: paste your PyPI token

### CI/CD Workflows
- **`.github/workflows/test.yml`**: Runs on every push to test builds
- **`.github/workflows/wheels.yml`**: Publishes wheels to PyPI on tag releases

## 📦 Version Management

### Updating Version Numbers
Update in `pyproject.toml`:
```toml
[project]
name = "blazemetrics"
version = "0.1.1"  # Update this
```

Optionally update `Cargo.toml` for consistency:
```toml
[package]
name = "blazemetrics"
version = "0.1.1"  # Keep in sync
```

### Version Numbering Convention
- **Patch** (0.1.1): Bug fixes, minor improvements
- **Minor** (0.2.0): New features, backward compatible
- **Major** (1.0.0): Breaking changes

## 🔄 Release Workflow

### Automated Release (Recommended)
```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 0.1.1"

# 3. Create and push tag
git tag v0.1.1
git push origin main
git push origin v0.1.1

# 4. CI automatically builds and publishes to PyPI
# 5. Verify on PyPI: https://pypi.org/project/blazemetrics/
```

### Manual Release (Fallback)
If CI fails or you need manual control:

```bash
# Build distributions
maturin build --release --out dist
maturin sdist --out dist

# Validate
twine check dist/*

# Upload to PyPI
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-<YOUR_TOKEN>"
twine upload dist/*
```

## 🏷️ GitHub Releases

### Creating a GitHub Release
1. Go to https://github.com/2796gaurav/blazemetrics/releases
2. Click "Create a new release"
3. Tag: `v0.1.1` (must match your git tag)
4. Title: `BlazeMetrics v0.1.1`
5. Description: Add release notes, changes, etc.
6. Check "Set as the latest release"
7. Click "Publish release"

### Release Notes Template
```markdown
## What's New in v0.1.1

### 🚀 Features
- New feature A
- Enhanced feature B

### 🐛 Bug Fixes
- Fixed issue with X
- Resolved Y problem

### 📦 Installation
```bash
pip install blazemetrics==0.1.1
```

### 🔗 Links
- [Documentation](https://github.com/2796gaurav/blazemetrics)
- [PyPI Package](https://pypi.org/project/blazemetrics/)
```

## ✅ Pre-Release Checklist

Before creating a new version:

- [ ] Version updated in `pyproject.toml`
- [ ] `README.md` badges/links point to correct repository
- [ ] `LICENSE` present and correct
- [ ] All tests pass locally
- [ ] Documentation updated if needed
- [ ] Changelog/release notes prepared
- [ ] PyPI API token configured in GitHub secrets

## 🧪 Testing Before Release

### Local Testing
```bash
# Build and test locally
maturin build --release
pip install target/wheels/*.whl

# Test import and basic functionality
python -c "
from blazemetrics import rouge_score, bleu
candidates = ['the cat sat on the mat']
references = [['the cat was on the mat']]
print('ROUGE:', rouge_score(candidates, references, score_type='rouge_n', n=1))
print('BLEU:', bleu(candidates, references))
print('✅ All tests passed!')
"
```

### CI Testing
- Push to a feature branch to trigger test workflow
- Verify all platforms build successfully
- Check that wheels are generated correctly

## 🔍 Post-Release Verification

After a release:

1. **PyPI**: Check https://pypi.org/project/blazemetrics/
   - Version appears in release history
   - Wheels available for your platform
   - README renders correctly

2. **GitHub**: Check https://github.com/2796gaurav/blazemetrics/releases
   - Release notes are complete
   - Assets (wheels) are attached

3. **Installation Test**:
   ```bash
   pip install blazemetrics==0.1.1
   python -c "import blazemetrics; print('✅ Installation successful')"
   ```

## 🚨 Troubleshooting

### Common Issues

**CI Build Fails**
- Check GitHub Actions logs
- Verify Rust toolchain is available
- Ensure all dependencies are in `pyproject.toml`

**PyPI Upload Fails**
- Verify `PYPI_API_TOKEN` is set in GitHub secrets
- Check token has correct permissions
- Ensure version number is unique

**Wheels Not Available**
- Check CI workflow completed successfully
- Verify wheels were built for target platform
- Look for build errors in CI logs

**Import Errors After Install**
- Ensure wheel was built for correct Python version
- Check platform compatibility
- Verify Rust extension compiled correctly

### Manual Recovery
If automated release fails:

```bash
# Build manually
maturin build --release --compatibility manylinux2014 -o dist
maturin sdist -o dist

# Upload manually
twine upload dist/*

# Create GitHub release manually
# Go to GitHub releases page and create release
```

## 📚 Additional Resources

- [PyPI Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [Maturin Documentation](https://maturin.rs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)

## 🎯 Release Flow Summary

1. **Update** version in `pyproject.toml`
2. **Commit** changes with descriptive message
3. **Tag** with `vX.Y.Z` format
4. **Push** tag to trigger CI
5. **Verify** PyPI and GitHub releases
6. **Test** installation on target platforms

That's it! The automated CI/CD pipeline handles the complex build and publishing process, so you can focus on code quality and user experience. 🚀 