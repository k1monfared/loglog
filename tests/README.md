# Test Cases for Markdown Conversion

This directory contains comprehensive test cases for the `to_md()` method in loglog.

## Test Files

### Input Files
- `test_input.txt` - Mixed depth structure with various nesting levels
- `test_input_shallow.txt` - Simple project structure with minimal nesting  
- `test_input_deep.txt` - Deep hierarchy testing header level limits
- `test_input_todos.txt` - TODO items with checkboxes and different statuses
- `test_input_flat.txt` - Completely flat structure (no nesting)

### Expected Output Files  
- `test_input_output.md` - Expected markdown for mixed depth (shallowest leaf depth = 2)
- `test_input_shallow_output.md` - Expected markdown for shallow structure (shallowest leaf depth = 1)
- `test_input_deep_output.md` - Expected markdown for deep structure (shallowest leaf depth = 5)
- `test_input_todos_output.md` - Expected markdown for TODO items (shallowest leaf depth = 1)
- `test_input_flat_output.md` - Expected markdown for flat structure (shallowest leaf depth = 1)

## Running Tests

### Run All Tests
```bash
cd tests
python run_tests.py
```

This compares current output with expected output and reports PASS/FAIL for each test case.

### Regenerate Expected Outputs
```bash
cd tests  
python run_tests.py generate
```

Use this when you've made changes to the algorithm and want to update the expected outputs.

## Test Coverage

The test cases cover:
- **Shallowest leaf depths**: 1, 2, 5 (testing different header cutoff scenarios)
- **Structure types**: flat, shallow, mixed, deep hierarchies
- **Content types**: regular text, TODO items with various statuses
- **Edge cases**: completely flat lists, deep nesting beyond header limits
- **Algorithm behavior**: header vs list assignment based on shallowest leaf depth

## Algorithm Verification

Each test verifies that:
1. Shallowest leaf depth is calculated correctly
2. Header cutoff = min(shallowest_leaf_depth, header_levels + 1) 
3. Levels 1 to (cutoff - 1) become headers H1, H2, H3, H4
4. Levels from cutoff onwards become properly nested lists
5. TODO syntax is preserved in both headers and lists