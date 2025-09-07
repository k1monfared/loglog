#!/bin/bash
# Test script for LogLog .deb package installation and functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PACKAGE_NAME="loglog"
VERSION="1.0.0"
TEST_DIR="/tmp/loglog_test_$$"

echo -e "${GREEN}=== LogLog Package Testing ===${NC}"

# Find the .deb file
DEB_FILE=$(ls ${PACKAGE_NAME}_${VERSION}*.deb 2>/dev/null | head -1)
if [ -z "$DEB_FILE" ]; then
    echo -e "${RED}✗ No .deb file found. Run build_package.sh first.${NC}"
    exit 1
fi

echo "Testing package: $DEB_FILE"

# Create test directory
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# Create test LogLog file
echo -e "${YELLOW}Creating test LogLog file...${NC}"
cat > test.log <<'EOF'
- Test Document #test
    - Features to test
        [] CLI conversion
        [] TODO extraction
        [] Hashtag filtering
    - Expected behavior #important
        - Should convert to HTML
        - Should find TODOs
        - Should filter by hashtags

- Another section
    - With nested content
        [x] Completed task
        [-] In progress task
        [] Pending task #urgent
EOF

echo -e "${GREEN}✓ Test file created${NC}"

# Test package installation
echo -e "\n${YELLOW}Testing package installation...${NC}"

# Check if package is already installed
if dpkg -l | grep -q "^ii.*loglog"; then
    echo -e "${YELLOW}LogLog is already installed, uninstalling first...${NC}"
    sudo apt-get remove -y loglog || sudo dpkg -r loglog
fi

# Install the package
echo -e "${YELLOW}Installing package...${NC}"
sudo dpkg -i "$OLDPWD/$DEB_FILE" || {
    echo -e "${YELLOW}Fixing dependencies...${NC}"
    sudo apt-get install -f -y
}

# Check if installation was successful
if ! command -v loglog >/dev/null 2>&1; then
    echo -e "${RED}✗ loglog command not found after installation${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Package installed successfully${NC}"

# Test basic functionality
echo -e "\n${YELLOW}Testing CLI functionality...${NC}"

# Test version
echo -e "${YELLOW}Testing --version...${NC}"
if loglog --version; then
    echo -e "${GREEN}✓ Version check passed${NC}"
else
    echo -e "${RED}✗ Version check failed${NC}"
    exit 1
fi

# Test help
echo -e "${YELLOW}Testing --help...${NC}"
if loglog --help > /dev/null; then
    echo -e "${GREEN}✓ Help command passed${NC}"
else
    echo -e "${RED}✗ Help command failed${NC}"
    exit 1
fi

# Test show command
echo -e "${YELLOW}Testing show command...${NC}"
if loglog show test.log > show_output.txt; then
    echo -e "${GREEN}✓ Show command passed${NC}"
    echo "Output preview:"
    head -5 show_output.txt | sed 's/^/  /'
else
    echo -e "${RED}✗ Show command failed${NC}"
    exit 1
fi

# Test stats command
echo -e "${YELLOW}Testing stats command...${NC}"
if loglog stats test.log > stats_output.txt; then
    echo -e "${GREEN}✓ Stats command passed${NC}"
    echo "Stats output:"
    cat stats_output.txt | sed 's/^/  /'
else
    echo -e "${RED}✗ Stats command failed${NC}"
    exit 1
fi

# Test convert command
echo -e "${YELLOW}Testing convert to HTML...${NC}"
if loglog convert test.log --to html --overwrite; then
    if [ -f "test.html" ]; then
        echo -e "${GREEN}✓ HTML conversion passed${NC}"
        echo "HTML file size: $(wc -c < test.html) bytes"
    else
        echo -e "${RED}✗ HTML file was not created${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ HTML conversion failed${NC}"
    exit 1
fi

# Test filter command
echo -e "${YELLOW}Testing filter by hashtag...${NC}"
if loglog filter test.log --hashtags test --output filtered.log; then
    if [ -f "filtered.log" ]; then
        echo -e "${GREEN}✓ Hashtag filtering passed${NC}"
        echo "Filtered content:"
        cat filtered.log | sed 's/^/  /'
    else
        echo -e "${RED}✗ Filtered file was not created${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Hashtag filtering failed${NC}"
    exit 1
fi

# Test TODO extraction
echo -e "${YELLOW}Testing TODO extraction...${NC}"
if loglog todos test.log --status pending; then
    echo -e "${GREEN}✓ TODO extraction passed${NC}"
else
    echo -e "${RED}✗ TODO extraction failed${NC}"
    exit 1
fi

# Test search functionality
echo -e "${YELLOW}Testing search functionality...${NC}"
if loglog search "task" test.log > search_output.txt; then
    echo -e "${GREEN}✓ Search functionality passed${NC}"
    echo "Search results:"
    cat search_output.txt | head -3 | sed 's/^/  /'
else
    echo -e "${RED}✗ Search functionality failed${NC}"
    exit 1
fi

# Check man page
echo -e "${YELLOW}Testing man page...${NC}"
if man loglog > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Man page installed${NC}"
else
    echo -e "${YELLOW}⚠ Man page not accessible (may need mandb update)${NC}"
fi

# Verify Python module import
echo -e "${YELLOW}Testing Python module import...${NC}"
if python3 -c "import loglog; print('LogLog module imported successfully')"; then
    echo -e "${GREEN}✓ Python module import passed${NC}"
else
    echo -e "${RED}✗ Python module import failed${NC}"
    exit 1
fi

# Test file locations
echo -e "\n${YELLOW}Checking installed files...${NC}"
echo "Checking binary location:"
which loglog | sed 's/^/  /'

echo "Checking documentation:"
if [ -d "/usr/share/doc/loglog" ]; then
    ls -la /usr/share/doc/loglog/ | head -5 | sed 's/^/  /'
    echo -e "${GREEN}✓ Documentation installed${NC}"
else
    echo -e "${YELLOW}⚠ Documentation directory not found${NC}"
fi

# Clean up test directory
cd /
rm -rf "$TEST_DIR"

echo -e "\n${GREEN}=== All Tests Passed! ===${NC}"
echo -e "${GREEN}LogLog package is working correctly.${NC}"

# Show package information
echo -e "\n${YELLOW}Package information:${NC}"
dpkg -l | grep loglog | sed 's/^/  /'

echo -e "\n${GREEN}✓ Package testing completed successfully${NC}"
echo -e "\nTo uninstall: ${YELLOW}sudo apt-get remove loglog${NC}"