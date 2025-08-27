# coding: utf-8
from enum import Enum

class EnumValueType(Enum):
    auto_ = "auto_"              # default
    datetime_ = "datetime_"
    int_ = "int_"
    floatStrict_ = "floatStrict_"
    floatEpsilon12_ = "floatEpsilon12_"  # Tolerance 1e-12
    boolean_ = "boolean_"
    string_ = "string_"
