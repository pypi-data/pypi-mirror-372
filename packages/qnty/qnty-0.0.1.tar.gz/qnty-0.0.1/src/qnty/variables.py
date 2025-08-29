"""
Specialized Variables
=====================

Dimension-specific variable classes with type safety.
"""

from .dimension import LENGTH, PRESSURE
from .variable import TypeSafeVariable
from .setters import LengthSetter, PressureSetter


# Specialized variable types  
class Length(TypeSafeVariable):
    """Type-safe length variable."""
    
    def __init__(self, name: str):
        super().__init__(name, LENGTH)
    
    def set(self, value: float) -> 'LengthSetter':
        return LengthSetter(self, value)


class Pressure(TypeSafeVariable):
    """Type-safe pressure variable."""
    
    def __init__(self, name: str):
        super().__init__(name, PRESSURE)
    
    def set(self, value: float) -> 'PressureSetter':
        return PressureSetter(self, value)