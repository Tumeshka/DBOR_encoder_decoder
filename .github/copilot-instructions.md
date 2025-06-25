<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# DBOR Conformance Level 2 Project Instructions

This project implements and tests DBOR (Data Binary Object Representation) encoder/decoder pairs for conformance level 2 as specified in the DBOR 1.0.0 specification.

## Project Context

- **Objective**: Verify round-trip integrity (`decode(encode(input)) == input`) for all valid level-2 DBOR values
- **Conformance Level**: Level 2 supports NoneValue, IntegerValue, ByteStringValue, Utf8StringValue, and SequenceValue
- **Language**: Python 3.7+
- **Dependencies**: None (uses only Python standard library)

## Code Style Guidelines

- Follow PEP 8 style conventions
- Use type hints where appropriate
- Write comprehensive docstrings for all functions and classes
- Include error handling for invalid inputs
- Maintain backwards compatibility with existing test cases

## Key Implementation Details

### Encoder (`src/encoder.py`)
- Uses `integer_token(h, v)` for encoding header/value pairs
- Header values: 0=positive int, 1=negative int, 2=bytes, 3=UTF-8, 4=sequence
- Values 0-23 encode directly, 24+ use extended encoding
- Maximum integer range: −2⁶³ to 2⁶⁴−1

### Decoder (`src/decoder.py`)
- Recursive descent parser
- Handles all conformance level 2 types
- Comprehensive error reporting via `DBORDecodeError`
- Validates UTF-8 encoding and data integrity

### Testing Strategy
- Round-trip testing is the primary validation method
- Test categories: primitives, sequences, edge cases, random cases
- Use `unittest` framework with comprehensive assertions
- Include JSON test data files for additional test vectors

## Common Patterns

### Round-Trip Testing
```python
def assert_round_trip(self, value):
    encoded = encode(value)
    decoded = decode(encoded)
    self.assertEqual(decoded, value)
```

### Error Handling
```python
try:
    result = encode(value)
except (TypeError, OverflowError, ValueError) as e:
    # Handle encoding errors appropriately
    pass
```

### Test Case Organization
- Use `subTest()` for parameterized testing
- Group related test cases by functionality
- Include both positive and negative test cases

## Debugging Tips

- Use `.hex()` method to inspect encoded byte sequences
- Check header bits: `(byte >> 5) & 0x7` for type, `byte & 0x1F` for payload
- Validate integer bounds before encoding
- Ensure UTF-8 strings are properly encoded/decoded

## Performance Considerations

- Avoid unnecessary object creation in tight loops
- Use bytes operations efficiently
- Consider memory usage for large sequences
- Profile encoding/decoding performance for optimization

## Extension Points

- Value type validation in `src/values.py`
- Test case generation in `src/test_cases.py`
- Canonical encoding utilities in `tools/canonical.py`
- Additional test data in `tests/*.json` files

When writing code for this project, prioritize correctness, maintainability, and comprehensive testing over performance optimization.
