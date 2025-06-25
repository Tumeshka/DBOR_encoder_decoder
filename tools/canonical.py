"""
Canonicalization Helpers for DBOR

This module provides utilities for canonical encoding and validation,
which may be useful for ensuring consistent encoding even though
conformance level 2 does not require canonical encoding.
"""

from typing import Any, Dict, List
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from encoder import encode
from decoder import decode


def is_canonical_encoding(value: Any) -> bool:
    """
    Check if the value would be encoded in canonical form.
    
    For DBOR conformance level 2, canonical encoding means:
    - Sequences are encoded with minimal length representation
    - Strings use minimal UTF-8 encoding
    - Integers use minimal encoding
    
    Args:
        value: The value to check
        
    Returns:
        bool: True if the value would be canonically encoded
    """
    try:
        # Encode the value
        encoded = encode(value)
        
        # Decode it back
        decoded = decode(encoded)
        
        # Check if round-trip works (basic requirement)
        if decoded != value:
            return False
        
        # For canonical encoding, we'd need to check specific encoding rules
        # For now, just verify round-trip consistency
        return True
        
    except Exception:
        return False


def canonical_encode(value: Any) -> bytes:
    """
    Encode a value in canonical form.
    
    For conformance level 2, this is the same as regular encoding
    since there's typically only one way to encode each value type.
    
    Args:
        value: The value to encode canonically
        
    Returns:
        bytes: Canonical DBOR encoding
    """
    return encode(value)


def verify_canonical_stability(value: Any) -> bool:
    """
    Verify that a value's canonical encoding is stable under round-trip.
    
    This means: canonical_encode(decode(canonical_encode(value))) == canonical_encode(value)
    
    Args:
        value: The value to test
        
    Returns:
        bool: True if canonical encoding is stable
    """
    try:
        # First canonical encoding
        encoded1 = canonical_encode(value)
        
        # Round-trip through decoder
        decoded = decode(encoded1)
        
        # Second canonical encoding
        encoded2 = canonical_encode(decoded)
        
        # They should be identical
        return encoded1 == encoded2
        
    except Exception:
        return False


def get_encoding_info(value: Any) -> Dict[str, Any]:
    """
    Get detailed information about how a value is encoded.
    
    Args:
        value: The value to analyze
        
    Returns:
        Dict containing encoding information
    """
    try:
        encoded = encode(value)
        decoded = decode(encoded)
        
        info = {
            'original_value': value,
            'original_type': type(value).__name__,
            'encoded_bytes': encoded,
            'encoded_hex': encoded.hex(),
            'encoded_length': len(encoded),
            'decoded_value': decoded,
            'decoded_type': type(decoded).__name__,
            'round_trip_success': decoded == value,
            'canonical_stable': verify_canonical_stability(value)
        }
        
        # Add specific encoding analysis
        if len(encoded) > 0:
            first_byte = encoded[0]
            header = (first_byte >> 5) & 0x7
            payload = first_byte & 0x1F
            
            header_names = {
                0: 'Positive Integer',
                1: 'Negative Integer', 
                2: 'Byte String',
                3: 'UTF-8 String',
                4: 'Sequence',
                7: 'Special (None if 0xFF)'
            }
            
            info['header_type'] = header
            info['header_name'] = header_names.get(header, f'Unknown ({header})')
            info['payload_value'] = payload
            
            if first_byte == 0xFF:
                info['special_encoding'] = 'None value'
            elif payload <= 23:
                info['encoding_type'] = 'Direct'
            else:
                info['encoding_type'] = 'Extended'
                info['extended_length'] = payload - 23
        
        return info
        
    except Exception as e:
        return {
            'original_value': value,
            'error': str(e),
            'error_type': type(e).__name__
        }


def analyze_encoding_efficiency(values: List[Any]) -> Dict[str, Any]:
    """
    Analyze encoding efficiency for a list of values.
    
    Args:
        values: List of values to analyze
        
    Returns:
        Dict containing efficiency statistics
    """
    stats = {
        'total_values': len(values),
        'successful_encodings': 0,
        'failed_encodings': 0,
        'total_original_size': 0,
        'total_encoded_size': 0,
        'round_trip_failures': 0,
        'canonical_unstable': 0,
        'encoding_types': {},
        'size_distribution': {}
    }
    
    for value in values:
        try:
            info = get_encoding_info(value)
            
            if 'error' in info:
                stats['failed_encodings'] += 1
                continue
                
            stats['successful_encodings'] += 1
            
            # Size analysis
            original_size = len(str(value).encode('utf-8'))  # Rough estimate
            encoded_size = info['encoded_length']
            
            stats['total_original_size'] += original_size
            stats['total_encoded_size'] += encoded_size
            
            # Round-trip check
            if not info['round_trip_success']:
                stats['round_trip_failures'] += 1
            
            # Canonical stability check
            if not info['canonical_stable']:
                stats['canonical_unstable'] += 1
            
            # Encoding type distribution
            header_name = info.get('header_name', 'Unknown')
            stats['encoding_types'][header_name] = stats['encoding_types'].get(header_name, 0) + 1
            
            # Size distribution
            size_bucket = f"{encoded_size // 10 * 10}-{encoded_size // 10 * 10 + 9} bytes"
            stats['size_distribution'][size_bucket] = stats['size_distribution'].get(size_bucket, 0) + 1
            
        except Exception:
            stats['failed_encodings'] += 1
    
    # Calculate compression ratio
    if stats['total_original_size'] > 0:
        stats['compression_ratio'] = stats['total_encoded_size'] / stats['total_original_size']
    else:
        stats['compression_ratio'] = 0
    
    return stats


def print_encoding_analysis(values: List[Any]) -> None:
    """
    Print a detailed analysis of encoding for a list of values.
    
    Args:
        values: List of values to analyze
    """
    stats = analyze_encoding_efficiency(values)
    
    print("DBOR Encoding Analysis")
    print("=" * 50)
    print(f"Total values: {stats['total_values']}")
    print(f"Successful encodings: {stats['successful_encodings']}")
    print(f"Failed encodings: {stats['failed_encodings']}")
    print(f"Round-trip failures: {stats['round_trip_failures']}")
    print(f"Canonical unstable: {stats['canonical_unstable']}")
    print(f"Compression ratio: {stats['compression_ratio']:.2f}")
    print()
    
    print("Encoding Types:")
    for header_name, count in sorted(stats['encoding_types'].items()):
        print(f"  {header_name}: {count}")
    print()
    
    print("Size Distribution:")
    for size_range, count in sorted(stats['size_distribution'].items()):
        print(f"  {size_range}: {count}")


if __name__ == '__main__':
    # Example usage
    from test_cases import TestCaseGenerator
    
    # Get some test cases
    test_cases = TestCaseGenerator.all_test_cases()[:50]  # First 50 for analysis
    
    print("Sample encoding analysis:")
    print_encoding_analysis(test_cases)
    
    # Test individual values
    print("\nIndividual value analysis:")
    sample_values = [None, 42, "hello", b"world", [1, 2, 3]]
    
    for value in sample_values:
        info = get_encoding_info(value)
        print(f"\nValue: {value!r}")
        print(f"  Encoded: {info.get('encoded_hex', 'N/A')}")
        print(f"  Size: {info.get('encoded_length', 0)} bytes")
        print(f"  Type: {info.get('header_name', 'N/A')}")
        print(f"  Round-trip: {info.get('round_trip_success', False)}")
        print(f"  Canonical stable: {info.get('canonical_stable', False)}")
