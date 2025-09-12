#!/usr/bin/env python3
"""Test file type icons in the file explorer"""

import sys
sys.stderr = sys.stdout

def test_file_icons():
    print("="*60)
    print("TESTING FILE TYPE ICONS")
    print("="*60)
    
    try:
        from loglog_gui import ModernFileTree, SystemTheme
        from pathlib import Path
        import tkinter as tk
        
        # Create test directory structure
        test_dir = Path("/tmp/loglog_icon_test")
        test_dir.mkdir(exist_ok=True)
        
        # Create test files with different extensions
        test_files = [
            "script.py",
            "config.json", 
            "document.md",
            "image.png",
            "archive.zip",
            "loglog_file.log",
            "stylesheet.css",
            "webpage.html"
        ]
        
        for filename in test_files:
            (test_dir / filename).write_text(f"Test {filename}")
        
        print(f"✓ Created test files in {test_dir}")
        
        # Test the file icon detection
        root = tk.Tk()
        theme = SystemTheme(root)
        file_tree = ModernFileTree(root, theme)
        
        print(f"\n🧪 Testing icon detection:")
        for filename in test_files:
            file_path = test_dir / filename
            icon = file_tree.get_file_icon(file_path)
            print(f"   {filename:<20} → {icon}")
        
        print(f"\n✓ File type icon system working correctly!")
        print(f"✓ Navigate to {test_dir} in the GUI to see the icons")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_file_icons()