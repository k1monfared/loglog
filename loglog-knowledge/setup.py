#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="loglog-knowledge",
    version="0.1.0",
    author="LogLog Knowledge Graph",
    author_email="",
    description="Knowledge graph service for LogLog hierarchical documents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/loglog-knowledge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "networkx>=3.0",
        "anthropic>=0.7.0",
        "asyncio",
        "aiohttp>=3.8.0",
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "loglog-kg=loglog_knowledge.cli:main",
        ],
    },
)