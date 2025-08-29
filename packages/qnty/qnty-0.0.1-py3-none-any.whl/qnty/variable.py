"""
High-Performance Quantity and Variables
========================================

FastQuantity class and type-safe variables optimized for engineering calculations 
with dimensional safety.
"""

from typing import Union, Optional, TypeVar, Generic, TYPE_CHECKING
from .dimension import DimensionSignature, DIMENSIONLESS, LENGTH, PRESSURE, AREA, VOLUME, FORCE, ENERGY
from .unit import UnitConstant, UnitDefinition, registry
from .units import DimensionlessUnits, LengthUnits, PressureUnits

if TYPE_CHECKING:
    from .setters import TypeSafeSetter, LengthSetter, PressureSetter


DimensionType = TypeVar('DimensionType', bound='FastQuantity')
SetterType = TypeVar('SetterType')


class FastQuantity:
    """High-performance quantity optimized for engineering calculations."""
    
    __slots__ = ('value', 'unit', 'dimension', '_si_factor', '_dimension_sig')
    
    def __init__(self, value: float, unit: UnitConstant):
        self.value = float(value)
        self.unit = unit
        self.dimension = unit.dimension
        # Cache commonly used values to avoid lookups
        self._si_factor = unit.si_factor
        self._dimension_sig = unit.dimension._signature
    
    def __str__(self):
        return f"{self.value} {self.unit.symbol}"
    
    def __repr__(self):
        return f"FastQuantity({self.value}, {self.unit.name})"
    
    # Ultra-fast arithmetic with dimensional checking
    def __add__(self, other: 'FastQuantity') -> 'FastQuantity':
        # Fast dimension compatibility check using cached signatures
        if self._dimension_sig != other._dimension_sig:
            raise ValueError(f"Cannot add {self.unit.name} and {other.unit.name}")
        
        # Fast path for same units - no conversion needed
        if self.unit == other.unit:
            return FastQuantity(self.value + other.value, self.unit)
        
        # Convert other to self's units using cached SI factors
        other_value = other.value * other._si_factor / self._si_factor
        return FastQuantity(self.value + other_value, self.unit)
    
    def __sub__(self, other: 'FastQuantity') -> 'FastQuantity':
        # Fast dimension compatibility check using cached signatures
        if self._dimension_sig != other._dimension_sig:
            raise ValueError(f"Cannot subtract {other.unit.name} from {self.unit.name}")
        
        # Fast path for same units - no conversion needed
        if self.unit == other.unit:
            return FastQuantity(self.value - other.value, self.unit)
        
        # Convert other to self's units using cached SI factors
        other_value = other.value * other._si_factor / self._si_factor
        return FastQuantity(self.value - other_value, self.unit)
    
    def __mul__(self, other: Union['FastQuantity', float, int]) -> 'FastQuantity':
        if isinstance(other, (int, float)):
            return FastQuantity(self.value * other, self.unit)
        
        # Fast dimensional analysis using cached signatures
        result_dimension_sig = self._dimension_sig * other._dimension_sig
        
        # Use cached SI factors for conversion
        self_si_value = self.value * self._si_factor
        other_si_value = other.value * other._si_factor
        result_si_value = self_si_value * other_si_value
        
        # Fast path for common dimension combinations
        result_unit = self._find_result_unit_fast(result_dimension_sig, self, other)
        result_value = result_si_value / result_unit.si_factor
        
        return FastQuantity(result_value, result_unit)
    
    def __rmul__(self, other: Union[float, int]) -> 'FastQuantity':
        """Reverse multiplication for cases like 2 * quantity."""
        if isinstance(other, (int, float)):
            return FastQuantity(other * self.value, self.unit)
        return NotImplemented
    
    def __truediv__(self, other: Union['FastQuantity', float, int]) -> 'FastQuantity':
        if isinstance(other, (int, float)):
            return FastQuantity(self.value / other, self.unit)
        
        # Fast dimensional analysis using cached signatures
        result_dimension_sig = self._dimension_sig // other._dimension_sig
        
        # Use cached SI factors for conversion
        self_si_value = self.value * self._si_factor
        other_si_value = other.value * other._si_factor
        result_si_value = self_si_value / other_si_value
        
        # Fast path for common dimension combinations
        result_unit = self._find_result_unit_fast(result_dimension_sig, self, other)
        result_value = result_si_value / result_unit.si_factor
        
        return FastQuantity(result_value, result_unit)
    
    def _find_result_unit_fast(self, result_dimension_sig: int, 
                              left_qty: 'FastQuantity', right_qty: 'FastQuantity') -> UnitConstant:
        """Ultra-fast unit finding using cached dimension signatures."""
        
        # Initialize dimension cache if empty
        if not registry._dimension_cache:
            registry._dimension_cache = {
                DIMENSIONLESS._signature: DimensionlessUnits.dimensionless,
                LENGTH._signature: LengthUnits.millimeter,
                PRESSURE._signature: PressureUnits.Pa,
                AREA._signature: LengthUnits.millimeter,  # mm²
                VOLUME._signature: LengthUnits.millimeter,  # mm³
                FORCE._signature: UnitConstant(UnitDefinition("newton", "N", FORCE, 1.0)),
                ENERGY._signature: UnitConstant(UnitDefinition("joule", "J", ENERGY, 1.0)),
            }
        
        # O(1) lookup for common dimensions
        if result_dimension_sig in registry._dimension_cache:
            return registry._dimension_cache[result_dimension_sig]
        
        # For rare combined dimensions, create temporary unit
        temp_unit = UnitDefinition(
            name=f"combined_{result_dimension_sig}",
            symbol="combined", 
            dimension=DimensionSignature(result_dimension_sig),
            si_factor=1.0
        )
        result_unit = UnitConstant(temp_unit)
        
        # Cache for future use
        registry._dimension_cache[result_dimension_sig] = result_unit
        return result_unit
    
    def _find_result_unit(self, result_dimension: DimensionSignature, 
                         left_qty: 'FastQuantity', right_qty: 'FastQuantity') -> UnitConstant:
        """Legacy method - kept for compatibility."""
        return self._find_result_unit_fast(result_dimension._signature, left_qty, right_qty)
    
    # Ultra-fast comparisons
    def __lt__(self, other: 'FastQuantity') -> bool:
        if self._dimension_sig != other._dimension_sig:
            raise ValueError("Cannot compare incompatible dimensions")
        
        # Fast path for same units
        if self.unit == other.unit:
            return self.value < other.value
            
        # Convert using cached SI factors
        other_value = other.value * other._si_factor / self._si_factor
        return self.value < other_value
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FastQuantity):
            return False
        if self._dimension_sig != other._dimension_sig:
            return False
        
        # Fast path for same units
        if self.unit == other.unit:
            return abs(self.value - other.value) < 1e-10
            
        # Convert using cached SI factors
        other_value = other.value * other._si_factor / self._si_factor
        return abs(self.value - other_value) < 1e-10
    
    def to(self, target_unit: UnitConstant) -> 'FastQuantity':
        """Ultra-fast unit conversion."""
        if self.unit == target_unit:
            return FastQuantity(self.value, target_unit)
        
        # Direct SI factor conversion - avoid registry lookup
        converted_value = self.value * self._si_factor / target_unit.si_factor
        return FastQuantity(converted_value, target_unit)


class TypeSafeVariable(Generic[DimensionType]):
    """Type-safe variable with compile-time dimensional checking."""
    
    def __init__(self, name: str, expected_dimension: DimensionSignature):
        self.name = name
        self.expected_dimension = expected_dimension
        self.quantity: Optional[FastQuantity] = None
    
    def set(self, value: float) -> Union['TypeSafeSetter', 'LengthSetter', 'PressureSetter']:
        from .setters import TypeSafeSetter
        return TypeSafeSetter(self, value)
    
    def __str__(self):
        return f"{self.name}: {self.quantity}" if self.quantity else f"{self.name}: unset"