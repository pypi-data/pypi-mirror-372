"""
Predefined Unit Constants
=========================

Type-safe unit constants for common engineering units.
"""

from .unit import UnitConstant, registry


# =====================================================================
# Type-Safe Unit Constants (No More Strings!)
# =====================================================================

class LengthUnits:
    """Type-safe length unit constants."""
    meter = UnitConstant(registry.units["meter"])
    millimeter = UnitConstant(registry.units["millimeter"])
    centimeter = UnitConstant(registry.units["centimeter"])
    inch = UnitConstant(registry.units["inch"])
    foot = UnitConstant(registry.units["foot"])
    
    # Common aliases
    m = meter
    mm = millimeter
    cm = centimeter
    in_ = inch  # 'in' is reserved
    ft = foot


class PressureUnits:
    """Type-safe pressure unit constants."""
    pascal = UnitConstant(registry.units["pascal"])
    kilopascal = UnitConstant(registry.units["kilopascal"])  
    megapascal = UnitConstant(registry.units["megapascal"])
    psi = UnitConstant(registry.units["psi"])
    bar = UnitConstant(registry.units["bar"])
    
    # Common aliases
    Pa = pascal
    kPa = kilopascal
    MPa = megapascal


class DimensionlessUnits:
    """Type-safe dimensionless unit constants."""
    dimensionless = UnitConstant(registry.units["dimensionless"])