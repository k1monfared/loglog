#!/usr/bin/env python3
"""Test native Text widget replacement for scrolling"""

import sys
sys.stderr = sys.stdout

def test_native_replacement():
    print("="*60)
    print("TESTING NATIVE TEXT WIDGET SCROLLING REPLACEMENT")
    print("="*60)
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        root = tk.Tk()
        root.title("Native Scrolling Replacement Test")
        root.geometry("1000x700")
        
        # Create main layout like LogLog
        main_paned = ttk.PanedWindow(root, orient='horizontal')
        main_paned.pack(fill='both', expand=True)
        
        # Left panel - file tree (simplified)
        left_frame = tk.Frame(main_paned, bg='lightgray', width=200)
        left_label = tk.Label(left_frame, text="File Tree\\n(TreeView would be here)", bg='lightgray')
        left_label.pack(pady=50)
        main_paned.add(left_frame)
        
        # Right panel - NATIVE TEXT WIDGET with scrolling
        right_frame = tk.Frame(main_paned)
        
        # Create Text widget with native scrollbar 
        text_widget = tk.Text(right_frame, wrap=tk.NONE, font=('Courier', 10))
        scrollbar = tk.Scrollbar(right_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack text and scrollbar
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        main_paned.add(right_frame)
        
        # Add tree-like content to Text widget
        lines = []
        lines.append("Native Text Widget Test Document")
        for i in range(1, 51):
            lines.append(f"    Line {i} - This is content line {i}")
            if i % 10 == 0:
                lines.append(f"        Nested content under line {i}")
                lines.append(f"        More nested content {i}B")
                lines.append(f"        Even more nested content {i}C")
        
        content = "\\n".join(lines)
        text_widget.insert('1.0', content)
        
        # Make text read-only (like a viewer)
        text_widget.configure(state='disabled')
        
        print("✅ Native Text widget created with content")
        print("🖱️ Mouse wheel should work automatically")
        print("⌨️ Keyboard scrolling should work automatically") 
        print("📜 Scrollbar should work automatically")
        print()
        print("🔄 Compare this scrolling behavior to LogLog:")
        print("   • Mouse wheel over text area")
        print("   • Page Up/Down keys")
        print("   • Arrow keys")
        print("   • Scrollbar dragging")
        print("   • All should work smoothly without custom handlers")
        
        root.mainloop()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_native_replacement()