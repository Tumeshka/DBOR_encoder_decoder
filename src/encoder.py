"""
DBOR Encoder Implementation for Conformance Level 2

This module implements the DBOR encoder for conformance level 2 as specified
in the DBOR 1.0.0 specification. It supports:
- NoneValue
- IntegerValue (v ∈ {−2⁶³ … 2⁶⁴−1})
- ByteStringValue
- Utf8StringValue  
- SequenceValue (nested sequences of supported types)
"""


def integer_token(h, v):
    """
    Generate an integer token with header h and value v.
    
    Args:
        h: Header value (0-4 for different DBOR types)
        v: Non-negative integer value to encode
        
    Returns:
        bytes: Encoded integer token
        
    Raises:
        ValueError: If the value is too large to encode (> 8 bytes)
    """
    b = h << 5
    if v <= 23:
        return bytes([b | v])

    s = b''
    v -= 23
    while v > 0:
        v -= 1
        s += bytes([v % 256])
        v = v // 256
        if len(s) > 8:
            raise ValueError('Value too large to encode')

    return bytes([b | (23 + len(s))]) + s


def encode(value):
    """
    Encode a Python value to DBOR format.
    
    Supports conformance level 2 types:
    - None -> NoneValue
    - int -> IntegerValue (within supported range)
    - bytes -> ByteStringValue
    - str -> Utf8StringValue
    - list/tuple -> SequenceValue
    
    Args:
        value: Python value to encode
        
    Returns:
        bytes: DBOR-encoded representation
        
    Raises:
        TypeError: If the value type is not supported
        OverflowError: If integer is outside supported range
        ValueError: If encoding fails
    """
    if value is None:
        return b'\xFF'
    
    if isinstance(value, int):
        # Check integer bounds for conformance level 2
        if value < -(2**63) or value >= 2**64:
            raise OverflowError(f'Integer {value} is outside supported range [−2⁶³, 2⁶⁴−1]')
        
        if value >= 0:
            return integer_token(0, value)
        else:
            return integer_token(1, -value - 1)
    
    if isinstance(value, bytes):
        return integer_token(2, len(value)) + value
    
    if isinstance(value, str):
        utf8_bytes = value.encode('utf-8')
        return integer_token(3, len(utf8_bytes)) + utf8_bytes
    
    if isinstance(value, (list, tuple)):
        # Encode all elements and concatenate
        encoded_elements = b''.join(encode(element) for element in value)
        return integer_token(4, len(encoded_elements)) + encoded_elements
    
    raise TypeError(f'Unsupported type: {type(value).__name__}')


# Alias for backwards compatibility
encoded = encode
