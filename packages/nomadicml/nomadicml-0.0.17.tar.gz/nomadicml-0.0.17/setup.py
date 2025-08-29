"""Setup script for the NomadicML SDK."""

import os
import re
from setuptools import setup, find_packages

# Function to extract version from __init__.py
def get_version():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(current_dir, "nomadicml", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        version_match = re.search(r"^__version__ = ['\"']([^'\"']*)['\"']", f.read(), re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nomadicml",
    version=get_version(), # Dynamically get version
    author="NomadicML Inc",
    author_email="info@nomadicml.com",
    description="Python SDK for NomadicML's DriveMonitor API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/nomadicml/nomadicml-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=3.10.0",
        "backoff>=2.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "types-requests>=2.28.0",
        ],
    },
)