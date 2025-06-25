"""
Round-Trip Tests for DBOR Conformance Level 2

This module contains comprehensive tests to verify that decode(encode(input)) == input
for all valid level-2 DBOR values.
"""

import unittest
import json
import os
from typing import Any, List
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from encoder import encode
from decoder import decode, DBORDecodeError
from test_cases import (
    TestCaseGenerator, 
    get_boundary_integers, 
    get_string_test_cases, 
    get_bytes_test_cases
)


class TestRoundTrip(unittest.TestCase):
    """Test round-trip integrity of DBOR encoder/decoder pairs."""
    
    def assert_round_trip(self, value: Any) -> None:
        """
        Assert that a value survives round-trip encoding/decoding.
        
        Args:
            value: The value to test
            
        Raises:
            AssertionError: If round-trip fails
        """
        try:
            encoded = encode(value)
            decoded = decode(encoded)
            self.assertEqual(decoded, value, 
                           f"Round-trip failed for {value!r}. "
                           f"Encoded: {encoded.hex()}, Decoded: {decoded!r}")
        except Exception as e:
            self.fail(f"Round-trip failed for {value!r} with exception: {e}")
    
    def test_none_value(self):
        """Test None value round-trip."""
        self.assert_round_trip(None)
    
    def test_primitive_integers(self):
        """Test basic integer values."""
        test_integers = [
            0, 1, -1, 2, -2, 10, -10, 100, -100,
            23, 24, 25,  # Encoding boundary
            255, 256, 257,  # Byte boundaries
            65535, 65536, 65537,  # Two-byte boundaries
        ]
        
        for integer in test_integers:
            with self.subTest(integer=integer):
                self.assert_round_trip(integer)
    
    def test_boundary_integers(self):
        """Test integer values at important encoding boundaries."""
        boundary_integers = get_boundary_integers()
        
        for integer in boundary_integers:
            with self.subTest(integer=integer):
                self.assert_round_trip(integer)
    
    def test_large_integers(self):
        """Test large integers near conformance level 2 limits."""
        large_integers = [
            2**32 - 1,
            2**32,
            2**48 - 1,
            2**48,
            2**63 - 1,    # Max signed 64-bit
            -(2**63),     # Min signed 64-bit
            2**64 - 1,    # Max conformance level 2
        ]
        
        for integer in large_integers:
            with self.subTest(integer=integer):
                self.assert_round_trip(integer)
    
    def test_invalid_integers(self):
        """Test that invalid integers raise appropriate errors."""
        invalid_integers = [
            2**64,        # Too large
            -(2**63) - 1, # Too small
        ]
        
        for integer in invalid_integers:
            with self.subTest(integer=integer):
                with self.assertRaises((OverflowError, ValueError)):
                    encode(integer)
    
    def test_byte_strings(self):
        """Test byte string round-trips."""
        byte_test_cases = get_bytes_test_cases()
        
        for byte_string in byte_test_cases:
            with self.subTest(byte_string=byte_string):
                self.assert_round_trip(byte_string)
    
    def test_utf8_strings(self):
        """Test UTF-8 string round-trips."""
        string_test_cases = get_string_test_cases()
        
        for string in string_test_cases:
            with self.subTest(string=string):
                self.assert_round_trip(string)
    
    def test_empty_sequence(self):
        """Test empty sequence."""
        self.assert_round_trip([])
    
    def test_single_element_sequences(self):
        """Test sequences with single elements."""
        single_element_cases = [
            [None],
            [0],
            [1],
            [-1],
            [b"bytes"],
            ["string"],
            [[]],  # Nested empty sequence
        ]
        
        for sequence in single_element_cases:
            with self.subTest(sequence=sequence):
                self.assert_round_trip(sequence)
    
    def test_multi_element_sequences(self):
        """Test sequences with multiple elements."""
        multi_element_cases = [
            [None, 0, 1],
            [1, "hello", b"world"],
            ["mixed", 42, b"\x01\x02", None],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [-1, -2, -3, -4, -5],
        ]
        
        for sequence in multi_element_cases:
            with self.subTest(sequence=sequence):
                self.assert_round_trip(sequence)
    
    def test_nested_sequences(self):
        """Test nested sequence structures."""
        nested_cases = [
            [[]],
            [[None]],
            [[1, 2], [3, 4]],
            [["nested", ["more", "nesting"]], 123],
            [[[], []], []],
            [[[[[None]]]]],  # Deep nesting
            [1, [2, [3, [4, [5]]]]],  # Progressive nesting
        ]
        
        for sequence in nested_cases:
            with self.subTest(sequence=sequence):
                self.assert_round_trip(sequence)
    
    def test_all_primitive_values(self):
        """Test all primitive values from test case generator."""
        primitives = TestCaseGenerator.primitive_values()
        
        for value in primitives:
            with self.subTest(value=value):
                self.assert_round_trip(value)
    
    def test_all_sequence_values(self):
        """Test all sequence values from test case generator."""
        sequences = TestCaseGenerator.sequence_values()
        
        for sequence in sequences:
            with self.subTest(sequence=sequence):
                self.assert_round_trip(sequence)
    
    def test_edge_cases(self):
        """Test edge case values."""
        edge_cases = TestCaseGenerator.edge_cases()
        
        for case in edge_cases:
            with self.subTest(case=case):
                self.assert_round_trip(case)
    
    def test_random_cases(self):
        """Test randomly generated cases."""
        random_cases = TestCaseGenerator.random_test_cases(50)
        
        for i, case in enumerate(random_cases):
            with self.subTest(case_index=i, case=case):
                self.assert_round_trip(case)
    
    def test_comprehensive_mixed_cases(self):
        """Test comprehensive mixed cases combining all types."""
        mixed_cases = [
            # Mix of all primitive types
            [None, 42, b"bytes", "string"],
            [0, -1, b"", "", []],
            
            # Complex nested structures
            [
                None, 
                [1, 2, 3], 
                b"binary", 
                "text", 
                [
                    ["deep", b"nesting"], 
                    42, 
                    [None, "more"]
                ]
            ],
            
            # Large mixed sequence
            list(range(10)) + ["strings", b"bytes"] + [[i] for i in range(5)],
            
            # Edge case combinations
            [2**63 - 1, -(2**63), b"\x00\xff", "🚀", [[[[None]]]]],
        ]
        
        for case in mixed_cases:
            with self.subTest(case=case):
                self.assert_round_trip(case)


class TestEncodingProperties(unittest.TestCase):
    """Test specific properties of DBOR encoding."""
    
    def test_none_encoding(self):
        """Test that None encodes to 0xFF."""
        encoded = encode(None)
        self.assertEqual(encoded, b'\xFF')
    
    def test_empty_sequence_encoding(self):
        """Test that empty sequence has correct structure."""
        encoded = encode([])
        # Should be header 4 (sequence) with length 0
        self.assertEqual(encoded[0] >> 5, 4)  # Header 4
        self.assertEqual(encoded[0] & 0x1F, 0)  # Length 0
    
    def test_small_integer_encoding(self):
        """Test that small integers (0-23) encode directly."""
        for i in range(24):
            encoded = encode(i)
            self.assertEqual(len(encoded), 1)
            self.assertEqual(encoded[0] >> 5, 0)  # Header 0 (positive int)
            self.assertEqual(encoded[0] & 0x1F, i)  # Direct value
    
    def test_empty_string_encoding(self):
        """Test empty string and bytes encoding."""
        # Empty string
        encoded_str = encode("")
        self.assertEqual(encoded_str[0] >> 5, 3)  # Header 3 (UTF-8)
        self.assertEqual(encoded_str[0] & 0x1F, 0)  # Length 0
        
        # Empty bytes
        encoded_bytes = encode(b"")
        self.assertEqual(encoded_bytes[0] >> 5, 2)  # Header 2 (bytes)
        self.assertEqual(encoded_bytes[0] & 0x1F, 0)  # Length 0


class TestErrorHandling(unittest.TestCase):
    """Test error handling in encoding and decoding."""
    
    def test_unsupported_types(self):
        """Test that unsupported types raise TypeError."""
        unsupported_values = [
            1.5,  # float
            complex(1, 2),  # complex
            {"key": "value"},  # dict
            {1, 2, 3},  # set
            object(),  # arbitrary object
        ]
        
        for value in unsupported_values:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    encode(value)
    
    def test_decode_empty_data(self):
        """Test that decoding empty data raises error."""
        with self.assertRaises(DBORDecodeError):
            decode(b"")
    
    def test_decode_invalid_data(self):
        """Test that decoding invalid data raises error."""
        invalid_data = [
            b"\x1F",  # Invalid header
            b"\x20\x01",  # Incomplete data
            b"\x60\x01\xFF",  # Invalid UTF-8
        ]
        
        for data in invalid_data:
            with self.subTest(data=data):
                with self.assertRaises(DBORDecodeError):
                    decode(data)
    
    def test_decode_non_bytes(self):
        """Test that decoding non-bytes raises TypeError."""
        with self.assertRaises(TypeError):
            decode("not bytes")


def load_json_test_data():
    """Load test data from JSON files if they exist."""
    test_data_files = [
        "data_primitive.json",
        "data_sequences.json", 
        "edge_cases.json"
    ]
    
    all_test_data = []
    tests_dir = os.path.dirname(__file__)
    
    for filename in test_data_files:
        filepath = os.path.join(tests_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_test_data.extend(data)
                    else:
                        all_test_data.append(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    return all_test_data


class TestFromJSONData(unittest.TestCase):
    """Test cases loaded from JSON data files."""
    
    def test_json_data_cases(self):
        """Test cases from JSON data files."""
        json_test_data = load_json_test_data()
        
        if not json_test_data:
            self.skipTest("No JSON test data files found")
        
        for i, case in enumerate(json_test_data):
            with self.subTest(case_index=i, case=case):
                try:
                    encoded = encode(case)
                    decoded = decode(encoded)
                    self.assertEqual(decoded, case, 
                                   f"JSON test case {i} failed: {case!r}")
                except Exception as e:
                    self.fail(f"JSON test case {i} failed with exception: {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
