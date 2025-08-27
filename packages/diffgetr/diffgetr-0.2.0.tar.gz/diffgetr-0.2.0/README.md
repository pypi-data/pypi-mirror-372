# diffgetr

A Python library for comparing nested data structures with detailed diff reporting and interactive navigation.

## Features

- Compare deeply nested dictionaries and lists with customizable precision
- **Side-by-side tabular comparison** with percentage changes for numeric values
- Summarize differences with key frequency counts and pattern recognition  
- Navigate interactively through diff results using dictionary-like syntax
- Support for array indexing and complex nested paths
- Multiple output formats: summary, detailed, and tabular side-by-side
- UUID and CSV pattern recognition for cleaner diff summaries
- Configurable DeepDiff parameters for fine-tuned comparisons
- Option to ignore added items for focused change analysis
- Command-line tool for JSON file comparison with path navigation

## Installation

```bash
pip install .
```

## Usage

### As a Library

#### Basic Usage

```python
from diffgetr.diff_get import diff_get

# Basic comparison
diff = diff_get(obj1, obj2)
print(diff)  # Prints a summary of differences

# Navigate to specific parts
sub_diff = diff['key1']['nested_key']
print(sub_diff)
```

#### Advanced Configuration

```python
# Custom DeepDiff parameters
diff = diff_get(
    obj1, obj2,
    deep_diff_kw={'significant_digits': 5, 'ignore_string_case': True},
    ignore_added=True  # Focus only on changes and removals
)

# Different output formats
diff.diff_summary()        # Print summary to stdout
diff.diff_all(indent=4)    # Print full diff details
diff.diff_sidebyside()     # Tabular side-by-side comparison with % changes
raw_diff = diff.diff_obj   # Access underlying DeepDiff object
```

#### Interactive Navigation

```python
# Navigate through nested structures
diff = diff_get(data1, data2)

# Use tab completion to see available keys
dir(diff)  # Shows common keys between both datasets

# Navigate with array indices
item_diff = diff['items'][0]['properties']

# Check current location
print(diff.location)  # Shows path like 'root.items[0].properties'
```

#### Path Pattern Matching

```python
# Find all diffs matching a wildcard pattern
for df in diff.path_diffs('root.models.*.windows.-1.model.calculations'):
    print('#'*80)
    print(df.path)
    print(df.diff_sidebyside())
```

This allows you to:
- Use `*` wildcards to match any key name, and easily check parts of complex json package

### Command Line

```bash
diffgetr file1.json file2.json path.to.key
```

**Parameters:**
- `file1.json`, `file2.json`: JSON files to compare
- `path.to.key`: Dot-separated path to navigate in the structure

**Path Examples:**
- `users.0.profile` - Navigate to first user's profile
- `data.items[5].name` - Navigate to name of 6th item
- `config.database` - Navigate to database configuration

## API Reference

### Constructor Parameters

```python
diff_get(s0, s1, loc=None, path=None, deep_diff_kw=None, ignore_added=False)
```

**Parameters:**
- `s0`, `s1`: Objects to compare
- `loc`: Internal location tracking (used recursively)
- `path`: Path component to append to location
- `deep_diff_kw`: Dictionary of parameters passed to DeepDiff (default: `{'ignore_numeric_type_changes': True, 'significant_digits': 3}`)
- `ignore_added`: If True, ignore items that were added in s1 but not in s0

### Methods

#### `diff_summary(file=None, top=50, bytes=None)`
Generate a summary of differences with pattern recognition and frequency counts.

**Parameters:**
- `file`: Output file object (default: stdout)
- `top`: Maximum number of diff patterns to show per category
- `bytes`: Whether to write bytes (auto-detected if None)

#### `diff_all(indent=2, file=None)`
Print complete diff details with full data structures.

**Parameters:**
- `indent`: Indentation level for pretty printing
- `file`: Output file object (default: stdout)

#### `diff_sidebyside()`
Display differences in a tabular side-by-side format with percentage changes for numeric values.

**Features:**
- Flattens nested structures into dot-notation keys
- **Groups missing/added keys by parent** for compact display
- Groups differences by common parent keys
- Shows percentage differences for numeric values
- Filters changes based on significant digits threshold
- Displays missing keys as `<MISSING>`
- Sorts by frequency of changes within each group

### Properties

- `location`: Current path in dot notation (e.g., 'root.data.items[0]')
- `diff_obj`: Underlying DeepDiff object for advanced operations

### Pattern Recognition

The tool automatically recognizes and abstracts common patterns:
- **UUIDs**: Replaced with `<UUID>` for cleaner summaries
- **CSV-like numbers**: Numeric sequences replaced with `<CSV>`
- **Path normalization**: Consistent path formatting across different access patterns

## Error Handling

When navigating to non-existent keys, the tool will:
1. Display a diff summary showing available keys
2. Raise a KeyError with location information
3. Continue execution for batch operations

## Examples

### Comparing Configuration Files

```python
import json
from diffgetr.diff_get import diff_get

with open('config_v1.json') as f1, open('config_v2.json') as f2:
    config1 = json.load(f1)
    config2 = json.load(f2)

diff = diff_get(config1, config2, ignore_added=True)
print(f"Changes found at: {diff.location}")
diff.diff_summary(top=20)
```

### Analyzing API Response Changes

```python
# Compare two API responses with high precision
diff = diff_get(
    response1, response2,
    deep_diff_kw={'significant_digits': 6, 'ignore_order': True}
)

# Navigate to specific sections
user_diff = diff['users'][0]['profile']
if user_diff:
    user_diff.diff_all()
```

### Side-by-Side Comparison

```python
# For detailed tabular comparison with percentage changes
diff = diff_get(financial_data_old, financial_data_new)
diff.diff_sidebyside()

# Output example:
# KEY                                                          | s0                           | s1                           | % DIFF    
# -------------------------------------------------------------------------------------------------------------
# 
# GROUP: root.quarterly_results
# - .q1.revenue                    | 1250000.0                    | 1340000.0                    |     7.200%
# - .q1.expenses                   | 980000.0                     | 1020000.0                    |     4.082%
# - .q2.revenue                    | 1180000.0                    | 1290000.0                    |     9.322%
# 
# GROUP: root.metadata
# - .last_updated                  | "2024-12-01"                 | "2025-01-15"                 
# - .version                       | "1.2.3"                      | "1.3.0"
```

## Testing

Run the comprehensive test suite to verify functionality:

```bash
python -m unittest discover tests -v
```

The test suite covers:
• Core diff functionality and navigation through nested structures
• Multiple output formats (summary, detailed, side-by-side)
• Pattern recognition for UUIDs and CSV-like data
• Error handling and edge cases
• IPython integration and tab completion
• Command-line interface functionality

## Contributing

This tool is part of the SMART_X project ecosystem. When contributing:

1. Maintain backward compatibility with existing APIs
2. Add tests for new pattern recognition features
3. Update documentation for any new navigation capabilities
4. Consider performance impact for large nested structures

## Version History

- **0.1.0**: Initial release with basic diff comparison
- **Current**: Enhanced with interactive navigation, pattern recognition, and configurable output formats

## License

MIT
