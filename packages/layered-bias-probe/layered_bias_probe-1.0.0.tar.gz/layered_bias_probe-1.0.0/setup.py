"""
Setup script for layered-bias-probe package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A comprehensive toolkit for layer-wise bias analysis in language models with fine-tuning support"

# Read requirements from requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback requirements if file not found
    requirements = [
        "torch>=2.0.0",
        "transformers>=4.32.0",
        "datasets>=2.0.0",
        "pandas>=1.5.0",
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

setup(
    name="layered-bias-probe",
    version="1.0.0",
    author="DebK",
    author_email="koushikdeb88@gmail.com",
    description="A comprehensive toolkit for layer-wise bias analysis in language models with fine-tuning support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DebK/layered-bias-probe",  # You'll need to create this GitHub repo
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "layered-bias-probe=layered_bias_probe.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "layered_bias_probe": ["config/*.yaml", "templates/*.txt"],
    },
    keywords="bias nlp language-models weat fairness transformers machine-learning layer-analysis fine-tuning",
    project_urls={
        "Bug Reports": "https://github.com/DebK/layered-bias-probe/issues",
        "Source": "https://github.com/DebK/layered-bias-probe",
        "Documentation": "https://github.com/DebK/layered-bias-probe#readme",
        "Homepage": "https://github.com/DebK/layered-bias-probe",
    },
)
