#!/usr/bin/env python3
"""
Setup script for rules-mcp-server
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="rules-mcp-server",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Model Context Protocol server for development rules and best practices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rules-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rules-mcp-server=server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["rules/*.md", "*.md"],
    },
    keywords="mcp model-context-protocol development-rules best-practices coding-standards",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/rules-mcp-server/issues",
        "Source": "https://github.com/yourusername/rules-mcp-server",
    },
)