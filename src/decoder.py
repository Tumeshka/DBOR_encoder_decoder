"""
DBOR Decoder Implementation for Conformance Level 2

This module implements the DBOR decoder for conformance level 2 as specified
in the DBOR 1.0.0 specification. It decodes DBOR-encoded data back to Python objects.
"""


class DBORDecodeError(Exception):
    """Exception raised when DBOR decoding fails."""
    pass


def decode_integer_token(data, pos):
    """
    Decode an integer token from DBOR data.
    
    Args:
        data: bytes object containing DBOR data
        pos: Current position in the data
        
    Returns:
        tuple: (decoded_value, new_position)
        
    Raises:
        DBORDecodeError: If decoding fails
    """
    if pos >= len(data):
        raise DBORDecodeError("Unexpected end of data")
    
    first_byte = data[pos]
    header = (first_byte >> 5) & 0x7
    payload = first_byte & 0x1F
    pos += 1
    
    if payload <= 23:
        return payload, pos
    
    # Extended length encoding
    length = payload - 23
    if length > 8:
        raise DBORDecodeError(f"Invalid length encoding: {length}")
    
    if pos + length > len(data):
        raise DBORDecodeError("Unexpected end of data in integer token")
    
    # Decode little-endian bytes
    value = 23
    for i in range(length):
        byte_val = data[pos + i]
        value += (byte_val + 1) * (256 ** i)
    
    return value, pos + length


def decode(data):
    """
    Decode DBOR data to Python objects.
    
    Args:
        data: bytes object containing DBOR-encoded data
        
    Returns:
        Decoded Python object
        
    Raises:
        DBORDecodeError: If decoding fails
        TypeError: If data is not bytes
    """
    if not isinstance(data, bytes):
        raise TypeError("Input must be bytes")
    
    if len(data) == 0:
        raise DBORDecodeError("Empty data")
    
    result, pos = _decode_value(data, 0)
    
    if pos != len(data):
        raise DBORDecodeError(f"Unexpected data after end of value at position {pos}")
    
    return result


def _decode_value(data, pos):
    """
    Decode a single DBOR value from data starting at position pos.
    
    Args:
        data: bytes object containing DBOR data
        pos: Starting position
        
    Returns:
        tuple: (decoded_value, new_position)
        
    Raises:
        DBORDecodeError: If decoding fails
    """
    if pos >= len(data):
        raise DBORDecodeError("Unexpected end of data")
    
    first_byte = data[pos]
    
    # Special case for NoneValue
    if first_byte == 0xFF:
        return None, pos + 1
    
    header = (first_byte >> 5) & 0x7
    
    if header == 0:  # Positive integer
        value, new_pos = decode_integer_token(data, pos)
        return value, new_pos
    
    elif header == 1:  # Negative integer
        magnitude, new_pos = decode_integer_token(data, pos)
        return -magnitude - 1, new_pos
    
    elif header == 2:  # ByteString
        length, new_pos = decode_integer_token(data, pos)
        if new_pos + length > len(data):
            raise DBORDecodeError("Unexpected end of data in ByteString")
        byte_string = data[new_pos:new_pos + length]
        return byte_string, new_pos + length
    
    elif header == 3:  # Utf8String
        length, new_pos = decode_integer_token(data, pos)
        if new_pos + length > len(data):
            raise DBORDecodeError("Unexpected end of data in Utf8String")
        utf8_bytes = data[new_pos:new_pos + length]
        try:
            utf8_string = utf8_bytes.decode('utf-8')
        except UnicodeDecodeError as e:
            raise DBORDecodeError(f"Invalid UTF-8 encoding: {e}")
        return utf8_string, new_pos + length
    
    elif header == 4:  # Sequence
        sequence_length, new_pos = decode_integer_token(data, pos)
        sequence_end = new_pos + sequence_length
        
        if sequence_end > len(data):
            raise DBORDecodeError("Unexpected end of data in Sequence")
        
        sequence = []
        current_pos = new_pos
        
        while current_pos < sequence_end:
            element, current_pos = _decode_value(data, current_pos)
            sequence.append(element)
        
        if current_pos != sequence_end:
            raise DBORDecodeError("Sequence length mismatch")
        
        return sequence, sequence_end
    
    else:
        raise DBORDecodeError(f"Unsupported header type: {header}")
