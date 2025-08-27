#!/usr/bin/env python3
"""
Setup for the package
"""

from setuptools import setup, find_packages

from nci_cidc_cli import __version__

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="nci_cidc_cli",
    version=__version__,
    packages=find_packages(exclude=("tests")),
    entry_points={"console_scripts": ["nci-cidc = nci_cidc_cli.cli:cidc"]},
    description="A command-line interface for interacting with the NCI CIDC.",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    python_requires=">=3.6",
)
