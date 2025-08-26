#!/usr/bin/env python3
"""
Setup script for rust-crate-pipeline
"""

from setuptools import find_packages, setup

# Read version from the package
try:
    from rust_crate_pipeline.version import __version__
except ImportError:
    __version__ = "3.0.0"

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rust-crate-pipeline",
    version=__version__,
    description=(
        "Enterprise-grade Rust crate analysis with AI-powered insights, "
        "advanced caching, ML predictions, and microservices architecture"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SuperUser666-Sigil",
    author_email="miragemodularframework@gmail.com",
    url="https://github.com/Superuser666-Sigil/SigilDERG-Data_Production",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "aiohttp>=3.9.0,<4.0.0",
        "pydantic>=2.5.0,<3.0.0",
        "click>=8.1.0,<9.0.0",
        "rich>=13.7.0,<14.0.0",
        "tqdm>=4.66.0,<5.0.0",
        "cachetools>=5.3.0,<6.0.0",
        "aiofiles>=24.1.0,<25.0.0",
        "redis>=5.0.0,<6.0.0",
        "scikit-learn>=1.3.0,<2.0.0",
        "numpy>=1.24.0,<2.0.0",
        "pandas>=2.0.0,<3.0.0",
        "PyJWT>=2.8.0,<3.0.0",
        "prometheus-client>=0.17.0,<1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "rust-crate-pipeline=rust_crate_pipeline.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Monitoring",
    ],
    keywords="rust,crate,analysis,ai,llm,pipeline,caching,ml,microservices",
)
