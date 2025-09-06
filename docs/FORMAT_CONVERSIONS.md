# LogLog Format Conversions

## Markdown Conversion

The `to_md()` method converts the tree structure to Markdown format using a shallowest leaf depth algorithm.

### Algorithm Logic

1. **Find the shallowest leaf node**: Scan the entire tree to find the leaf node (node without children) that has the smallest depth
2. **Determine header cutoff**: Use `min(shallowest_leaf_depth, header_levels + 1)` as the cutoff
3. **Apply formatting**:
   - Levels 1 to (cutoff - 1): Become headers H1, H2, H3, H4, etc.
   - Levels from cutoff onwards: Become list items with appropriate nesting

### Test Cases

#### Test Case 1: Mixed Depths (shallowest leaf depth = 2)
**Input structure:**
- A.3, C.1, F.1, F.2 are leaf nodes at depth 2 (shallowest leaves)
- Other leaf nodes go deeper (A.1.1.1, D.1.1.1.1, etc.)

**Output:** Level 1 becomes H1, level 2+ become lists:
```markdown
# A
- A.1
  - A.1.1
    - A.1.1.1
    - A.1.1.2
- A.3

# F
- F.1
- F.2
```

#### Test Case 2: Shallow Structure (shallowest leaf depth = 1)
**Input structure:**
```
Project A                    # Level 1 → list (shallowest leaf)
Project B                    # Level 1 → list
    Task B1                  # Level 2 → nested list
```

**Output:** No headers (since 1-1=0), everything becomes lists:
```markdown
- Project A
- Project B
  - Task B1
- Project C
  - Task C1
    - Subtask C1.1
    - Subtask C1.2
```

#### Test Case 3: Deep Structure (shallowest leaf depth = 5)
**Input structure:**
```
Alpha                        # Level 1 → H1
    Beta                     # Level 2 → H2  
        Gamma                # Level 3 → H3
            Delta            # Level 4 → H4
                Epsilon      # Level 5 → list (shallowest leaf)
```

**Output:** Levels 1-4 become H1-H4, level 5+ become lists:
```markdown
# Alpha
## Beta
### Gamma
#### Delta
- Epsilon
  - Zeta
    - Eta
      - Theta
```

#### Test Case 4: TODO Items (shallowest leaf depth = 1)
**Input structure:**
```
[x] Completed Project       # Level 1 → list (shallowest leaf)
    [x] Task 1 done          # Level 2 → nested list
        [] Subtask 1.1       # Level 3 → deeper nested list
[] Simple task               # Level 1 → list (shallowest leaf)
```

**Output:** No headers, all TODO items become lists:
```markdown
- [x] Completed Project
  - [x] Task 1 done
    - [ ] Subtask 1.1
    - [x] Subtask 1.2
  - [ ] Task 2 pending

- [ ] New Project
  - [ ] Setup phase
    - [ ] Requirements gathering
      - [ ] Stakeholder interviews
      - [ ] Technical specs

- [ ] Simple task
```

### Edge Cases

#### Completely Flat Structure (shallowest leaf depth = 1)
When all items are at the same top level with no nesting:
```
Item A    # Level 1 → list (shallowest leaf)
Item B    # Level 1 → list  
Item C    # Level 1 → list
```
**Output:** No headers (1-1=0), everything becomes lists:
```markdown
- Item A
- Item B  
- Item C
- Item D
- Item E
```

### Parameters

- `header_levels=4` (default): Maximum number of header levels (H1-H4). Beyond this, items become lists
- The algorithm automatically adapts based on the shallowest leaf depth in your content

## Reverse Conversion: Markdown to Loglog

The `from_md()` function converts Markdown back to the loglog format.

### Conversion Rules

1. **Headers → Items with `-`**:
   - `# Header` → `- Header` (no indentation)
   - `## Header` → `    - Header` (4 spaces + `-`)
   - `### Header` → `        - Header` (8 spaces + `-`)
   - Each header level adds 4 spaces of indentation

2. **Regular List Items → Items with `-`**:
   - `- item` → `    - item` (at appropriate indentation based on context)
   - `  - nested item` → `        - nested item` (preserves nesting with 4-space increments)

3. **TODO List Items → Items without `-`** (special case):
   - `- [ ] task` → `    [] task` (checkbox syntax, no `-` prefix)
   - `- [x] task` → `    [x] task`
   - `- [?] task` → `    [?] task`

4. **Paragraphs → Separate Items with `-`**:
   - Each paragraph (separated by blank lines) becomes its own `- paragraph text`
   - Paragraphs are placed at the current indentation level

### Example Conversion

**Markdown input:**
```markdown
# Project A

This is the first paragraph about Project A.

This is a second paragraph with more details.

- Task 1
  - Subtask 1.1
- [ ] Task 2 pending
- [x] Task 3 done

# Project B  
- Task B1
```

**Loglog output:**
```
- Project A
    - This is the first paragraph about Project A.
    - This is a second paragraph with more details.
    - Task 1
        - Subtask 1.1
    [] Task 2 pending
    [x] Task 3 done
- Project B
    - Task B1
```

### Key Features

- **All items use `-` prefix** except TODO items which use checkbox syntax directly
- **4-space indentation** for each nesting level
- **Paragraph preservation** - each paragraph becomes a separate list item
- **TODO syntax preservation** - maintains `[]`, `[x]`, `[?]` formatting
- **Hierarchical structure** maintained through consistent indentation

## Interactive HTML Conversion

The `to_html()` method converts the tree structure to an interactive HTML document with foldable sections.

### Features

1. **Foldable Tree Structure**: Every item with children gets a clickable triangle
2. **Click to Fold/Unfold**: Click triangles (▶/▼) to show/hide child sections
3. **Keyboard Shortcuts**: 
   - `Ctrl+1` through `Ctrl+9` - Fold everything to that level
   - `Ctrl+0` - Unfold everything completely
4. **TODO Item Styling**: 
   - ☐ Pending items (red text)
   - ☑ Completed items (strikethrough, gray text)
   - ☒ Unknown status items (red text)
5. **Clean Design**: Minimal styling, monospace font, no external dependencies

### Usage

```python
from loglog import build_tree_from_file

# Load your loglog file
root = build_tree_from_file('my_notes.txt')

# Generate interactive HTML
html_content = root.to_html('My Notes - Interactive View')

# Save to file
with open('my_notes.html', 'w') as f:
    f.write(html_content)
```

### Interactive Controls

#### Mouse Controls
- **Click triangles**: Fold/unfold specific sections
- **Keyboard focus**: Items are navigated and controlled entirely via keyboard
- **Auto-scroll**: Focused items automatically scroll into view

#### Keyboard Shortcuts

**Navigation**:
- `Up/Down` arrows - Navigate between **visible** items only (respects folding)
- `Right` arrow - Hierarchical navigation: unfolds current item and moves to first child, or moves to next item if no children
- `Left` arrow - Always folds current item, or moves to parent if already folded
- `Enter/Spacebar` - Toggle fold/unfold current item

**Global Folding**:
- `Ctrl+1` through `Ctrl+9` - Fold everything to that level
- `Ctrl+0` - Unfold everything completely

**Focus Mode**:
- `Ctrl+Alt+1` through `Ctrl+Alt+9` - Fold everything to that level, **except** the currently focused branch
- Perfect for examining one branch while hiding distracting content at other branches

#### Example Focus Mode Usage:
1. Navigate to "Project A > Task 1 > Subtask 1.1" using arrow keys
2. Press `Ctrl+Alt+2` 
3. **Result**: Everything else folds to level 2, but the entire "Project A" branch stays expanded so you can see your current item
4. Press `Ctrl+0` to return to fully expanded view

#### Navigation Flow Examples:
- **Right arrow traversal**: Repeatedly pressing `→` will traverse ALL items depth-first (unfolds as needed)
- **Down arrow navigation**: Pressing `↓` only moves to the next **visible** item (respects current folding state) 
- **Left arrow control**: Always folds the current item, or moves to parent if already folded

#### Visual Feedback & Themes
- **Smooth animations** for folding/unfolding
- **Smart branch highlighting** shows current mouse path in blue (cyan/blue highlight)
- **Position indicator** in bottom-left shows current mouse level and item
- **Dark/Light theme toggle** - Click 🌙/☀️ button to switch themes with smooth transitions
- **Hideable help** - Click the help box to collapse to a small "?" button
- **Enhanced color scheme**: 
  - Light mode: Clean white background with blue focus highlights
  - Dark mode: Rich dark theme with enhanced contrast and blue highlights
  - TODO items: Red for pending, gray for completed with improved visibility

#### Controls Layout
- **Top-right corner**: Theme toggle button (🌙 Dark / ☀️ Light) and collapsible help
- **Bottom-left corner**: Mouse position indicator
- **Theme persistence**: Your theme preference is saved and restored automatically

### Generated Files

The HTML files are completely self-contained with embedded CSS and JavaScript - no external dependencies needed. Perfect for sharing hierarchical notes that others can explore interactively.