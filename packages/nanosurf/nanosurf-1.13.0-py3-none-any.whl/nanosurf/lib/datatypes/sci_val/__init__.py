"""scientific value library formats and parse nice looking number strings into float numbers
    It handles units and exponent characters e.g. A string "2.45223kg" result in a float number 2452.23 and unit 'g'
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import math
import sys
import platform

import nanosurf.lib.datatypes.sci_val.unit_prefix as up
import nanosurf.lib.datatypes.sci_val.convert as convert

if platform.system() == "Windows":
    from nanosurf.lib.spm.studio.wrapper import CmdTreeProp
else:
    class CmdTreeProp():
        pass


class SciVal:
    def __init__(self, value = 0.0, unit_str: str = ""):
        if isinstance(value, SciVal):
            self._value = value._value
            self._value_default = value._value_default
            self._value_min = value._value_min
            self._value_max = value._value_max
            self._unit = value._unit
            self._prefix_id = up.Prefix.auto_
            self._allowed_unit_prefixes = value._allowed_unit_prefixes
            self._is_real = value._is_real
        elif isinstance(value, CmdTreeProp):
                self._value = value.value
                self._value_default = value.value
                self._value_min = -sys.float_info.max
                self._value_max = sys.float_info.max
                self._unit = value.unit
                self._prefix_id = up.Prefix.auto_
                self._allowed_unit_prefixes = up.default_prefix_range
                self._is_real = True
        else:
            self._value = value
            self._value_default = value
            self._value_min = -sys.float_info.max
            self._value_max = sys.float_info.max
            self._unit = unit_str
            self._prefix_id = up.Prefix.auto_
            self._allowed_unit_prefixes = up.default_prefix_range
            self._is_real = True
          
    def set_prefix_id(self, prefix_id: up.Prefix):
        if (self.is_prefix_enabled(prefix_id) or (prefix_id == up.Prefix.auto_)):
            self._prefix_id = prefix_id

    def prefix_id(self) -> up.Prefix:
        return self._prefix_id    
    
    def prefix_id_to_str(self, prefix_id: up.Prefix) -> str:
        return up.prefix_id_to_string(prefix_id)

    def _change_value_by_prefix_id(self, new_prefix_id: up.Prefix, old_prefix_id: up.Prefix):
        if (new_prefix_id != self._prefix_id and self.can_have_prefix() and self.is_prefix_enabled(new_prefix_id)):
            exp_old_val = up.prefix_id_to_absolute_value(old_prefix_id)
            exp_new_val = up.prefix_id_to_absolute_value(new_prefix_id)
            self.set_value(self._value / exp_old_val * exp_new_val)

    def is_real(self) -> bool:
        return self._is_real

    def to_string(self, precision : int = 3):
        return convert.to_string(self._value, self._unit, precision, self._prefix_id, self._allowed_unit_prefixes)

    def to_string_formatted(self, prefix_id: up.Prefix, precision: int = 3):
        return convert.to_string(self._value, self._unit, precision, prefix_id, up.default_prefix_range)

    def allowed_prefixes(self) -> list[up.Prefix]:
        return self._allowed_unit_prefixes

    def is_prefix_enabled(self, prefix_id: up.Prefix) -> bool:
        return prefix_id in self._allowed_unit_prefixes
        
    def can_have_prefix(self) -> bool:
        no_prefix = (self._unit=="") or (self._unit=="%") or (self._unit=="°") or (self._unit=="°C")
        return not(no_prefix)

    def unit(self) -> str:
        return self._unit

    def value(self) -> float:
        return self._value

    def value_min(self) -> float:
        return self._value_min

    def value_max(self) -> float:
        return self._value_max

    def value_default(self) -> float:
        return self._value_default

    def set_unit(self, unit_str: str):
        self._unit = unit_str

    def set_value(self, val: float):
        self._value = min(max(self._value_min, val), self._value_max)
        self._value = self._round_if_integral(self._value)
        # self._value = self._make_odd_if_step_odd1(self._value)
        
    def set_value_min(self, val: float):
        self._value_min = self._round_if_integral(val)
        self.set_value(self._value)

    def set_value_max(self, val: float):
        self._value_max = self._round_if_integral(val)
        self.set_value(self._value)

    def set_value_default(self, val: float):
        self._value_default = self._round_if_integral(val)

    def set_is_real(self, is_real:bool):
        self._is_real = is_real
        
    def set_allowed_prefixes(self, allowed_prefix_ids: list[up.Prefix]):
        self._allowed_unit_prefixes = allowed_prefix_ids

    def from_string(self, value_str) -> bool:
        value_changed = False
        res = convert.to_value(value_str, self._unit, self._prefix_id) 
        if res.success:
            value_changed = (self._value != res.value)
            self.set_value(res.value)
            if self._prefix_id == up.Prefix.auto_:
                self._prefix_id = res.prefix_id
        return value_changed

    def reset_to_default_value(self):
        self.set_value(self._value_default)
        self._prefix_id = up.Prefix.auto_

    # local methods ---------------------------------------------------

    def _create_result_object(self, new_value: float, other):
        if isinstance(other, SciVal):
            res = SciVal(self)
            res.set_value(new_value)
            return res
        return new_value

    def _get_value_from(self, other):
        if isinstance(other, SciVal):
            return other.value()
        return other

    def _round_if_integral(self, val:float) -> float:
        if self._is_real:
            return val
        return float(math.floor(val+0.5))

    # overwrite magic conversion and math functions ----------------------------------

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return self._value

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def __add__(self, other):
        return self._create_result_object(self._value + self._get_value_from(other), other)   
              
    def __sub__(self, other):
        return self._create_result_object(self._value - self._get_value_from(other), other)   
              
    def __mul__(self, other):
        return self._create_result_object(self._value * self._get_value_from(other), other)   
              
    def __truediv__(self, other):
        return self._create_result_object(self._value / self._get_value_from(other), other)   

    def __floordiv__(self, other):
        return self._create_result_object(self._value // self._get_value_from(other), other)   

    def __mod__(self, other):
        return self._create_result_object(self._value % self._get_value_from(other), other)   
              
    def __pow__(self, other):
        return self._create_result_object(math.pow(self._value / self._get_value_from(other)), other)   

    def __lt__(self, other):
        return self._value < self._get_value_from(other)
              
    def __gt__(self, other):
        return self._value > self._get_value_from(other)
              
    def __le__(self, other):
        return self._value <= self._get_value_from(other)
              
    def __ge__(self, other):
        return self._value >= self._get_value_from(other)
              
    def __eq__(self, other):
        return self._value == self._get_value_from(other)
              
    def __ne__(self, other):
        return self._value != self._get_value_from(other)
              
    def __iadd__(self, other):
        self._value += self._get_value_from(other)
              
    def __isub__(self, other):
        self._value -= self._get_value_from(other)
              
    def __imul__(self, other):
        self._value *= self._get_value_from(other)
              
    def __idiv__(self, other):
        self._value /= self._get_value_from(other)
              
    def __imod__(self, other):
        self._value %= self._get_value_from(other)
              
    def __neg__(self):
        return self._create_result_object(-self._value)   
              
    def __pos__(self):
        return self._create_result_object(+self._value)   
              
def from_str(val_str: str)-> SciVal:
    res = convert.to_value(val_str, current_unit="", use_current_unit=False)
    if res.success:
        return SciVal(value=res.value, unit_str=res.unit)
    return SciVal()

