# LogLog Packaging Guide

This document explains how to build and distribute LogLog packages for Ubuntu and Debian systems.

## Overview

LogLog is packaged as a standard Debian package (.deb) that can be installed on Ubuntu, Debian, and other Debian-based distributions. The package provides:

- System-wide installation of the `loglog` command
- Python module installation
- Manual page documentation  
- Example files and documentation

## Quick Start

### Building the Package

1. **Install build dependencies:**
   ```bash
   sudo apt install devscripts debhelper python3 python3-setuptools dh-python
   ```

2. **Build the package:**
   ```bash
   ./build_package.sh
   ```

3. **Test the package:**
   ```bash
   ./test_package.sh
   ```

4. **Install locally:**
   ```bash
   sudo dpkg -i loglog_1.0.0-1_all.deb
   sudo apt-get install -f  # Fix any missing dependencies
   ```

## Package Structure

### Files Included

- **Binary:** `/usr/bin/loglog` - Main CLI executable
- **Python Module:** `/usr/lib/python3/dist-packages/loglog.py` - Core library
- **Documentation:** `/usr/share/doc/loglog/` - README, usage guides
- **Manual Page:** `/usr/share/man/man1/loglog.1` - Man page
- **Examples:** Included in documentation directory

### Dependencies

**Required:**
- `python3 (>= 3.8)` - Core Python interpreter

**Recommended:**
- `pandoc` - For LaTeX conversion support
- `texlive-latex-base` - For PDF generation

**Suggested:**
- `texlive-latex-extra` - Additional LaTeX packages

## Building Process

### Build Scripts

**`build_package.sh`** - Main build script that:
- Checks build dependencies
- Creates proper directory structure
- Copies source files
- Builds the Debian package using `dpkg-buildpackage`
- Validates the output

**`test_package.sh`** - Comprehensive test suite that:
- Installs the package
- Tests all CLI commands
- Verifies file locations
- Checks Python module import
- Validates functionality with real examples

### Build Environment

The build process creates these directories:
```
build/
├── loglog-1.0.0/           # Source directory
│   ├── debian/             # Debian packaging files
│   ├── loglog.py          # Core module
│   ├── loglog_cli.py      # CLI implementation
│   └── ...                # Other source files
└── loglog_1.0.0.orig.tar.gz  # Source tarball
```

## Package Metadata

### Control File Information

- **Package Name:** `loglog`
- **Section:** `text` (text processing utilities)
- **Priority:** `optional`
- **Architecture:** `all` (pure Python, platform independent)
- **Maintainer:** LogLog Development Team

### Standards Compliance

- **Debian Policy:** 4.5.0
- **Debhelper Compat:** 12
- **Python Policy:** Compatible with Python 3.8+

## Ubuntu Repository Submission

### Prerequisites for Official Repository

To submit LogLog to Ubuntu repositories, you need:

1. **Package Quality:**
   - Lintian-clean package (no policy violations)
   - Comprehensive testing on multiple Ubuntu versions
   - Proper copyright and licensing information

2. **Legal Requirements:**
   - Clear MIT license for all code
   - No patent or trademark issues
   - Proper upstream source attribution

3. **Community Process:**
   - Ubuntu Developer membership or sponsorship
   - Package review by Ubuntu developers
   - Integration with Ubuntu's build system

### Submission Process

#### 1. Prepare for Review

```bash
# Check package quality
lintian loglog_1.0.0-1_all.deb

# Test on multiple Ubuntu versions
# - Ubuntu 20.04 LTS (Focal)
# - Ubuntu 22.04 LTS (Jammy) 
# - Ubuntu 24.04 LTS (Noble)
```

#### 2. Upload to Personal Package Archive (PPA)

```bash
# Sign the package
debuild -S -sa

# Upload to Launchpad PPA
dput ppa:yourusername/loglog loglog_1.0.0-1_source.changes
```

#### 3. Request Inclusion

- Submit a "Request for Package" (RFP) bug to Ubuntu
- Get sponsor/reviewer feedback
- Address any issues raised
- Wait for acceptance

### Alternative Distribution Methods

#### 1. Personal Package Archive (PPA)

Create a Launchpad PPA for easier user installation:

```bash
sudo add-apt-repository ppa:loglog/stable
sudo apt update
sudo apt install loglog
```

#### 2. GitHub Releases

Distribute .deb files through GitHub releases:

```bash
# Tag release
git tag v1.0.0
git push origin v1.0.0

# Upload .deb file to GitHub release
# Users can download and install with:
# sudo dpkg -i loglog_1.0.0-1_all.deb
```

#### 3. Direct Download

Host .deb files on a website with installation instructions.

## Quality Assurance

### Automated Testing

The package includes comprehensive tests:

```bash
# Basic functionality
loglog --version
loglog --help

# Core operations
loglog show test.log
loglog convert test.log --to html
loglog stats test.log

# Advanced features
loglog filter test.log --hashtags important
loglog todos test.log --status pending
loglog search "keyword" test.log
```

### Manual Testing Checklist

- [ ] Package installs without errors
- [ ] All CLI commands work correctly
- [ ] Python module imports successfully
- [ ] Man page displays properly
- [ ] Documentation files are accessible
- [ ] Package uninstalls cleanly
- [ ] No file conflicts with other packages

### Lintian Checks

Run lintian to check Debian policy compliance:

```bash
lintian loglog_1.0.0-1_all.deb
lintian loglog_1.0.0-1.dsc
```

Address any warnings or errors before submission.

## Troubleshooting

### Common Build Issues

**Missing Dependencies:**
```bash
sudo apt install devscripts debhelper python3-dev python3-setuptools dh-python
```

**Build Fails:**
- Check `debian/rules` file permissions
- Ensure all required files are present
- Verify Python module imports work

**Package Installation Issues:**
```bash
# Fix broken dependencies
sudo apt-get install -f

# Force installation (use carefully)
sudo dpkg -i --force-depends loglog_1.0.0-1_all.deb
```

### Testing Different Ubuntu Versions

Use Docker for testing on different versions:

```bash
# Test on Ubuntu 20.04
docker run -it ubuntu:20.04
apt update && apt install -y python3 python3-pip
# Install and test package

# Test on Ubuntu 22.04
docker run -it ubuntu:22.04
# Repeat testing
```

## Continuous Integration

Consider setting up CI/CD pipelines for automated testing:

```yaml
# .github/workflows/package.yml
name: Build and Test Package
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: sudo apt install devscripts debhelper python3-setuptools dh-python
      - name: Build package
        run: ./build_package.sh
      - name: Test package  
        run: ./test_package.sh
```

## Maintenance

### Version Updates

1. Update `packaging/debian/changelog`
2. Increment version in `setup.py`
3. Test thoroughly on supported platforms
4. Build and distribute new package

### Security Updates

- Monitor dependencies for security issues
- Apply patches promptly
- Coordinate with Ubuntu security team if needed

## Resources

- [Debian New Maintainer's Guide](https://www.debian.org/doc/manuals/maint-guide/)
- [Ubuntu Packaging Guide](https://packaging.ubuntu.com/html/)
- [Python Packaging for Debian](https://wiki.debian.org/Python/LibraryStyleGuide)
- [Launchpad PPA Documentation](https://help.launchpad.net/Packaging/PPA)