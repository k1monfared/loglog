# loglog

A simple way of taking notes with absolute minimum structure. Everything is a list, even the list items are lists.

## Motivation
I log a lot of things in the following format:

```
- is a dolor sit amet, consectetur adipiscing elit. Vestibulum gravida porta dapibus.
    - delves into the euismod rhoncus elit, quis tempor nulla luctus.
        - offers a ultricies consectetur ipsum sit amet, condimentum aliquet mi.
            - Further magna sed, consequat ac nibh. Donec ut mauris eget.
    - discusses another vehicula velit ac, feugiat ultricies nisi.
        - explores tincidunt lobortis purus, nec efficitur elit vulputate.
        - analyzes the consequat ac, rhoncus nec eros. Nulla facilisi.
            - Examination of vestibulum ullamcorper dolor, vel vehicula dui ullamcorper.
- focuses on: a venenatis magna. Mauris fermentum, magna id mollis.
    - examines various cursus, posuere at semper ut, posuere in ipsum.
        - investigates a tempor justo, id ullamcorper magna finibus.
        - evaluates:
            - discusses lorem ipsum
            - Further gravida lectus, sed efficitur ligula venenatis vitae.
                - offers a ultricies consectetur:
                    - Further magna sed, consequat ac nibh. Donec ut mauris eget.
                    - analyzes the consequat ac, rhoncus nec eros. Nulla facilisi.
            - offers quam. Praesent sit amet velit nec diam.
    - presents: ipsum. Sed vitae ligula eget libero congue.
    - Additional vehicula justo, quis tristique metus aliquam eget.
        - discusses a lorem ipsum, non vehicula nisl lacinia.
    - Comparative consequat quam, et porttitor ipsum vehicula nec.
- offers a pellentesque aliquam:
    - explores a vestibulum condimentum nisi, in condimentum magna gravida.
        - investigates the luctus metus, vitae commodo nulla molestie.
            - In-depth fermentum eros, eget condimentum arcu commodo vitae.
            - evaluates the viverra lorem, sed tempor orci varius.
    - examines another tempor. Sed accumsan tellus eu nisl faucibus.
- addresses an nisi. Donec ultricies mauris eu justo fermentum.
    - discusses a lorem ipsum, non vehicula nisl lacinia.
        - analyzes the aliquet. Curabitur vel sagittis felis.
        - explores eleifend. Sed ac ipsum eget metus.
            - Examination of lorem ipsum, id tempus purus hendrerit.
- provides: a semper, eget consequat odio. Nam tristique nunc ac consequat.
    - delves into the suscipit semper, et sodales libero sollicitudin vitae.
        - offers quam. Praesent sit amet velit nec diam.
        - presents ipsum. Sed vitae ligula eget libero congue.
            - Additional vehicula justo, quis tristique metus aliquam eget.
        - Comparative consequat quam, et porttitor ipsum vehicula nec.
```

This has several benefits:
- Mainly it reduces the overhead of structure for when I'm taking notes. I don't need to think about whether this is a title, heading 1, section, subsection, list, etc. I can freely write down the flow of my thoughts.
- It also is very flexible. By simple indentation I can put a whole section under another item or move things around.
- If I'm using a text editor that folds text, I can easily fold/unfold sections at various levels.
- When a topic gets too big, or if I need a new document around a certain topic, I can just copy that part to a new file and adjust the indentation.
- It is highly portable, i.e. this is a raw text file that I can easily turn it into a markdown, or into other rich formatted texts.
- It is cross platform. Any platform can read/edit a text file.
- I can algorithmically manipulate/analyze it, which is the goal of this repo.

## Functionality
The python code is going to be able to read a text file like above and provide some functionality:

- [x] create a tree data structure that represents the structure of the text.
- [x] handle empty lines, empty items, items with different types:
    - `regular` items start with nothing, or with `-`.
    - `todo` items start with `[]` or `[x]` or `[?]` and have "done" status which is `True`, `False`, or `Null`.
        - I'm not quite sure about the syntaxing here. Maybe I can be a bit more flexible to allow compatibility, but then that adds more structure. I think keeping things simple is better.
- [ ] understand whether an item is a "title" or a "text", or maybe a combination of both. here are some examples:
    ```
        - example:
            - the above item is a title, and below it are a few items regarding it.
            - and this is just a text item, there is not much else you would expect to see
        - another example: but this is a combination, first there is a title of a few words, then a colon, then a longer sentence. There might still be some items below it or not
    ```
- [ ] prints the cleaned up version of the file to the text file.
    - [x] prints only a node and its children
    - [ ] prints the children to a certain depth
- [ ] convert
    - [x] to markdown
    - [x] from markdown
    - [x] to html (interactive)
    - [ ] to latex
        - [ ] to pdf
- [ ] find
    - [ ] a node by it's title
    - [ ] a node by information relevant to its sub-items
- [ ] summarize
    - [ ] all info of a node and its children
    - [ ] all info relevant to a topic frim all nodes related to it
- [ ] create a knowledge graph of topics, facts, etc

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
