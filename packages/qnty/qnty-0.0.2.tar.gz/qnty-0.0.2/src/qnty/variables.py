"""
Specialized Variables and Setters
==================================

Dimension-specific variable classes with type safety, fluent API setters,
and mathematical operations for expressions and equations.
"""

from __future__ import annotations

from typing import cast

from .dimension import DIMENSIONLESS, LENGTH, PRESSURE
from .equation import Equation
from .expression import Expression, wrap_operand
from .units import DimensionlessUnits, LengthUnits, PressureUnits
from .variable import FastQuantity, TypeSafeSetter, TypeSafeVariable


class ExpressionVariable(TypeSafeVariable):
    """
    TypeSafeVariable extended with expression and equation capabilities.
    
    This adds mathematical operations that create expressions and equations,
    keeping the base TypeSafeVariable free of these dependencies.
    """
    
    def equals(self, expression: Expression | TypeSafeVariable | FastQuantity | int | float):
        """Create an equation: self = expression."""
        # Wrap the expression in proper Expression type
        rhs_expr = wrap_operand(expression)
        return Equation(f"{self.name}_eq", self, rhs_expr)
    
    def __add__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Add this variable to another operand, returning an Expression."""
        return wrap_operand(self) + wrap_operand(other)

    def __radd__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse add for this variable."""
        return wrap_operand(other) + wrap_operand(self)
    
    def __sub__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Subtract another operand from this variable, returning an Expression."""
        return wrap_operand(self) - wrap_operand(other)
    
    def __rsub__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse subtract for this variable."""
        return wrap_operand(other) - wrap_operand(self)
    
    def __mul__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Multiply this variable by another operand, returning an Expression."""
        return wrap_operand(self) * wrap_operand(other)
    
    def __rmul__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse multiply for this variable."""
        return wrap_operand(other) * wrap_operand(self)
    
    def __truediv__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Divide this variable by another operand, returning an Expression."""
        return wrap_operand(self) / wrap_operand(other)

    def __rtruediv__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse divide for this variable."""
        return wrap_operand(other) / wrap_operand(self)
    
    def __pow__(self, other: TypeSafeVariable | FastQuantity | int | float) -> Expression:
        """Raise this variable to a power, returning an Expression."""
        return wrap_operand(self) ** wrap_operand(other)

    def __rpow__(self, other: FastQuantity | int | float) -> Expression:
        """Reverse power for this variable."""
        return wrap_operand(other) ** wrap_operand(self)


# Specialized setter classes
class LengthSetter(TypeSafeSetter):
    """Length-specific setter with only length units."""
    
    def __init__(self, variable: Length, value: float):
        super().__init__(variable, value)
    
    # Only length units available - compile-time safe!
    @property
    def meters(self) -> Length:
        self.variable.quantity = FastQuantity(self.value, LengthUnits.meter)
        return cast(Length, self.variable)
    
    @property
    def millimeters(self) -> Length:
        self.variable.quantity = FastQuantity(self.value, LengthUnits.millimeter)
        return cast(Length, self.variable)
    
    @property
    def inches(self) -> Length:
        self.variable.quantity = FastQuantity(self.value, LengthUnits.inch)
        return cast(Length, self.variable)
    
    @property
    def feet(self) -> Length:
        self.variable.quantity = FastQuantity(self.value, LengthUnits.foot)
        return cast(Length, self.variable)


class PressureSetter(TypeSafeSetter):
    """Pressure-specific setter with only pressure units."""
    
    def __init__(self, variable: Pressure, value: float):
        super().__init__(variable, value)
    
    # Only pressure units available - compile-time safe!
    @property
    def psi(self) -> Pressure:
        self.variable.quantity = FastQuantity(self.value, PressureUnits.psi)
        return cast(Pressure, self.variable)
    
    @property
    def kPa(self) -> Pressure:
        self.variable.quantity = FastQuantity(self.value, PressureUnits.kilopascal)
        return cast(Pressure, self.variable)
    
    @property
    def MPa(self) -> Pressure:
        self.variable.quantity = FastQuantity(self.value, PressureUnits.megapascal)
        return cast(Pressure, self.variable)
    
    @property
    def bar(self) -> Pressure:
        self.variable.quantity = FastQuantity(self.value, PressureUnits.bar)
        return cast(Pressure, self.variable)


class DimensionlessSetter(TypeSafeSetter):
    """Dimensionless-specific setter with only dimensionless units."""
    
    def __init__(self, variable: Dimensionless, value: float):
        super().__init__(variable, value)
    
    # Dimensionless units
    @property
    def dimensionless(self) -> Dimensionless:
        self.variable.quantity = FastQuantity(self.value, DimensionlessUnits.dimensionless)
        return cast(Dimensionless, self.variable)
    
    # Common alias for no units
    @property
    def unitless(self) -> Dimensionless:
        self.variable.quantity = FastQuantity(self.value, DimensionlessUnits.dimensionless)
        return cast(Dimensionless, self.variable)


# Specialized variable types that users interact with
class Length(ExpressionVariable):
    """Type-safe length variable with expression capabilities."""
    
    _setter_class = LengthSetter
    
    def __init__(self, *args, is_known: bool = True):
        if len(args) == 1:
            # Length("name") - original syntax
            super().__init__(args[0], LENGTH, is_known=is_known)
        elif len(args) == 3:
            # Length(value, "unit", "name") - new syntax
            value, unit, name = args
            super().__init__(name, LENGTH, is_known=is_known)
            # Auto-set the value with the specified unit
            setter = LengthSetter(self, value)
            # Get the unit setter method dynamically
            if unit == "in":  # Handle "in" alias for inches
                setter.inches
            elif hasattr(setter, unit):
                getattr(setter, unit)
            elif hasattr(setter, unit + 's'):  # Handle singular/plural
                getattr(setter, unit + 's')
            else:
                # Default to meters if unit not recognized
                setter.meters
        else:
            raise ValueError("Length expects either 1 argument (name) or 3 arguments (value, unit, name)")


class Pressure(ExpressionVariable):
    """Type-safe pressure variable with expression capabilities."""
    
    _setter_class = PressureSetter
    
    def __init__(self, *args, is_known: bool = True):
        if len(args) == 1:
            # Pressure("name") - original syntax
            super().__init__(args[0], PRESSURE, is_known=is_known)
        elif len(args) == 3:
            # Pressure(value, "unit", "name") - new syntax
            value, unit, name = args
            super().__init__(name, PRESSURE, is_known=is_known)
            # Auto-set the value with the specified unit
            setter = PressureSetter(self, value)
            # Get the unit setter method dynamically
            if unit == "psi":
                setter.psi
            elif unit == "kPa":
                setter.kPa
            elif unit == "MPa":
                setter.MPa
            elif unit == "bar":
                setter.bar
            else:
                # Default to psi if unit not recognized
                setter.psi
        else:
            raise ValueError("Pressure expects either 1 argument (name) or 3 arguments (value, unit, name)")


class Dimensionless(ExpressionVariable):
    """Type-safe dimensionless variable with expression capabilities."""

    _setter_class = DimensionlessSetter

    def __init__(self, *args, is_known: bool = True):
        if len(args) == 1:
            # Dimensionless("name") - original syntax
            super().__init__(args[0], DIMENSIONLESS, is_known=is_known)
        elif len(args) == 2:
            # Dimensionless(value, "name") - new syntax
            value, name = args
            super().__init__(name, DIMENSIONLESS, is_known=is_known)
            # Auto-set the value as dimensionless
            setter = DimensionlessSetter(self, value)
            setter.dimensionless
        else:
            raise ValueError("Dimensionless expects either 1 argument (name) or 2 arguments (value, name)")
