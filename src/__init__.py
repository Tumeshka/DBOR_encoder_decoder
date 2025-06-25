"""
DBOR Conformance Level 2 Implementation

This package provides a complete implementation of DBOR (Data Binary Object Representation)
encoder and decoder for conformance level 2 as specified in the DBOR 1.0.0 specification.

Main modules:
- encoder: DBOR encoding functionality
- decoder: DBOR decoding functionality  
- values: DBOR value type definitions
- test_cases: Comprehensive test case generators

Example usage:
    from src.encoder import encode
    from src.decoder import decode
    
    # Round-trip example
    value = [None, 42, "hello", b"world"]
    encoded = encode(value)
    decoded = decode(encoded)
    assert decoded == value
"""

from .encoder import encode
from .decoder import decode, DBORDecodeError
from .values import (
    NoneValue, IntegerValue, ByteStringValue, 
    Utf8StringValue, SequenceValue, from_python, to_python
)

__version__ = "1.0.0"
__author__ = "DBOR Conformance Test Suite"
__description__ = "DBOR encoder/decoder for conformance level 2"

__all__ = [
    'encode',
    'decode', 
    'DBORDecodeError',
    'NoneValue',
    'IntegerValue', 
    'ByteStringValue',
    'Utf8StringValue',
    'SequenceValue',
    'from_python',
    'to_python'
]
