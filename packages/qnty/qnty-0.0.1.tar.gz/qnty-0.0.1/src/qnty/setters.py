"""
Specialized Setters
===================

Dimension-specific setters with fluent API and compile-time type safety.
"""

from typing import TYPE_CHECKING
from .variable import FastQuantity
from .units import LengthUnits, PressureUnits
from .unit import UnitConstant

if TYPE_CHECKING:
    from .variables import Length, Pressure
    from .variable import TypeSafeVariable


class TypeSafeSetter:
    """Type-safe setter that only accepts compatible units."""
    
    def __init__(self, variable: 'TypeSafeVariable', value: float):
        self.variable = variable
        self.value = value
    
    def with_unit(self, unit: UnitConstant) -> 'TypeSafeVariable':
        """Set with type-safe unit constant."""
        if not self.variable.expected_dimension.is_compatible(unit.dimension):
            raise TypeError(f"Unit {unit.name} incompatible with expected dimension")
        
        self.variable.quantity = FastQuantity(self.value, unit)
        return self.variable


class LengthSetter:
    """Length-specific setter with only length units."""
    
    def __init__(self, variable: 'Length', value: float):
        self.variable = variable
        self.value = value
    
    # Only length units available - compile-time safe!
    @property
    def meters(self) -> 'Length':
        self.variable.quantity = FastQuantity(self.value, LengthUnits.meter)
        return self.variable
    
    @property
    def millimeters(self) -> 'Length':
        self.variable.quantity = FastQuantity(self.value, LengthUnits.millimeter)
        return self.variable
    
    @property
    def inches(self) -> 'Length':
        self.variable.quantity = FastQuantity(self.value, LengthUnits.inch)
        return self.variable
    
    @property
    def feet(self) -> 'Length':
        self.variable.quantity = FastQuantity(self.value, LengthUnits.foot)
        return self.variable


class PressureSetter:
    """Pressure-specific setter with only pressure units."""
    
    def __init__(self, variable: 'Pressure', value: float):
        self.variable = variable
        self.value = value
    
    # Only pressure units available - compile-time safe!
    @property 
    def psi(self) -> 'Pressure':
        self.variable.quantity = FastQuantity(self.value, PressureUnits.psi)
        return self.variable
    
    @property
    def kPa(self) -> 'Pressure':
        self.variable.quantity = FastQuantity(self.value, PressureUnits.kilopascal)
        return self.variable
    
    @property
    def MPa(self) -> 'Pressure':
        self.variable.quantity = FastQuantity(self.value, PressureUnits.megapascal)
        return self.variable
    
    @property
    def bar(self) -> 'Pressure':
        self.variable.quantity = FastQuantity(self.value, PressureUnits.bar)
        return self.variable