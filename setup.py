#!/usr/bin/env python3
"""
LogLog setup script for creating distributable packages.
"""

from setuptools import setup, find_packages
import os
import re

def get_version():
    """Extract version from loglog.py"""
    version_file = os.path.join(os.path.dirname(__file__), 'loglog.py')
    with open(version_file, 'r') as f:
        content = f.read()
    # Look for __version__ or a simple version pattern
    # For now, we'll set a fixed version
    return "1.0.0"

def read_long_description():
    """Read the long description from README"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def read_requirements():
    """Read requirements from requirements.txt if it exists"""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='loglog',
    version=get_version(),
    author='LogLog Development Team',
    author_email='info@loglog.dev',
    description='A hierarchical note-taking format and CLI tool for zero-overhead structured notes',
    long_description=read_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/loglog/loglog',
    project_urls={
        'Documentation': 'https://github.com/loglog/loglog/blob/main/docs/CLI_USAGE.md',
        'Source': 'https://github.com/loglog/loglog',
        'Tracker': 'https://github.com/loglog/loglog/issues',
    },
    
    # Package discovery
    py_modules=['loglog'],
    packages=find_packages(),
    
    # Dependencies
    python_requires='>=3.8',
    install_requires=read_requirements(),
    
    # Entry points for CLI
    entry_points={
        'console_scripts': [
            'loglog=loglog_cli:main',
        ],
    },
    
    # Package data
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt', '*.log'],
        'docs': ['*.md'],
        'demo': ['*'],
        'tests': ['*'],
    },
    
    # Metadata
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Office/Business',
        'Topic :: Text Processing :: Markup',
        'Topic :: Utilities',
    ],
    
    keywords='notes, todo, cli, markdown, hierarchical, productivity',
    
    # Optional dependencies
    extras_require={
        'pdf': ['pdflatex'],  # System dependency, not Python package
        'dev': ['pytest', 'black', 'flake8'],
    },
    
    # Data files for system installation
    data_files=[
        ('share/doc/loglog', ['README.md', 'LICENSE']),
        ('share/doc/loglog/docs', ['docs/CLI_USAGE.md', 'docs/FEATURES.md']),
        ('share/man/man1', ['packaging/loglog.1']),  # We'll create this
    ],
)