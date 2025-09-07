#!/bin/bash
# Build script for creating LogLog .deb package

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="loglog"
VERSION="1.0.0"
BUILD_DIR="build"
PACKAGE_DIR="packaging"

echo -e "${GREEN}=== LogLog Package Builder ===${NC}"
echo "Building ${PACKAGE_NAME} version ${VERSION}"

# Check for required tools
echo -e "\n${YELLOW}Checking build dependencies...${NC}"
MISSING_DEPS=()

if ! command -v dpkg-buildpackage >/dev/null 2>&1; then
    MISSING_DEPS+="devscripts"
fi

if ! command -v dh >/dev/null 2>&1; then
    MISSING_DEPS+="debhelper"
fi

if ! command -v python3 >/dev/null 2>&1; then
    MISSING_DEPS+="python3"
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo "Install with: sudo apt install devscripts debhelper python3 python3-setuptools dh-python"
    exit 1
fi

echo -e "${GREEN}✓ All build dependencies found${NC}"

# Clean previous builds
echo -e "\n${YELLOW}Cleaning previous builds...${NC}"
rm -rf "${BUILD_DIR}"
rm -f ../${PACKAGE_NAME}_${VERSION}*
rm -f ../${PACKAGE_NAME}-dbgsym_*

# Create build directory structure
echo -e "\n${YELLOW}Setting up build directory...${NC}"
mkdir -p "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}"

# Copy source files
echo -e "${YELLOW}Copying source files...${NC}"
cp -r . "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/" 2>/dev/null || {
    # Handle case where we're already in a subdirectory
    cp *.py "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/"
    cp *.md "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/"
    cp *.txt "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/" 2>/dev/null || true
    cp -r docs "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/" 2>/dev/null || true
    cp -r demo "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/" 2>/dev/null || true
    cp -r tests "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/" 2>/dev/null || true
    cp -r packaging "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/"
    cp LICENSE "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/" 2>/dev/null || true
}

# Copy Debian package files to correct location
echo -e "${YELLOW}Setting up Debian packaging files...${NC}"
cp -r packaging/debian "${BUILD_DIR}/${PACKAGE_NAME}-${VERSION}/"

# Create source tarball
echo -e "\n${YELLOW}Creating source tarball...${NC}"
cd "${BUILD_DIR}"
tar -czf "${PACKAGE_NAME}_${VERSION}.orig.tar.gz" "${PACKAGE_NAME}-${VERSION}"

# Build the package
echo -e "\n${YELLOW}Building Debian package...${NC}"
cd "${PACKAGE_NAME}-${VERSION}"

# Set environment for build
export DEBEMAIL="info@loglog.dev"
export DEBFULLNAME="LogLog Development Team"

# Build package
echo -e "${GREEN}Running dpkg-buildpackage...${NC}"
dpkg-buildpackage -us -uc -b

# Move back to original directory
cd ../..

# Check results
echo -e "\n${GREEN}=== Build Complete ===${NC}"
if ls "${BUILD_DIR}"/../${PACKAGE_NAME}_${VERSION}*.deb >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Package built successfully:${NC}"
    ls -la "${BUILD_DIR}"/../${PACKAGE_NAME}_${VERSION}*.deb
    
    # Copy to current directory for easy access
    cp "${BUILD_DIR}"/../${PACKAGE_NAME}_${VERSION}*.deb .
    echo -e "\n${GREEN}✓ Package copied to current directory${NC}"
    
    # Show package info
    echo -e "\n${YELLOW}Package information:${NC}"
    dpkg-deb --info ${PACKAGE_NAME}_${VERSION}*.deb
    
    echo -e "\n${GREEN}Build successful! You can install with:${NC}"
    echo "sudo dpkg -i ${PACKAGE_NAME}_${VERSION}*.deb"
    echo "sudo apt-get install -f  # Fix any dependency issues"
    
else
    echo -e "${RED}✗ Package build failed${NC}"
    exit 1
fi