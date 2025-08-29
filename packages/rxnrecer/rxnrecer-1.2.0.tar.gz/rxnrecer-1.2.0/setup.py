#!/usr/bin/env python3
"""Setup script for RXNRECer package."""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rxnrecer",
    version="1.2.0",
    author="RXNRECer Team",
    author_email="contact@rxnrecer.org",
    description="Deep learning framework for predicting enzyme-catalyzed reactions from protein sequences",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kingstdio/RXNRECer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "biopython>=1.79",
        "requests>=2.25.0",
        "tqdm>=4.62.0",
        "click>=8.0.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "boto3>=1.26.0",
        "feather-format>=0.4.1",
        "pyarrow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rxnrecer=rxnrecer.cli.predict:main",
            "rxnrecer-download-data=rxnrecer.cli.download:download_data",
            "rxnrecer-cache=rxnrecer.cli.cache:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
