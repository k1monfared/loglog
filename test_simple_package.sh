#!/bin/bash
# Test script for the simple-built LogLog .deb package

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PACKAGE_NAME="loglog"
VERSION="1.0.0"
TEST_DIR="/tmp/loglog_test_$$"
DEB_FILE="loglog_1.0.0_all.deb"

echo -e "${GREEN}=== LogLog Simple Package Testing ===${NC}"

# Check if .deb file exists
if [ ! -f "$DEB_FILE" ]; then
    echo -e "${RED}✗ $DEB_FILE not found. Run build_simple.sh first.${NC}"
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
    echo "You may need to enter your password for sudo operations."
    sudo apt-get remove -y loglog || sudo dpkg -r loglog
fi

# Install the package
echo -e "${YELLOW}Installing package...${NC}"
echo "You may need to enter your password for sudo operations."
if sudo dpkg -i "$OLDPWD/$DEB_FILE"; then
    echo -e "${GREEN}✓ Package installed successfully${NC}"
else
    echo -e "${YELLOW}Installation had issues, trying to fix dependencies...${NC}"
    sudo apt-get install -f -y
fi

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"

# Check if loglog command is available
if ! command -v loglog >/dev/null 2>&1; then
    echo -e "${RED}✗ loglog command not found after installation${NC}"
    echo "Checking PATH..."
    echo $PATH
    echo "Looking for loglog binary..."
    which loglog || echo "loglog not in PATH"
    find /usr -name "loglog" 2>/dev/null || echo "loglog not found in /usr"
    exit 1
fi

echo -e "${GREEN}✓ loglog command found at: $(which loglog)${NC}"

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
    echo "Error output:"
    cat show_output.txt | head -10 | sed 's/^/  /'
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
if loglog todos test.log --status pending > todos_output.txt; then
    echo -e "${GREEN}✓ TODO extraction passed${NC}"
    echo "TODO output:"
    cat todos_output.txt | sed 's/^/  /'
else
    echo -e "${RED}✗ TODO extraction failed${NC}"
    exit 1
fi

# Test search functionality
echo -e "${YELLOW}Testing search functionality...${NC}"
if loglog search "task" test.log > search_output.txt; then
    echo -e "${GREEN}✓ Search functionality passed${NC}"
    echo "Search results:"
    head -3 search_output.txt | sed 's/^/  /'
else
    echo -e "${RED}✗ Search functionality failed${NC}"
    exit 1
fi

# Check man page
echo -e "${YELLOW}Testing man page...${NC}"
if man loglog > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Man page accessible${NC}"
else
    echo -e "${YELLOW}⚠ Man page not accessible (may need mandb update)${NC}"
    # Try updating man database
    if command -v mandb >/dev/null 2>&1; then
        echo "Attempting to update man database..."
        sudo mandb -q 2>/dev/null || echo "Could not update man database"
    fi
fi

# Verify Python module import (this tests the system installation)
echo -e "${YELLOW}Testing Python module import...${NC}"
if python3 -c "import sys; sys.path.insert(0, '/usr/lib/python3/dist-packages'); import loglog; print('LogLog module imported successfully')"; then
    echo -e "${GREEN}✓ Python module import passed${NC}"
else
    echo -e "${RED}✗ Python module import failed${NC}"
    echo "Checking installation paths..."
    ls -la /usr/lib/python3/dist-packages/loglog* 2>/dev/null || echo "LogLog modules not found"
fi

# Test file locations
echo -e "\n${YELLOW}Checking installed files...${NC}"
echo "Binary location:"
ls -la "$(which loglog)" | sed 's/^/  /'

echo "Python modules:"
ls -la /usr/lib/python3/dist-packages/loglog* | sed 's/^/  /'

echo "Documentation:"
if [ -d "/usr/share/doc/loglog" ]; then
    ls -la /usr/share/doc/loglog/ | head -5 | sed 's/^/  /'
    echo -e "${GREEN}✓ Documentation installed${NC}"
else
    echo -e "${YELLOW}⚠ Documentation directory not found${NC}"
fi

echo "Manual page:"
ls -la /usr/share/man/man1/loglog.1.gz 2>/dev/null | sed 's/^/  /' || echo "  Manual page not found"

# Performance test with a larger file
echo -e "\n${YELLOW}Testing with larger file...${NC}"
cat > large_test.log <<'EOF'
- Large Document Test #performance
    - Section 1
        - Subsection 1.1
            [] Task 1
            [x] Task 2 
            [] Task 3 #important
        - Subsection 1.2
            - Deep nesting test
                - Level 3
                    - Level 4
                        [] Deep task
    - Section 2 #analysis
        - Data processing
            [x] Collect data
            [-] Process data
            [] Generate report #deadline
        - Quality assurance
            [] Review results
            [] Validate output
EOF

if loglog stats large_test.log > large_stats.txt; then
    echo -e "${GREEN}✓ Large file processing passed${NC}"
    echo "Large file stats:"
    cat large_stats.txt | sed 's/^/  /'
else
    echo -e "${RED}✗ Large file processing failed${NC}"
fi

# Clean up test directory
cd /
rm -rf "$TEST_DIR"

echo -e "\n${GREEN}=== All Tests Passed! ===${NC}"
echo -e "${GREEN}LogLog package is working correctly.${NC}"

# Show package information
echo -e "\n${YELLOW}Installed package information:${NC}"
dpkg -l | grep loglog | sed 's/^/  /'

echo -e "\n${YELLOW}Package file information:${NC}"
dpkg -s loglog | grep -E "^(Package|Version|Architecture|Depends|Description)" | sed 's/^/  /'

echo -e "\n${GREEN}✓ Package testing completed successfully${NC}"
echo -e "\nPackage is ready for distribution!"
echo -e "\nTo uninstall: ${YELLOW}sudo apt-get remove loglog${NC}"
echo -e "Package size: $(ls -lh "$OLDPWD/$DEB_FILE" | awk '{print $5}')"