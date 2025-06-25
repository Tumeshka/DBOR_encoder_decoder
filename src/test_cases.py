"""
Test Cases and Generators for DBOR Conformance Level 2

This module provides comprehensive test cases for validating DBOR encoder/decoder
round-trip integrity at conformance level 2.
"""

import random
from typing import List, Any, Iterator


class TestCaseGenerator:
    """Generates test cases for DBOR conformance level 2."""
    
    @staticmethod
    def primitive_values() -> List[Any]:
        """Generate basic primitive values for testing."""
        return [
            # None value
            None,
            
            # Integer boundary cases
            0,
            1,
            -1,
            23,  # Boundary for direct encoding
            24,  # First extended encoding
            255,  # Single byte extended
            256,  # Two byte extended
            65535,  # Two byte max
            65536,  # Three byte start
            
            # Large integer boundaries
            2**63 - 1,   # Max positive for signed 64-bit
            -(2**63),    # Min negative for signed 64-bit
            2**64 - 1,   # Max for conformance level 2
            
            # Byte strings
            b"",
            b"hello",
            b"\x00\x01\x02\xff",
            b"\x80\x81\x82",  # High bit set
            
            # UTF-8 strings
            "",
            "hello",
            "world",
            "ASCII text",
            "üñîçødë",  # Unicode characters
            "🚀🌟💯",   # Emoji
            "こんにちは",  # Japanese
            "Здравствуй",  # Cyrillic
        ]
    
    @staticmethod
    def sequence_values() -> List[Any]:
        """Generate sequence values for testing."""
        primitives = TestCaseGenerator.primitive_values()
        
        return [
            # Empty sequence
            [],
            
            # Single element sequences
            [None],
            [0],
            [b"bytes"],
            ["string"],
            
            # Multi-element sequences
            [None, 0, 1],
            [1, "hello", b"world"],
            ["mixed", 42, b"\x01\x02", None],
            
            # Nested sequences
            [[]],
            [[None]],
            [[1, 2], [3, 4]],
            [["nested", ["more", "nesting"]], 123],
            [[[], []], []],
            
            # Sequences with various combinations
            [primitives[:5]],  # First 5 primitives
            [primitives[5:10]],  # Next 5 primitives
            
            # Deep nesting
            [[[[[None]]]]],
            [1, [2, [3, [4, [5]]]]],
        ]
    
    @staticmethod
    def edge_cases() -> List[Any]:
        """Generate edge case values for stress testing."""
        return [
            # Integer edge cases
            23,   # Last direct encoding
            24,   # First extended encoding
            2**8 - 1 + 23,   # Last 1-byte extended
            2**8 + 23,       # First 2-byte extended
            2**16 - 1 + 23,  # Last 2-byte extended
            2**16 + 23,      # First 3-byte extended
            
            # Negative equivalents
            -24,  # First negative extended
            -(2**8 + 23),
            -(2**16 + 23),
            
            # Large values near boundaries
            2**32 - 1,
            2**32,
            2**48 - 1,
            2**48,
            
            # Empty and single-char strings
            b"",
            b"a",
            "",
            "a",
            
            # Long strings (but not too long for testing)
            b"x" * 1000,
            "y" * 1000,
            
            # Sequences with many elements
            list(range(100)),
            [None] * 50,
            [b""] * 25,
            
            # Mixed deeply nested
            [i for i in range(10)] + [[j for j in range(5)] for _ in range(3)],
        ]
    
    @staticmethod
    def generate_random_integer(min_val: int = -(2**63), max_val: int = 2**64 - 1) -> int:
        """Generate a random integer within conformance level 2 bounds."""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def generate_random_bytes(max_length: int = 100) -> bytes:
        """Generate random bytes of varying length."""
        length = random.randint(0, max_length)
        return bytes(random.randint(0, 255) for _ in range(length))
    
    @staticmethod
    def generate_random_string(max_length: int = 100) -> str:
        """Generate random UTF-8 string."""
        # Mix of ASCII and Unicode characters
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        unicode_chars = "üñîçødëαβγδεζηθικλμνξοπρστυφχψω🚀🌟💯"
        all_chars = chars + unicode_chars
        
        length = random.randint(0, max_length)
        return ''.join(random.choice(all_chars) for _ in range(length))
    
    @staticmethod
    def generate_random_sequence(max_depth: int = 3, max_elements: int = 10) -> Any:
        """Generate a random sequence with controlled depth and size."""
        if max_depth <= 0:
            # Generate primitive value
            choice = random.choice(['none', 'int', 'bytes', 'str'])
            if choice == 'none':
                return None
            elif choice == 'int':
                return TestCaseGenerator.generate_random_integer()
            elif choice == 'bytes':
                return TestCaseGenerator.generate_random_bytes(20)
            else:  # str
                return TestCaseGenerator.generate_random_string(20)
        
        # Generate sequence
        num_elements = random.randint(0, max_elements)
        sequence = []
        
        for _ in range(num_elements):
            if random.random() < 0.3:  # 30% chance of nested sequence
                element = TestCaseGenerator.generate_random_sequence(max_depth - 1, max_elements // 2)
                if isinstance(element, list):
                    sequence.append(element)
                else:
                    sequence.append(element)
            else:
                # Add primitive
                element = TestCaseGenerator.generate_random_sequence(0, 0)  # Force primitive
                sequence.append(element)
        
        return sequence
    
    @staticmethod
    def all_test_cases() -> List[Any]:
        """Get all test cases combined."""
        test_cases = []
        test_cases.extend(TestCaseGenerator.primitive_values())
        test_cases.extend(TestCaseGenerator.sequence_values())
        test_cases.extend(TestCaseGenerator.edge_cases())
        return test_cases
    
    @staticmethod
    def random_test_cases(count: int = 100) -> List[Any]:
        """Generate a specified number of random test cases."""
        random.seed(42)  # For reproducible tests
        test_cases = []
        
        for _ in range(count):
            case = TestCaseGenerator.generate_random_sequence(max_depth=4, max_elements=8)
            test_cases.append(case)
        
        return test_cases


def get_boundary_integers() -> List[int]:
    """Get integer values at important boundaries for conformance level 2."""
    return [
        # Zero and small values
        0, 1, -1, 
        
        # Direct encoding boundary (0-23)
        22, 23, 24, 25,
        
        # Extended encoding boundaries
        2**8 - 1 + 23,   # Last 1-byte
        2**8 + 23,       # First 2-byte
        2**16 - 1 + 23,  # Last 2-byte
        2**16 + 23,      # First 3-byte
        2**24 - 1 + 23,  # Last 3-byte
        2**24 + 23,      # First 4-byte
        2**32 - 1 + 23,  # Last 4-byte
        2**32 + 23,      # First 5-byte
        2**40 - 1 + 23,  # Last 5-byte
        2**40 + 23,      # First 6-byte
        2**48 - 1 + 23,  # Last 6-byte
        2**48 + 23,      # First 7-byte
        2**56 - 1 + 23,  # Last 7-byte
        2**56 + 23,      # First 8-byte
        
        # Large values
        2**32 - 1,
        2**32,
        2**63 - 1,    # Max signed 64-bit
        -(2**63),     # Min signed 64-bit
        2**64 - 1,    # Max conformance level 2
        
        # Negative equivalents of some boundaries
        -24, -25,
        -(2**8 + 23),
        -(2**16 + 23),
        -(2**32),
        -(2**32 - 1),
    ]


def get_string_test_cases() -> List[str]:
    """Get comprehensive string test cases."""
    return [
        "",                    # Empty string
        "a",                   # Single ASCII
        "hello world",         # Basic ASCII
        "Hello, World! 123",   # ASCII with punctuation and numbers
        
        # Unicode categories
        "café",                # Latin-1 supplement
        "naïve",              # Combining characters
        "üñîçødë",            # Extended Latin
        "Здравствуй мир",     # Cyrillic
        "こんにちは世界",        # Japanese Hiragana/Kanji
        "안녕하세요",           # Korean Hangul
        "مرحبا بالعالم",        # Arabic
        "שלום עולם",           # Hebrew
        
        # Emoji and symbols
        "🚀",                  # Single emoji
        "🌟💯✨",              # Multiple emoji
        "Hello 🌍!",          # Mixed text and emoji
        "©®™",                 # Copyright symbols
        "♠♣♥♦",               # Card suits
        "αβγδεζηθικλμνξοπρστυφχψω",  # Greek alphabet
        
        # Edge cases
        " ",                   # Single space
        "\t\n\r",            # Whitespace characters
        "\"quotes\"",         # Quotes
        "back\\slash",        # Backslashes
        "line\nbreak",        # Line breaks
        
        # Long strings
        "a" * 100,            # Long ASCII
        "ü" * 50,             # Long Unicode
    ]


def get_bytes_test_cases() -> List[bytes]:
    """Get comprehensive byte string test cases."""
    return [
        b"",                   # Empty bytes
        b"\x00",              # Null byte
        b"hello",             # ASCII bytes
        b"Hello, World!",     # ASCII with punctuation
        
        # Binary data patterns
        b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f",
        b"\xff\xfe\xfd\xfc\xfb\xfa\xf9\xf8\xf7\xf6\xf5\xf4\xf3\xf2\xf1\xf0",
        b"\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f",
        
        # Random-looking data
        bytes(range(256)),     # All possible byte values
        b"\xde\xad\xbe\xef",  # Common hex pattern
        b"\xca\xfe\xba\xbe",  # Another common pattern
        
        # Repeated patterns
        b"\x00" * 100,        # Many zeros
        b"\xff" * 50,         # Many 0xFF
        b"\xaa\x55" * 25,     # Alternating pattern
        
        # UTF-8 encoded text (but treated as bytes)
        "Hello, 世界!".encode('utf-8'),
        "🚀🌟💯".encode('utf-8'),
    ]
