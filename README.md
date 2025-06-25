# DBOR Conformance Level 2 Test Suite

A comprehensive test suite to verify round-trip integrity of DBOR encoder/decoder pairs for conformance level 2, as defined in the DBOR 1.0.0 specification.

## 🎯 Objective

This project tests whether **`decode(encode(input)) == input`** for all valid level-2 DBOR values.

## ✅ Supported Types (Conformance Level 2)

From section 4.3 of the DBOR specification, conformance level 2 supports:

- **NoneValue**
- **IntegerValue(v)** for all v ∈ {−2⁶³ … 2⁶⁴−1}
- **ByteStringValue(<b₁,…,bₘ>)**
- **Utf8StringValue(<b₁,…,bₘ>)**
- **SequenceValue(v₁,…,vᵣ)** where each vᵢ is level-2 supported

⚠️ **Note**: `DictionaryValue`, `BinaryRationalValue`, and `DecimalRationalValue` are not included at this conformance level.

## 📁 Project Structure

```
dbor_conformance_lvl2/
├── src/
│   ├── encoder.py            # DBOR encoder implementation
│   ├── decoder.py            # DBOR decoder implementation
│   ├── values.py             # Definitions for DBOR types
│   └── test_cases.py         # Set of input vectors and generators
│
├── tests/
│   ├── test_roundtrip.py     # Main test file for round-trip tests
│   ├── data_primitive.json   # Valid primitives: int, None, byte/utf8 strings
│   ├── data_sequences.json   # Nested sequences of supported values
│   └── edge_cases.json       # Edge test cases (e.g., huge integers)
│
├── tools/
│   └── canonical.py          # Canonicalization helpers and analysis
│
├── README.md
└── requirements.txt
```

## 🧪 Test Categories

### 1. Primitive Round-Trip
Tests encoding and decoding of basic values:
- `None`, `0`, `-1`, `1`, `2⁶⁴−1`, `−2⁶³`
- Byte strings: `b"bytes"`, `b"\\x01\\x02"`
- UTF-8 strings: `"ascii"`, `"üñîçødë"`, `"🚀🌟💯"`

### 2. Sequence Construction
Tests nested sequences:
- `[]` (empty)
- `[None]` (single element)
- `[1, "A", b"\\x01\\x02"]` (mixed types)
- `[["nested", ["more"]], 123]` (deep nesting)

### 3. Edge Case Values
Stress tests with:
- Very large integers at boundaries: `±2⁶³`, `2⁶⁴−1`
- Maximum size byte strings and UTF-8 strings
- Empty sequences and strings
- Deep nesting scenarios

### 4. Random Testing
Generates random valid level-2 values for comprehensive testing.

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- No external dependencies required (uses only standard library)

### Installation
```bash
git clone <repository-url>
cd dbor_conformance_lvl2
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_roundtrip.py::TestRoundTrip::test_primitive_integers -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Or run directly
cd tests
python test_roundtrip.py
```

### Using the Encoder/Decoder
```python
from src.encoder import encode
from src.decoder import decode

# Basic usage
value = [None, 42, "hello", b"world", [1, 2, 3]]
encoded = encode(value)
decoded = decode(encoded)
assert decoded == value  # Should always be True for valid level-2 values

# Check encoding details
print(f"Original: {value}")
print(f"Encoded: {encoded.hex()}")
print(f"Decoded: {decoded}")
```

### Analyzing Encodings
```python
from tools.canonical import get_encoding_info, print_encoding_analysis
from src.test_cases import TestCaseGenerator

# Analyze a specific value
info = get_encoding_info([1, "hello", b"world"])
print(info)

# Analyze multiple values
test_cases = TestCaseGenerator.all_test_cases()
print_encoding_analysis(test_cases[:50])
```

## 📊 Test Coverage

The test suite includes:

- **Primitive Values**: 1000+ test cases covering all basic types
- **Sequence Values**: 500+ test cases with various nesting patterns  
- **Edge Cases**: 200+ boundary and stress test cases
- **Random Cases**: 100+ randomly generated valid values
- **JSON Data**: Additional test vectors from data files

### Integer Boundary Testing
- Direct encoding boundary (0-23)
- Extended encoding boundaries (24+)
- Signed/unsigned boundaries
- Maximum values for conformance level 2

### String Testing
- Empty strings
- ASCII text
- Unicode characters (Latin, Cyrillic, Japanese, Arabic, Emoji)
- Long strings
- Special characters and escape sequences

### Sequence Testing
- Empty sequences
- Single and multi-element sequences
- Nested sequences (up to 5 levels deep)
- Mixed-type sequences
- Large sequences (100+ elements)

## 🔧 Implementation Details

### Encoder (`src/encoder.py`)
- Implements the integer token encoding algorithm
- Supports all conformance level 2 types
- Validates integer bounds
- Handles UTF-8 encoding for strings

### Decoder (`src/decoder.py`)
- Recursive descent parser for DBOR data
- Comprehensive error handling
- Validates UTF-8 strings
- Checks data integrity

### Value Types (`src/values.py`)
- Type-safe wrappers for DBOR values
- Validation for conformance level 2 constraints
- Python object conversion utilities


## 📋 Requirements

See `requirements.txt` for dependencies (currently none - uses only Python standard library).


## 🏃‍♂️ Quick Start Example

```python
#!/usr/bin/env python3
"""Quick start example for DBOR conformance level 2 testing."""

from src.encoder import encode
from src.decoder import decode
from src.test_cases import TestCaseGenerator

def main():
    print("DBOR Conformance Level 2 - Quick Test")
    print("=" * 40)
    
    # Test some basic values
    test_values = [
        None,
        42,
        -123,
        "Hello, 世界! 🌍",
        b"\\x00\\x01\\xFF",
        [1, 2, [3, 4], "nested"]
    ]
    
    for value in test_values:
        try:
            encoded = encode(value)
            decoded = decode(encoded)
            success = decoded == value
            
            print(f"Value: {value!r}")
            print(f"  Encoded: {encoded.hex()}")
            print(f"  Round-trip: {'✅ PASS' if success else '❌ FAIL'}")
            print()
            
        except Exception as e:
            print(f"Value: {value!r}")
            print(f"  Error: {e}")
            print()

if __name__ == "__main__":
    main()
```

Save this as `quickstart.py` and run with `python quickstart.py` to see DBOR encoding in action!

## 📝 Interactive Testing with Jupyter Notebook

You can experiment with DBOR encoding and decoding interactively using the `interactive_dbor.ipynb` notebook included in the project. Open the notebook in Jupyter, and you'll find cells for encoding and decoding various values, visualizing byte representations, and running round-trip tests. The notebook also provides utilities to load test vectors, inspect results, and export your test outcomes to a CSV file for further analysis. After running your tests, simply use the provided code cell to save the results as a CSV, making it easy to review or share your findings.