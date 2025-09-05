# Unit Tests for Loglog

This directory contains comprehensive unit tests for the loglog conversion functions.

## Test Structure

### `test_roundtrip.py`
Tests round-trip conversions to ensure data integrity:

1. **TXT → MD → TXT** round-trip tests:
   - Load original `.txt` loglog files
   - Convert to markdown using `tree.to_md()`
   - Convert back to loglog using `from_md()`
   - Compare normalized versions (accounts for formatting differences)
   - **Expected result**: Very high similarity (>90%) after normalization

2. **MD → TXT → MD** round-trip tests:
   - Load original `.md` markdown files (our test outputs)
   - Convert to loglog using `from_md()` 
   - Convert back to markdown using tree structure
   - Compare structural similarity (focuses on headers and lists)
   - **Expected result**: Perfect structural match (100%)

### Test Files Used
All tests use the existing test files from `tests/`:
- `test_input.txt` - Mixed depth structure (shallowest leaf depth = 2)
- `test_input_shallow.txt` - Simple structure (shallowest leaf depth = 1)  
- `test_input_deep.txt` - Deep hierarchy (shallowest leaf depth = 5)
- `test_input_todos.txt` - TODO items (shallowest leaf depth = 1)
- `test_input_flat.txt` - Flat structure (shallowest leaf depth = 1)
- Corresponding `*_output.md` files

## Normalization Strategy

### For TXT → MD → TXT tests:
- **TODO format normalization**: `[]` → `[ ]` (adds space)
- **Dash prefix addition**: Adds `- ` prefix to non-TODO items for comparison
- **Whitespace normalization**: Removes trailing whitespace and empty lines

### For MD → TXT → MD tests:
- **Structural comparison**: Focuses on headers (H1, H2, etc.) and list hierarchy
- **Content preservation**: Verifies that text content is maintained
- **Format flexibility**: Allows for minor formatting differences

## Running Tests

### Run All Tests
```bash
cd tests/unit
python test_runner.py
```

### Run Specific Test
```bash
cd tests/unit  
python test_roundtrip.py
```

### Run with Python unittest
```bash
cd tests/unit
python -m unittest test_roundtrip.py -v
```

## What The Tests Verify

1. **Data Integrity**: Content is preserved through conversions
2. **Structure Preservation**: Hierarchical relationships are maintained
3. **Format Handling**: Both loglog and markdown formats are handled correctly
4. **TODO Syntax**: Checkbox syntax is properly converted both ways
5. **Edge Cases**: Flat structures, deep nesting, and mixed content work correctly

## Expected Behaviors

### Perfect Matches (100%)
- **MD → TXT → MD**: Should have perfect structural similarity
- **TXT → MD → TXT** (after normalization): Should have perfect content match

### Acceptable Differences
- **Dash prefixes**: Original loglog format vs. `from_md()` output format
- **TODO spacing**: `[]` vs. `[ ]` formatting
- **Whitespace**: Minor spacing differences in markdown formatting

## Debug Output
When tests fail, debug files are saved to `tests/debug/`:
- `*_original.*` - Original input
- `*_roundtrip.*` - Final converted output  
- `*_intermediate.*` - Intermediate conversion step

This helps identify exactly where conversions may be losing fidelity.