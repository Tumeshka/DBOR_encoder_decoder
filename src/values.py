"""
DBOR Value Type Definitions for Conformance Level 2

This module defines the value types supported by DBOR conformance level 2
as specified in section 4.3 of the DBOR 1.0.0 specification.
"""

from typing import Union, List, Any
from abc import ABC, abstractmethod


class DBORValue(ABC):
    """Abstract base class for all DBOR values."""
    
    @abstractmethod
    def to_python(self) -> Any:
        """Convert this DBOR value to a Python object."""
        pass
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        """Check equality with another DBOR value."""
        pass


class NoneValue(DBORValue):
    """Represents the DBOR None value."""
    
    def to_python(self) -> None:
        return None
    
    def __eq__(self, other) -> bool:
        return isinstance(other, NoneValue) or other is None
    
    def __repr__(self) -> str:
        return "NoneValue()"


class IntegerValue(DBORValue):
    """
    Represents a DBOR integer value.
    
    For conformance level 2, supports integers in range {−2⁶³ … 2⁶⁴−1}.
    """
    
    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("IntegerValue requires an int")
        
        # Check conformance level 2 bounds
        if value < -(2**63) or value >= 2**64:
            raise ValueError(f"Integer {value} is outside conformance level 2 range [−2⁶³, 2⁶⁴−1]")
        
        self.value = value
    
    def to_python(self) -> int:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, IntegerValue):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return False
    
    def __repr__(self) -> str:
        return f"IntegerValue({self.value})"


class ByteStringValue(DBORValue):
    """Represents a DBOR byte string value."""
    
    def __init__(self, value: bytes):
        if not isinstance(value, bytes):
            raise TypeError("ByteStringValue requires bytes")
        self.value = value
    
    def to_python(self) -> bytes:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, ByteStringValue):
            return self.value == other.value
        if isinstance(other, bytes):
            return self.value == other
        return False
    
    def __repr__(self) -> str:
        return f"ByteStringValue({self.value!r})"


class Utf8StringValue(DBORValue):
    """Represents a DBOR UTF-8 string value."""
    
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("Utf8StringValue requires str")
        
        # Verify it can be encoded as UTF-8
        try:
            value.encode('utf-8')
        except UnicodeEncodeError as e:
            raise ValueError(f"String cannot be encoded as UTF-8: {e}")
        
        self.value = value
    
    def to_python(self) -> str:
        return self.value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Utf8StringValue):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False
    
    def __repr__(self) -> str:
        return f"Utf8StringValue({self.value!r})"


class SequenceValue(DBORValue):
    """
    Represents a DBOR sequence value.
    
    For conformance level 2, can contain any combination of supported level-2 values.
    """
    
    def __init__(self, values: List[DBORValue]):
        if not isinstance(values, (list, tuple)):
            raise TypeError("SequenceValue requires a list or tuple")
        
        # Validate that all elements are supported level-2 values
        for i, value in enumerate(values):
            if not self._is_level2_supported(value):
                raise ValueError(f"Element at index {i} is not a supported level-2 value: {value}")
        
        self.values = list(values)
    
    def _is_level2_supported(self, value) -> bool:
        """Check if a value is supported at conformance level 2."""
        if value is None:
            return True
        if isinstance(value, (NoneValue, IntegerValue, ByteStringValue, Utf8StringValue, SequenceValue)):
            return True
        if isinstance(value, (int, bytes, str)):
            return True
        if isinstance(value, (list, tuple)):
            return all(self._is_level2_supported(item) for item in value)
        return False
    
    def to_python(self) -> List[Any]:
        result = []
        for value in self.values:
            if isinstance(value, DBORValue):
                result.append(value.to_python())
            else:
                result.append(value)
        return result
    
    def __eq__(self, other) -> bool:
        if isinstance(other, SequenceValue):
            return self.values == other.values
        if isinstance(other, (list, tuple)):
            return self.to_python() == list(other)
        return False
    
    def __repr__(self) -> str:
        return f"SequenceValue({self.values!r})"


# Type alias for valid level-2 DBOR values
Level2Value = Union[NoneValue, IntegerValue, ByteStringValue, Utf8StringValue, SequenceValue]


def from_python(value: Any) -> DBORValue:
    """
    Convert a Python value to the appropriate DBOR value type.
    
    Args:
        value: Python value to convert
        
    Returns:
        Corresponding DBOR value object
        
    Raises:
        TypeError: If the value type is not supported at level 2
        ValueError: If the value is invalid for its type
    """
    if value is None:
        return NoneValue()
    
    if isinstance(value, int):
        return IntegerValue(value)
    
    if isinstance(value, bytes):
        return ByteStringValue(value)
    
    if isinstance(value, str):
        return Utf8StringValue(value)
    
    if isinstance(value, (list, tuple)):
        dbor_values = [from_python(item) for item in value]
        return SequenceValue(dbor_values)
    
    raise TypeError(f"Unsupported type for conformance level 2: {type(value).__name__}")


def to_python(dbor_value: DBORValue) -> Any:
    """
    Convert a DBOR value to a Python object.
    
    Args:
        dbor_value: DBOR value to convert
        
    Returns:
        Corresponding Python object
    """
    return dbor_value.to_python()
