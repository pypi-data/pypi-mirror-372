"""
Dimension System
================

Compile-time dimensional analysis using type system for ultra-fast operations.
"""

from typing import final
from dataclasses import dataclass
from enum import IntEnum

class BaseDimension(IntEnum):
    """Base dimensions as prime numbers for efficient bit operations."""
    LENGTH = 2
    MASS = 3  
    TIME = 5
    CURRENT = 7
    TEMPERATURE = 11
    AMOUNT = 13
    LUMINOSITY = 17


@final
@dataclass(frozen=True)
class DimensionSignature:
    """Immutable dimension signature for zero-cost dimensional analysis."""
    
    # Store as bit pattern for ultra-fast comparison
    _signature: int = 1
    
    @classmethod
    def create(cls, length=0, mass=0, time=0, current=0, temp=0, amount=0, luminosity=0):
        """Create dimension from exponents."""
        signature = 1
        if length != 0:
            signature *= BaseDimension.LENGTH ** length
        if mass != 0:
            signature *= BaseDimension.MASS ** mass
        if time != 0:
            signature *= BaseDimension.TIME ** time
        if current != 0:
            signature *= BaseDimension.CURRENT ** current
        if temp != 0:
            signature *= BaseDimension.TEMPERATURE ** temp
        if amount != 0:
            signature *= BaseDimension.AMOUNT ** amount
        if luminosity != 0:
            signature *= BaseDimension.LUMINOSITY ** luminosity
        
        return cls(signature)
    
    def __mul__(self, other):
        return DimensionSignature(self._signature * other._signature)
    
    def __truediv__(self, other):
        return DimensionSignature(self._signature // other._signature)
    
    def __pow__(self, power):
        return DimensionSignature(self._signature ** power)
    
    def is_compatible(self, other):
        """Ultra-fast dimensional compatibility check."""
        return self._signature == other._signature
    
    def __eq__(self, other):
        """Fast equality check for dimensions."""
        return isinstance(other, DimensionSignature) and self._signature == other._signature
    
    def __hash__(self):
        """Enable dimensions as dictionary keys."""
        return hash(self._signature)


# Pre-defined dimension constants
DIMENSIONLESS = DimensionSignature.create()
LENGTH = DimensionSignature.create(length=1)
MASS = DimensionSignature.create(mass=1) 
TIME = DimensionSignature.create(time=1)
AREA = DimensionSignature.create(length=2)
VOLUME = DimensionSignature.create(length=3)
VELOCITY = DimensionSignature.create(length=1, time=-1)
ACCELERATION = DimensionSignature.create(length=1, time=-2)
FORCE = DimensionSignature.create(mass=1, length=1, time=-2)
PRESSURE = DimensionSignature.create(mass=1, length=-1, time=-2)
ENERGY = DimensionSignature.create(mass=1, length=2, time=-2)