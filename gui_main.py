#!/usr/bin/env python3
"""
LogLog GUI - Main Entry Point
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui', 'src'))

from loglog_gui import ModernLogLogGUI
from loglog_tree_model import LogLogNode

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            app = ModernLogLogGUI()
            app.load_file(file_path)
            app.root.mainloop()
        else:
            print(f"File not found: {file_path}")
            sys.exit(1)
    else:
        app = ModernLogLogGUI()
        app.root.mainloop()

if __name__ == "__main__":
    main()