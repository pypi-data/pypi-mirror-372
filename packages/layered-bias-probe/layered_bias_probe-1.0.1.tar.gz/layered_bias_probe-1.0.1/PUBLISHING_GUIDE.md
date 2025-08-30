# Publishing layered-bias-probe to PyPI

## 🎯 Goal
Make `layered-bias-probe` available via `pip install layered-bias-probe`

## 📋 Prerequisites

1. **Create PyPI accounts:**
   - Production: https://pypi.org/account/register/
   - Testing: https://test.pypi.org/account/register/

2. **Install publishing tools:**
   ```bash
   pip install --upgrade pip
   pip install --upgrade build twine
   ```

## 🔧 Step 1: Prepare Package for Publishing

### Update setup.py with publishing metadata:

```python
# Add these fields to setup.py
setup(
    name="layered-bias-probe",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Layer-wise bias analysis and fine-tuning for large language models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/layered-bias-probe",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/layered-bias-probe/issues",
        "Documentation": "https://github.com/yourusername/layered-bias-probe#readme",
        "Source Code": "https://github.com/yourusername/layered-bias-probe",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="bias, nlp, language-models, weat, fairness, transformers",
)
```

### Create additional required files:

1. **LICENSE file** (choose a license):
   ```
   MIT License
   
   Copyright (c) 2025 Your Name
   
   Permission is hereby granted, free of charge, to any person obtaining a copy...
   ```

2. **MANIFEST.in** (include additional files):
   ```
   include README.md
   include LICENSE
   include requirements.txt
   recursive-include layered_bias_probe/config *.yaml
   recursive-include examples *.py
   ```

3. **pyproject.toml** (modern packaging):
   ```toml
   [build-system]
   requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]
   build-backend = "setuptools.build_meta"
   
   [project]
   name = "layered-bias-probe"
   dynamic = ["version"]
   description = "Layer-wise bias analysis and fine-tuning for large language models"
   readme = "README.md"
   license = {text = "MIT"}
   authors = [
       {name = "Your Name", email = "your.email@example.com"},
   ]
   classifiers = [
       "Development Status :: 4 - Beta",
       "Intended Audience :: Developers",
       "Intended Audience :: Science/Research",
       "License :: OSI Approved :: MIT License",
       "Operating System :: OS Independent",
       "Programming Language :: Python :: 3",
       "Programming Language :: Python :: 3.8",
       "Programming Language :: Python :: 3.9",
       "Programming Language :: Python :: 3.10",
       "Programming Language :: Python :: 3.11",
       "Topic :: Scientific/Engineering :: Artificial Intelligence",
   ]
   requires-python = ">=3.8"
   dependencies = [
       "torch>=1.9.0",
       "transformers>=4.20.0",
       "datasets>=2.0.0",
       "pandas>=1.3.0",
       "numpy>=1.21.0",
       "scikit-learn>=1.0.0",
       "tqdm>=4.60.0",
       "accelerate>=0.20.0",
       "bitsandbytes>=0.39.0",
       "huggingface-hub>=0.14.0",
       "plotly>=5.0.0",
       "matplotlib>=3.5.0",
       "seaborn>=0.11.0",
       "click>=8.0.0",
       "pyyaml>=6.0",
   ]
   
   [project.urls]
   Homepage = "https://github.com/yourusername/layered-bias-probe"
   Repository = "https://github.com/yourusername/layered-bias-probe"
   Issues = "https://github.com/yourusername/layered-bias-probe/issues"
   
   [project.scripts]
   layered-bias-probe = "layered_bias_probe.cli:main"
   
   [tool.setuptools_scm]
   ```

## 🔧 Step 2: Build the Package

```bash
# Navigate to package directory
cd layered-bias-probe

# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build
```

This creates:
- `dist/layered_bias_probe-0.1.0-py3-none-any.whl` (wheel)
- `dist/layered-bias-probe-0.1.0.tar.gz` (source)

## 🧪 Step 3: Test on TestPyPI First

### Upload to TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

### Test installation from TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ layered-bias-probe
```

## 🚀 Step 4: Upload to Production PyPI

Once testing is successful:

```bash
python -m twine upload dist/*
```

Enter your PyPI credentials when prompted.

## 🎉 Step 5: Verify Installation

After upload, anyone can install with:
```bash
pip install layered-bias-probe
```

## 🔄 Step 6: Version Updates

For future updates:

1. Update version in setup.py or pyproject.toml
2. Update CHANGELOG.md
3. Rebuild and upload:
   ```bash
   rm -rf build/ dist/ *.egg-info/
   python -m build
   python -m twine upload dist/*
   ```

## 🛡️ Security Best Practices

1. **Use API tokens instead of passwords:**
   - Generate token at https://pypi.org/manage/account/token/
   - Create `~/.pypirc`:
     ```ini
     [pypi]
     username = __token__
     password = pypi-AgEIcHlwaS5vcmc...
     ```

2. **Enable 2FA** on your PyPI account

3. **Use trusted publishing** with GitHub Actions (advanced)

## 📊 Monitoring

After publishing:
- Monitor downloads: https://pypistats.org/packages/layered-bias-probe
- Track issues: GitHub Issues
- Monitor security: Dependabot alerts

---

## 🚨 Important Notes

1. **Package name must be unique** on PyPI
2. **Cannot delete versions** once uploaded
3. **Test thoroughly** on TestPyPI first
4. **Keep backups** of your source code
5. **Document breaking changes** in version updates
