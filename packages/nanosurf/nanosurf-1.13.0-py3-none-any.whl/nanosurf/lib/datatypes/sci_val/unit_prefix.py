"""scientific value library formats and parse nice looking number strings into float numbers
    It handles units and exponent characters e.g. A string "2.45223kg" result in a float number 2452.23 and unit 'g'
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum

class Prefix(enum.IntEnum):
    yotta =  0,
    zetta =  1,
    exa   =  2,
    peta  =  3,
    tera  =  4,
    giga  =  5,
    mega  =  6,
    kilo  =  7,
    base  =  8,
    milli =  9,
    micro = 10,
    nano  = 11,
    pico  = 12,
    femto = 13,
    atto  = 14,
    zepto = 15,
    yocto = 16,
    auto_ = 17,

  # Full range of prefixes, used as default for sci_val and sci_val_formatter
default_prefix_range = [
    Prefix.yotta,
    Prefix.zetta,
    Prefix.exa,
    Prefix.peta,
    Prefix.tera,
    Prefix.giga,
    Prefix.mega,
    Prefix.kilo,
    Prefix.base,
    Prefix.milli,
    Prefix.micro,
    Prefix.nano,
    Prefix.pico,
    Prefix.femto,
    Prefix.atto,
    Prefix.zepto,
    Prefix.yocto
]


prefix_max_exp_value = +24
prefix_min_exp_value = -24

_prefix_symbols = [
    ["Y","Yotta", 24, 1000000000000000000000000.0],
    ["Z","Zetta", 21,    1000000000000000000000.0],
    ["E", "Exa",  18,       1000000000000000000.0],
    ["P", "Peta", 15,          1000000000000000.0],
    ["T", "Tera", 12,             1000000000000.0],
    ["G", "Giga",  9,                1000000000.0],
    ["M", "Mega",  6,                   1000000.0],
    ["k", "kilo",  3,                      1000.0],
    [ "", "",      0,                         1.0],
    ["m", "milli",-3,                           0.001],
    ["µ", "micro",-6,                           0.000001],
    ["n", "nano", -9,                           0.000000001],
    ["p", "pico", -12,                          0.000000000001],
    ["f", "femto",-15,                          0.00000000000001],
    ["a", "atta", -18,                          0.00000000000000001],
    ["z", "zepto",-21,                          0.00000000000000000001],
    ["y", "yocto",-24,                          0.00000000000000000000001],
    ["",  "auto",   0,                        1.0]
]

class _PrefixSympolID(enum.IntEnum):
    Symbol = 0,
    Name = 1,
    ExpValue = 2,
    AbsValue = 3

def string_prefix_to_prefix_id(prefix_str: str) -> Prefix:
    if prefix_str == "u":
        return Prefix.micro

    for index,p in enumerate(_prefix_symbols):
        if p[_PrefixSympolID.Symbol] == prefix_str:
            prefix_index = index   
            return default_prefix_range[prefix_index]
    return Prefix.base

def is_prefix_str_valid(prefix_str:str) -> bool:
    if prefix_str == "u":
        return True
        
    for p in _prefix_symbols:
        if p[_PrefixSympolID.Symbol] == prefix_str:
            return True   
    return False

def prefix_id_to_string(prefix_id: Prefix):
    return _prefix_symbols[int(prefix_id)][_PrefixSympolID.Symbol] 

def prefix_value_to_string(exponent_value):
    expstr = _prefix_symbols[Prefix.auto_][_PrefixSympolID.Symbol] 
    for p in _prefix_symbols:
        if p[_PrefixSympolID.ExpValue] == exponent_value:
            return p[_PrefixSympolID.Symbol]   
    return expstr

def prefix_id_to_exponent_value(prefix_id:Prefix):
    return _prefix_symbols[prefix_id][_PrefixSympolID.ExpValue] 

def prefix_id_to_absolute_value(prefix_id:Prefix):
    return _prefix_symbols[prefix_id][_PrefixSympolID.AbsValue] 

def prefix_value_to_prefix_id(exp_value):
    prefix_id = Prefix.base
    for index,p in enumerate(_prefix_symbols):
        if p[_PrefixSympolID.ExpValue] == exp_value:
            prefix_id = index   
    return prefix_id


def next_smaller_prefix_id(prefix_id:Prefix):
    if (prefix_id == Prefix.auto_) or (prefix_id == Prefix.yocto):
        return prefix_id
    else:
        for index,p in enumerate(default_prefix_range):
            if p == prefix_id:
                return default_prefix_range[index + 1]
    return  prefix_id           
    

