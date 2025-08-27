"""scientific value library formats and parse nice looking number strings into float numbers
    It handles units and exponent characters e.g. A string "2.45223kg" result in a float number 2452.23 and unit 'g'
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import sys
import math
import re

import nanosurf.lib.datatypes.sci_val.unit_prefix as up

class Token:
    success = False,
    value = 0,
    unit = "",
    prefix_id = up.Prefix.base

def to_value(val_str: str, current_unit: str = "", current_prefix_id: up.Prefix = up.Prefix.auto_, use_current_unit: bool = False) -> Token:
    instance = SciValParser(val_str, current_unit, current_prefix_id, use_current_unit=use_current_unit)
    return instance.str_to_value()

def to_string(value: float, unit: str, precision : int = 3, prefix_id:up.Prefix = up.Prefix.auto_, allowed_prefix_ids: list[up.Prefix] = up.default_prefix_range):
    instance = SciValFormatter(value,precision, prefix_id,allowed_prefix_ids,unit)
    return instance.value_to_str()

class SciValFormatter:
    def __init__(self, value: float, precision: int, prefix_id: up.Prefix, allowed_prefix_ids: list[up.Prefix], unit_str: str):
        self._value = value
        self._precision = precision
        self._prefix_id = prefix_id
        self._allowed_prefix_ids = allowed_prefix_ids
        self._unit = unit_str
        self._config_formatter()
        
    def value_to_str(self):
        self._convert_value_to_string()
        self._append_unit()
        return self._result_string

    def _config_formatter(self):
        self._result_string = ""
        self._exponent_value = 0
        self._no_prefix = (self._unit == "%") or (self._unit == "") or (self._unit == "°")
        self._no_space = (self._unit == "%") or (self._unit == "°")
        self._is_negative = (self._value < 0.0)
        if self._no_prefix:
            self._prefix_id = up.Prefix.base

    def _convert_value_to_string(self):
        self._config_formatter()
        if self._is_value_on_limit():
            self._result_string = self._create_inf_string()
        else:
            self._format_with_prefix()
            self._limit_lower_and_upper_bounds()

    def _format_with_prefix(self):
        if self._prefix_id == up.Prefix.auto_:
            self._format_with_auto_prefix()
        else:
            self._format_with_fixed_prefix()

    def _format_with_auto_prefix(self):
        self._exponent_value  = self._calculate_exponent(self._value)   
        auto_prefix_id =  up.prefix_value_to_prefix_id(self._exponent_value)     
        exponent_absolute_value = up.prefix_id_to_absolute_value(auto_prefix_id)
        self._value /= exponent_absolute_value
        self._result_string = self._format(self._value, self._precision)
        bigger_than_epsilon = abs(self._value) > sys.float_info.epsilon
        if (self._value > -1.0) and (self._value < +1.0) and bigger_than_epsilon and (self._exponent_value >= (up.prefix_min_exp_value+3)):
            self._decrement_exponent()    
        self._switch_to_closest_allowed_prefix(up.prefix_value_to_prefix_id(self._exponent_value))            

    def _format_with_fixed_prefix(self):
        exponent_absolute_value = up.prefix_id_to_absolute_value(self._prefix_id)
        self._exponent_value  = up.prefix_id_to_exponent_value(self._prefix_id)
        self._value /= exponent_absolute_value
        self._result_string = self._format(self._value, self._precision)

    def _format(self, value, precision):
        format_str = "{val:."+str(precision)+"f}"
        return format_str.format(val= value)

    def _calculate_exponent(self, value):
        tmp_exponent = 1
        if value != 0.0:
            tmp_exponent = math.floor(math.log10(abs(value)))
            if (value > -1.0) and (value < +1.0):
               tmp_exponent += 1
        return int(int(tmp_exponent / 3) * 3)      

    def _decrement_exponent(self):
        self._value *= 1000.0
        self._exponent_value -= 3
        self._result_string = self._format(self._value, self._precision)

    def _increment_exponent(self):
        self._value /= 1000.0
        self._exponent_value += 3
        self._result_string = self._format(self._value, self._precision)

    def _switch_to_closest_allowed_prefix(self, start_prefix_id: up.Prefix):
        if start_prefix_id not in self._allowed_prefix_ids:
            diff = up.prefix_max_exp_value - up.prefix_min_exp_value
            new_prefix = up.Prefix.base
            for allowed_prefix_id in self._allowed_prefix_ids:
                if (abs(self._exponent_value - up.prefix_id_to_exponent_value(allowed_prefix_id))) < diff:
                    new_prefix_id = allowed_prefix_id
                    diff = abs(self._exponent_value - up.prefix_id_to_exponent_value(allowed_prefix_id))
            self._exponent_value = up.prefix_id_to_exponent_value(new_prefix_id)
            prev_prefix_factor = up.prefix_id_to_absolute_value(start_prefix_id)
            self._value = self._value * prev_prefix_factor / up.prefix_id_to_absolute_value(new_prefix_id)
            self._result_string = self._format(self._value, self._precision)

    def _limit_lower_and_upper_bounds(self):
        pass

    def _append_unit(self):
        if not self._no_space and not self._no_prefix:
            self._result_string += " "
        self._result_string += up.prefix_value_to_string(self._exponent_value)
        self._result_string += self._unit

    def _is_value_on_limit(self):
        limit = False
        limit = limit or math.isnan(self._value)
        limit = limit or math.isinf(self._value)
        return limit

    def _create_inf_string(self):
        if self._is_negative:
            return str(-math.inf)
        else:
            return str(math.inf)

class SciValParser:
    def __init__(self, val_str: str, current_unit: str, current_prefix_id: up.Prefix, use_current_unit: bool = True):
        self._str_value = val_str
        self._current_prefix_id = current_prefix_id
        self._current_unit = current_unit
        self._use_current_unit = use_current_unit
        self._string_regex = re.compile(r'(?:[\s]*)(?P<num>[-+]?[0-9]*\.?[0-9]*)(?:[\s]*)(?P<prefix>[\w]?)(?P<unit>[\w]*)')
        
    def str_to_value(self) -> Token:
        res = Token()
        res.success = False

        m = self._string_regex.match(self._str_value)
        if m:
            parsed_dict = m.groupdict()
            self._parsed_prefix =  parsed_dict['prefix']
            self._parsed_unit =  parsed_dict['unit']
     
            if self._need_parsed_prefix_unit_swap():
                t = self._parsed_prefix
                self._parsed_prefix = self._parsed_unit
                self._parsed_unit = t
            try:
                res.value = float(parsed_dict['num'])
                res.unit = self._parsed_unit
            except:
                res.value = 0.0
                res.unit = ""
            res.success = True

        if res.success:
            if self._use_current_unit == False:
                if not up.is_prefix_str_valid(self._parsed_prefix):
                    res.unit = self._parsed_prefix + self._parsed_unit     
                    prefix_id = up.Prefix.base
                else:
                    prefix_id = up.string_prefix_to_prefix_id(self._parsed_prefix)  
            elif self._use_no_prefix():
                prefix_id = up.Prefix.base
            elif self._used_parsed_prefix():
                prefix_id =  up.string_prefix_to_prefix_id(self._parsed_prefix)   
            elif self._use_current_prefix():
                prefix_id = self._current_prefix_id
            else:
                prefix_id = self._current_prefix_id
            res.prefix_id = prefix_id
            res.value *= up.prefix_id_to_absolute_value(res.prefix_id)
        return res

    def _need_parsed_prefix_unit_swap(self):
        if (self._parsed_prefix!="") and (self._parsed_unit==""): 
            return True
        return False

    def _use_no_prefix(self):
        if (self._current_unit == "") or (self._current_unit == "%") or (self._current_unit == "°") or (self._current_unit == "°C"):
            return True
        if (self._parsed_prefix!="") and (self._parsed_unit == "") and (self._parsed_prefix == self._current_unit) and (self._current_unit != up.prefix_id_to_string(self._current_prefix_id)):
            return True
        if (self._parsed_prefix + self._parsed_unit) == "px":
            return True
        return False

    def _used_parsed_prefix(self):
        if (self._parsed_unit == self._current_unit):
            return True
        parsed_combined = self._parsed_prefix + self._parsed_unit
        if (self._parsed_prefix!="") and (self._parsed_prefix != self._current_unit) and (parsed_combined != self._current_unit):
            return True
        return False

    def _use_current_prefix(self):
        if (self._parsed_prefix!="") and (self._parsed_unit == "") and (self._parsed_prefix == self._current_unit) and  (self._current_unit != up.prefix_id_to_string(self._current_prefix_id)):
            return True
        parsed_combined = self._parsed_prefix + self._parsed_unit
        if (self._parsed_prefix!="") and (self._parsed_unit != "") and (self._parsed_unit != self._current_unit) and (parsed_combined == self._current_unit):
            return True
        return False
