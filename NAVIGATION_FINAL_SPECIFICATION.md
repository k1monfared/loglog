# LogLog Final Navigation Specification

## 🎯 **Finalized Keyboard & Mouse System**

Based on consistency analysis and feedback, here's the refined navigation system:

### **Core Design Decisions**

1. ✅ **Space Key**: TODO cycling (more natural)
2. ✅ **Right Arrow**: Unfold current item, stay on it
3. ✅ **Selection**: Remove ghost highlighting complexity - use mouse Ctrl+Click for individual selection
4. ✅ **Edit Mode**: Ctrl+Enter to save, Escape to cancel

## ⌨️ **Keyboard Navigation (Final)**

### **Basic Movement**
```
↑ (Up): Move focus to previous item in visual order
↓ (Down): Move focus to next item in visual order
← (Left): Go to parent (fold current if unfolded)
→ (Right): Unfold current item (stay on same item)
```

### **Selection System**
```
Shift+↑/↓: Extend selection range up/down from anchor
Shift+←: Extend selection to parent hierarchy  
Shift+→: Extend selection to children hierarchy
Ctrl+A: Select all items at current level
```

**Note**: Individual item selection (non-contiguous) requires mouse Ctrl+Click

### **TODO Status Management**
```
Space: Cycle TODO status ([] → [-] → [x] → [])
?: Set TODO to unknown status [?] 
-: Set TODO to in-progress status [-]
```
**Scope**: All shortcuts apply to ALL selected items

### **Editing System**
```
Enter: Start editing focused item
Enter (while editing at end): Create new sibling item
Enter (while editing in middle): Break line, rest becomes new item
Backspace (at start while editing): Combine with previous item
Ctrl+Enter: Save changes and exit edit mode
Escape: Cancel changes and exit edit mode
Tab/Shift+Tab: Change indentation (works in edit mode and normal mode)
```

### **Folding System**
```
→: Unfold current item (stay on it)  
←: Fold current item (if unfolded) OR move to parent (if folded)
Shift+→: Unfold current AND move to first child
Ctrl+0: Unfold all items
Ctrl+1-9: Show only levels 1-9 (fold deeper)
Ctrl+Shift+A: Focus mode (fold everything except current branch)
```

### **Search System**
```
Ctrl+F: Open global search
Ctrl+Shift+F: Open scoped search (within selection)
F3: Next search result
Shift+F3: Previous search result  
Escape: Close search
```

## 🖱️ **Mouse Navigation (Parity System)**

### **Click Behaviors**
```
Single Click:
- Set focus to clicked item
- Clear any existing selection
- If in edit mode: position cursor

Ctrl+Click: 
- Toggle individual item selection (for non-contiguous selection)
- Maintain current focus
- Build up selection of scattered items

Shift+Click:
- Range select from last focused item to clicked item
- All items in range become selected
- Move focus to clicked item

Double Click:
- Start editing clicked item immediately
- Clear selection and focus on item
```

### **Triangle (Fold/Unfold) Interactions**
```
Triangle Click: Toggle fold state of item
Ctrl+Triangle Click: Toggle fold state recursively (item + all children)
Shift+Triangle Click: Fold/unfold all siblings at same level
```

### **Drag & Drop**
```
Drag Single Item:
- Move item to new location in hierarchy
- Show visual drop indicators
- Snap to valid drop zones (before/after items, as child)

Drag Multiple Selection:
- Move all selected items as a group
- Maintain relative hierarchy relationships
- Show multi-item drag feedback
```

### **Context Menu (Right Click)**
```
Item Context Menu:
├── Edit Text
├── TODO Status ►
│   ├── Pending []
│   ├── In Progress [-] 
│   ├── Complete [x]
│   └── Unknown [?]
├── ─────────────
├── Cut
├── Copy  
├── Paste
├── Delete
├── ─────────────
├── Move Up
├── Move Down
├── Indent →
├── Outdent ←
├── ─────────────
├── Fold/Unfold
├── Fold All Children
└── Focus Mode
```

## 🎨 **Visual Feedback System**

### **Focus & Selection States**
```
Focused Item: Blue border, subtle background highlight
Selected Items: Same blue background as focused (all look identical)
Multi-Selection: All selected items have same visual treatment
Edit Mode: Different border color, inline text cursor visible
```

### **TODO Status Visual Indicators**
```
[] Pending: Red checkbox/background
[-] In Progress: Orange checkbox/background
[x] Complete: Gray with strikethrough text
[?] Unknown: Yellow checkbox/background
```

### **Folding Visual Indicators**
```
▶ (Collapsed): Indicates item has hidden children
▼ (Expanded): Indicates item children are visible
Smooth animations: 200ms transitions for fold/unfold
Indentation: 25px per hierarchy level
```

### **Search Visual Feedback**
```
Search Matches: Yellow highlight background
Current Match: Orange highlight background
Auto-expand: Folded items with matches automatically unfold
Match Counter: "3 of 47 matches" in search box
```

## 🔄 **State Management Rules**

### **Focus Rules**
- Always exactly one focused item (or none)
- Focus moves with arrow keys
- Focus is part of selection (selected items always include focused)
- Ctrl+Click can change selection without moving focus

### **Selection Rules**  
- Can have multiple selected items
- Selected items always include the focused item
- Range selection (Shift+arrows) creates contiguous selection
- Individual selection (Ctrl+Click) creates non-contiguous selection
- All operations apply to ALL selected items

### **Edit Mode Rules**
- Only one item can be edited at a time
- Always edit the focused item
- Edit mode is modal - different keybindings active
- Clear visual indication of edit state
- Auto-save on focus change or file operations

### **Fold State Rules**
- Each item independently remembers fold state
- Folding parent automatically hides all descendants  
- Fold states persist across file save/load
- Search results auto-expand folded ancestors

## 🎯 **Workflow Examples**

### **TODO Management Workflow**
```
1. Navigate to TODO item (arrows)
2. Space to cycle status ([] → [-] → [x])
3. Or: - for in-progress, ? for unknown
4. Works on multiple selected items simultaneously
```

### **Bulk Selection Workflow**
```
1. Click first item
2. Shift+Click last item (range selection)
3. OR: Ctrl+Click individual scattered items
4. Apply operation (Space for TODO, Tab for indent, etc.)
```

### **Editing Workflow**
```
1. Navigate to item (arrows)
2. Enter to start editing
3. Type changes
4. Ctrl+Enter to save, or Escape to cancel
5. Enter at end creates new sibling item
```

### **Hierarchy Management Workflow**
```
1. Select items to move (click/shift+click)
2. Tab/Shift+Tab to change indentation
3. OR: Drag and drop to new location
4. Fold/unfold with → ← arrows
```

This finalized system removes complexity while maintaining power, follows standard UI conventions, and provides both keyboard and mouse workflows for all operations.