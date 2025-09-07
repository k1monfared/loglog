#!/bin/bash
# Simple build script that creates a .deb package without system package installation
# This uses a more basic approach with fakeroot and dpkg-deb

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PACKAGE_NAME="loglog"
VERSION="1.0.0"
ARCH="all"
BUILD_DIR="build_simple"

echo -e "${GREEN}=== LogLog Simple Package Builder ===${NC}"
echo "Building ${PACKAGE_NAME} version ${VERSION} (${ARCH})"

# Clean previous builds
echo -e "\n${YELLOW}Cleaning previous builds...${NC}"
rm -rf "${BUILD_DIR}"
rm -f "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

# Create directory structure
echo -e "\n${YELLOW}Creating package structure...${NC}"
mkdir -p "${BUILD_DIR}/DEBIAN"
mkdir -p "${BUILD_DIR}/usr/bin"
mkdir -p "${BUILD_DIR}/usr/lib/python3/dist-packages"
mkdir -p "${BUILD_DIR}/usr/share/man/man1"
mkdir -p "${BUILD_DIR}/usr/share/doc/${PACKAGE_NAME}"

# Create control file
echo -e "${YELLOW}Creating control file...${NC}"
cat > "${BUILD_DIR}/DEBIAN/control" <<EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Architecture: ${ARCH}
Depends: python3 (>= 3.8)
Recommends: pandoc, texlive-latex-base
Suggests: texlive-latex-extra
Section: text
Priority: optional
Maintainer: LogLog Development Team <info@loglog.dev>
Homepage: https://github.com/loglog/loglog
Description: Hierarchical note-taking format and CLI tool
 LogLog is a hierarchical note-taking format that eliminates structural
 decision-making from the writing process. Everything is a list, even
 list items are lists, allowing you to start writing at any depth level
 and reorganize later through simple indentation.
 .
 Features include:
  * Zero structural overhead - focus on content, not formatting
  * Cross-platform plain text files
  * Algorithmically parseable for powerful tooling
  * TODO management with status tracking
  * Format conversion (HTML, Markdown, LaTeX, PDF)
  * Hashtag filtering and content extraction
  * Batch processing capabilities
  * Interactive HTML export with keyboard navigation
 .
 The package includes a comprehensive command-line interface for
 file conversion, content filtering, TODO management, and batch operations.
EOF

# Create main executable
echo -e "${YELLOW}Creating main executable...${NC}"
cat > "${BUILD_DIR}/usr/bin/loglog" <<'EOF'
#!/usr/bin/env python3
"""
LogLog CLI - Main executable wrapper
"""
import sys
import os

# Add the package directory to Python path
sys.path.insert(0, '/usr/lib/python3/dist-packages')

try:
    from loglog_cli import main
    sys.exit(main())
except ImportError as e:
    print(f"Error: Could not import loglog_cli: {e}", file=sys.stderr)
    print("Please ensure LogLog is properly installed.", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

chmod +x "${BUILD_DIR}/usr/bin/loglog"

# Copy Python modules
echo -e "${YELLOW}Copying Python modules...${NC}"
cp loglog.py "${BUILD_DIR}/usr/lib/python3/dist-packages/"
cp loglog_cli.py "${BUILD_DIR}/usr/lib/python3/dist-packages/"

# Copy manual page
echo -e "${YELLOW}Copying manual page...${NC}"
cp packaging/loglog.1 "${BUILD_DIR}/usr/share/man/man1/"
gzip "${BUILD_DIR}/usr/share/man/man1/loglog.1"

# Copy documentation
echo -e "${YELLOW}Copying documentation...${NC}"
cp README.md "${BUILD_DIR}/usr/share/doc/${PACKAGE_NAME}/"
cp LICENSE "${BUILD_DIR}/usr/share/doc/${PACKAGE_NAME}/" 2>/dev/null || echo "LICENSE not found, skipping"
cp docs/CLI_USAGE.md "${BUILD_DIR}/usr/share/doc/${PACKAGE_NAME}/" 2>/dev/null || echo "CLI_USAGE.md not found, skipping"

# Create copyright file
cat > "${BUILD_DIR}/usr/share/doc/${PACKAGE_NAME}/copyright" <<EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: loglog
Upstream-Contact: LogLog Development Team <info@loglog.dev>
Source: https://github.com/loglog/loglog

Files: *
Copyright: 2024 LogLog Development Team
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
EOF

# Create changelog
cat > "${BUILD_DIR}/usr/share/doc/${PACKAGE_NAME}/changelog.Debian.gz" <<EOF
loglog (1.0.0-1) unstable; urgency=medium

  * Initial release of LogLog hierarchical note-taking tool
  * Complete CLI interface with argparse-based commands
  * File conversion to HTML, Markdown, LaTeX, and PDF formats
  * Content filtering by hashtags and TODO status
  * Batch processing capabilities for multiple files
  * Search functionality with regex support
  * Statistics and analysis tools
  * Interactive HTML export with keyboard navigation
  * TODO management with status tracking
  * Cross-platform compatibility with plain text format
  * Zero external Python dependencies (uses standard library only)
  * Comprehensive documentation and examples

 -- LogLog Development Team <info@loglog.dev>  Sat, 07 Sep 2024 00:00:00 +0000
EOF

# Compress changelog
gzip "${BUILD_DIR}/usr/share/doc/${PACKAGE_NAME}/changelog.Debian.gz"

# Set correct permissions
echo -e "${YELLOW}Setting permissions...${NC}"
find "${BUILD_DIR}" -type d -exec chmod 755 {} \;
find "${BUILD_DIR}" -type f -exec chmod 644 {} \;
chmod +x "${BUILD_DIR}/usr/bin/loglog"
chmod +x "${BUILD_DIR}/DEBIAN/control"

# Calculate installed size
INSTALLED_SIZE=$(du -sk "${BUILD_DIR}" | cut -f1)
echo "Installed-Size: ${INSTALLED_SIZE}" >> "${BUILD_DIR}/DEBIAN/control"

# Build the package
echo -e "\n${YELLOW}Building package with dpkg-deb...${NC}"
if command -v fakeroot >/dev/null 2>&1; then
    fakeroot dpkg-deb --build "${BUILD_DIR}" "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
else
    echo -e "${YELLOW}fakeroot not found, building directly (may show ownership warnings)...${NC}"
    dpkg-deb --build "${BUILD_DIR}" "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
fi

# Check results
echo -e "\n${GREEN}=== Build Complete ===${NC}"
if [ -f "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb" ]; then
    echo -e "${GREEN}✓ Package built successfully:${NC}"
    ls -la "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
    
    # Show package info
    echo -e "\n${YELLOW}Package information:${NC}"
    dpkg-deb --info "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
    
    echo -e "\n${GREEN}Build successful! You can install with:${NC}"
    echo "sudo dpkg -i ${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"
    echo "sudo apt-get install -f  # Fix any dependency issues"
    
    # Optional: Run lintian if available
    if command -v lintian >/dev/null 2>&1; then
        echo -e "\n${YELLOW}Running lintian checks...${NC}"
        lintian "${PACKAGE_NAME}_${VERSION}_${ARCH}.deb" || echo "Some lintian warnings (this is normal for simple builds)"
    fi
    
else
    echo -e "${RED}✗ Package build failed${NC}"
    exit 1
fi