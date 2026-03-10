"""Package setup for infra-audit."""

from setuptools import setup, find_packages

setup(
    name="infra-audit",
    version="0.1.0",
    description="CLI tool that audits Linux/macOS servers for common security and reliability issues.",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "infra-audit=infra_audit.cli:main",
        ],
    },
)
