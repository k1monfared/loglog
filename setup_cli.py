#!/usr/bin/env python3
"""
Setup script for LogLog CLI

Creates a symlink or script to make the CLI accessible system-wide.
"""

import os
import sys
import stat
import shutil
from pathlib import Path

def create_symlink_setup():
    """Create symlink in user's local bin directory"""
    script_path = Path(__file__).parent / 'loglog_cli.py'
    local_bin = Path.home() / '.local' / 'bin'
    
    # Create local bin directory if it doesn't exist
    local_bin.mkdir(parents=True, exist_ok=True)
    
    symlink_path = local_bin / 'loglog'
    
    # Remove existing symlink if it exists
    if symlink_path.exists():
        symlink_path.unlink()
    
    # Create symlink
    os.symlink(script_path.absolute(), symlink_path)
    
    print(f"✓ Created symlink: {symlink_path} -> {script_path}")
    print(f"✓ Make sure {local_bin} is in your PATH")
    print("✓ You can now use 'loglog' command from anywhere")
    
    # Check if local bin is in PATH
    path_env = os.environ.get('PATH', '')
    if str(local_bin) not in path_env:
        print(f"\nTo add {local_bin} to PATH, add this to your ~/.bashrc or ~/.zshrc:")
        print(f'export PATH="$PATH:{local_bin}"')

def create_wrapper_script():
    """Create a wrapper script that calls the Python CLI"""
    script_path = Path(__file__).parent / 'loglog_cli.py'
    local_bin = Path.home() / '.local' / 'bin'
    
    # Create local bin directory if it doesn't exist
    local_bin.mkdir(parents=True, exist_ok=True)
    
    wrapper_path = local_bin / 'loglog'
    
    # Create wrapper script
    wrapper_content = f'''#!/bin/bash
python3 "{script_path.absolute()}" "$@"
'''
    
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    
    # Make executable
    wrapper_path.chmod(wrapper_path.stat().st_mode | stat.S_IEXEC)
    
    print(f"✓ Created wrapper script: {wrapper_path}")
    print(f"✓ Make sure {local_bin} is in your PATH") 
    print("✓ You can now use 'loglog' command from anywhere")

def main():
    print("LogLog CLI Setup")
    print("================")
    
    # Check if python3 is available
    if not shutil.which('python3'):
        print("❌ Python 3 not found. Please install Python 3.")
        return 1
    
    # Check if loglog_cli.py exists
    cli_script = Path(__file__).parent / 'loglog_cli.py'
    if not cli_script.exists():
        print(f"❌ CLI script not found: {cli_script}")
        return 1
    
    print(f"✓ Found CLI script: {cli_script}")
    
    # Try symlink first, fall back to wrapper script
    try:
        create_symlink_setup()
    except OSError:
        print("❌ Symlink creation failed, trying wrapper script...")
        create_wrapper_script()
    
    print("\n🎉 Setup complete! Try running:")
    print("   loglog --help")
    print("   loglog show demo/lorem_ipsum.log")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())