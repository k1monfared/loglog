#!/bin/bash
# Demo script showing the complete LogLog package workflow
# This demonstrates building, testing, and using the .deb package

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            LogLog Package Demo               ║${NC}"
echo -e "${BLUE}║     From Source to Installable .deb         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"

echo -e "\n${GREEN}This demo shows the complete workflow:${NC}"
echo "1. Building a Debian package from source"
echo "2. Testing the package functionality"
echo "3. Demonstrating real-world usage"
echo "4. Package management operations"

read -p "Press Enter to continue..."

echo -e "\n${YELLOW}═══ Step 1: Package Structure Overview ═══${NC}"
echo -e "${GREEN}Current repository structure:${NC}"
tree -I '__pycache__|*.pyc|.git|build' -L 2

echo -e "\n${GREEN}Package configuration files:${NC}"
echo "• setup.py - Python package configuration"
echo "• packaging/debian/control - Package metadata"  
echo "• packaging/debian/rules - Build instructions"
echo "• packaging/loglog.1 - Manual page"
echo "• build_package.sh - Automated build script"
echo "• test_package.sh - Comprehensive test suite"

read -p "Press Enter to continue to building..."

echo -e "\n${YELLOW}═══ Step 2: Building the Package ═══${NC}"
echo -e "${GREEN}Checking build dependencies...${NC}"

# Check if build tools are available
MISSING_DEPS=()
command -v dpkg-buildpackage >/dev/null 2>&1 || MISSING_DEPS+=("devscripts")
command -v dh >/dev/null 2>&1 || MISSING_DEPS+=("debhelper")
command -v python3 >/dev/null 2>&1 || MISSING_DEPS+=("python3")

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo -e "${RED}Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo "Install with: sudo apt install devscripts debhelper python3 python3-setuptools dh-python"
    echo -e "${YELLOW}Demo will continue with simulation...${NC}"
    SIMULATE=1
else
    echo -e "${GREEN}✓ All build dependencies found${NC}"
    SIMULATE=0
fi

if [ $SIMULATE -eq 0 ]; then
    echo -e "\n${GREEN}Building package with build_package.sh...${NC}"
    ./build_package.sh || {
        echo -e "${RED}Build failed - continuing with demo anyway${NC}"
        SIMULATE=1
    }
else
    echo -e "${YELLOW}Simulating package build...${NC}"
    echo "$ ./build_package.sh"
    echo "=== LogLog Package Builder ==="
    echo "Building loglog version 1.0.0"
    echo "✓ All build dependencies found"
    echo "✓ Setting up build directory..."
    echo "✓ Creating source tarball..."
    echo "✓ Building Debian package..."
    echo "✓ Package built successfully:"
    echo "loglog_1.0.0-1_all.deb"
fi

read -p "Press Enter to continue to testing..."

echo -e "\n${YELLOW}═══ Step 3: Package Testing ═══${NC}"

if [ $SIMULATE -eq 0 ] && [ -f loglog_1.0.0-1_all.deb ]; then
    echo -e "${GREEN}Testing the built package...${NC}"
    echo "Note: Testing requires sudo privileges for package installation"
    
    read -p "Run actual package tests? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./test_package.sh
    else
        echo -e "${YELLOW}Skipping actual installation test${NC}"
    fi
else
    echo -e "${YELLOW}Simulating package testing...${NC}"
    echo "$ ./test_package.sh"
    echo "=== LogLog Package Testing ==="
    echo "Testing package: loglog_1.0.0-1_all.deb"
    echo "✓ Package installed successfully"
    echo "✓ Version check passed"
    echo "✓ Help command passed"
    echo "✓ Show command passed"
    echo "✓ Stats command passed"
    echo "✓ HTML conversion passed"
    echo "✓ Hashtag filtering passed"
    echo "✓ TODO extraction passed"
    echo "✓ Search functionality passed"
    echo "✓ Man page installed"
    echo "✓ Python module import passed"
    echo "=== All Tests Passed! ==="
fi

read -p "Press Enter to continue to usage demo..."

echo -e "\n${YELLOW}═══ Step 4: Real-World Usage Demo ═══${NC}"
echo -e "${GREEN}Creating sample LogLog files...${NC}"

# Create demo directory
mkdir -p /tmp/loglog_demo
cd /tmp/loglog_demo

# Create sample files
cat > project.log <<'EOF'
- Project Planning #planning
    - Requirements Gathering #important
        [] Define user stories
        [] Create wireframes  
        [x] Research competitors
    - Technical Architecture #decision
        - Backend: Python FastAPI
        - Frontend: React TypeScript
        - Database: PostgreSQL
        [] Set up development environment
        [] Create CI/CD pipeline
    - Timeline #schedule
        - Phase 1: MVP (Q1 2024)
        - Phase 2: Beta (Q2 2024)
        - Phase 3: Launch (Q3 2024)

- Development Progress #status
    - Completed Features
        [x] User authentication
        [x] Basic CRUD operations
        [x] API documentation
    - In Progress #current
        [-] Frontend dashboard
        [-] Email notifications
    - Upcoming #next
        [] Mobile app development
        [] Performance optimization
        [] Security audit #important
EOF

cat > meeting_notes.log <<'EOF'
- Weekly Standup - March 15 #meeting
    - Team Updates
        - Alice: Working on authentication module
        - Bob: Fixing database performance issues
        - Carol: Designing new UI components
    - Blockers #blockers
        [] Need approval for cloud infrastructure budget
        [] Waiting for API keys from third-party service
    - Action Items #actions
        [] Schedule architecture review meeting
        [] Update project timeline based on new requirements
        [x] Send demo link to stakeholders

- Client Meeting - March 16 #meeting #client
    - Feedback on MVP Demo
        - Positive response to core functionality
        - Requested additional reporting features
        - Concerns about mobile responsiveness
    - Next Steps #important
        [] Prioritize mobile optimization
        [] Create detailed project proposal for Phase 2
        [] Schedule follow-up demo in two weeks
EOF

echo -e "${GREEN}Sample files created:${NC}"
ls -la *.log

echo -e "\n${GREEN}Demonstrating LogLog CLI commands:${NC}"

echo -e "\n${BLUE}1. Show file structure:${NC}"
echo "$ loglog show project.log"
if command -v loglog >/dev/null 2>&1; then
    loglog show project.log | head -15
    echo "  ... (truncated)"
else
    python3 "$OLDPWD/loglog_cli.py" show project.log | head -15
    echo "  ... (truncated)"
fi

echo -e "\n${BLUE}2. File statistics:${NC}"
echo "$ loglog stats *.log"
if command -v loglog >/dev/null 2>&1; then
    loglog stats *.log
else
    python3 "$OLDPWD/loglog_cli.py" stats *.log
fi

echo -e "\n${BLUE}3. Filter by hashtags:${NC}"
echo "$ loglog filter project.log --hashtags important --output important_items.log"
if command -v loglog >/dev/null 2>&1; then
    loglog filter project.log --hashtags important --output important_items.log
else
    python3 "$OLDPWD/loglog_cli.py" filter project.log --hashtags important --output important_items.log
fi
echo "Content of filtered file:"
cat important_items.log | head -8

echo -e "\n${BLUE}4. Extract pending TODOs:${NC}"
echo "$ loglog todos *.log --status pending --format json"
if command -v loglog >/dev/null 2>&1; then
    loglog todos *.log --status pending --format json | head -20
else
    python3 "$OLDPWD/loglog_cli.py" todos *.log --status pending --format json | head -20
fi
echo "  ... (truncated)"

echo -e "\n${BLUE}5. Convert to HTML:${NC}"
echo "$ loglog convert project.log --to html"
if command -v loglog >/dev/null 2>&1; then
    loglog convert project.log --to html --overwrite
else
    python3 "$OLDPWD/loglog_cli.py" convert project.log --to html --overwrite
fi
echo "Generated files:"
ls -la *.html *.log

# Clean up
cd "$OLDPWD"
rm -rf /tmp/loglog_demo

echo -e "\n${YELLOW}═══ Step 5: Package Information ═══${NC}"

if [ $SIMULATE -eq 0 ] && [ -f loglog_1.0.0-1_all.deb ]; then
    echo -e "${GREEN}Package details:${NC}"
    dpkg-deb --info loglog_1.0.0-1_all.deb | head -15
    
    echo -e "\n${GREEN}Package contents:${NC}"
    dpkg-deb --contents loglog_1.0.0-1_all.deb | head -10
    echo "  ... and more"
else
    echo -e "${GREEN}Package details (example):${NC}"
    echo " Package: loglog"
    echo " Version: 1.0.0-1"
    echo " Architecture: all"
    echo " Depends: python3 (>= 3.8)"
    echo " Section: text"
    echo " Priority: optional"
    echo " Description: Hierarchical note-taking format and CLI tool"
    echo "  LogLog eliminates structural decision-making from writing..."
fi

echo -e "\n${YELLOW}═══ Installation Instructions ═══${NC}"
echo -e "${GREEN}For end users:${NC}"

if [ $SIMULATE -eq 0 ] && [ -f loglog_1.0.0-1_all.deb ]; then
    echo "1. Download the .deb package: loglog_1.0.0-1_all.deb"
else
    echo "1. Download the .deb package from GitHub releases or build locally"
fi

cat <<EOF
2. Install the package:
   sudo dpkg -i loglog_1.0.0-1_all.deb
   sudo apt-get install -f  # Fix any dependency issues

3. Verify installation:
   loglog --version
   man loglog

4. Start using LogLog:
   echo "- My first note" > notes.log
   loglog show notes.log
   loglog convert notes.log --to html
EOF

echo -e "\n${GREEN}For distribution:${NC}"
echo "• Upload to GitHub releases for direct download"
echo "• Submit to Launchpad PPA for easier installation" 
echo "• Request inclusion in official Ubuntu repositories"
echo "• See docs/PACKAGING.md for detailed submission process"

echo -e "\n${BLUE}╔══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                Demo Complete!                ║${NC}"
echo -e "${BLUE}║                                              ║${NC}"
echo -e "${BLUE}║  LogLog is ready for distribution as a      ║${NC}"
echo -e "${BLUE}║  professional .deb package for Ubuntu!      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════╝${NC}"

if [ $SIMULATE -eq 0 ] && [ -f loglog_1.0.0-1_all.deb ]; then
    echo -e "\n${GREEN}Package ready: $(ls -la loglog_1.0.0-1_all.deb | awk '{print $9, $5}') bytes${NC}"
fi

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Test on multiple Ubuntu versions"
echo "2. Set up automated CI/CD builds" 
echo "3. Create Launchpad PPA"
echo "4. Submit to Ubuntu repositories"
echo "5. Monitor adoption and gather feedback"