# coding: utf-8
from typing import Any, Callable, Dict
from datetime import datetime

from delta_trace_db.query.nodes.enum_value_type import EnumValueType
from delta_trace_db.query.sort.abstract_sort import AbstractSort
from delta_trace_db.query.util_field import UtilField


class SingleSort(AbstractSort):
    """Single-key sorting for query results.

    (ja) クエリの戻り値について、単一キーでのソートを指定するためのクラスです。
    """

    class_name = "SingleSort"
    version = "3"

    def __init__(self, field: str, reversed_: bool = False, v_type: EnumValueType = EnumValueType.auto_):
        self.field = field
        self.reversed = reversed_
        self.v_type = v_type

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "SingleSort":
        field = src["field"]
        is_reversed = src.get("reversed", False)
        try:
            v_type = EnumValueType[src.get("vType", "auto_")]
        except KeyError:
            v_type = EnumValueType.auto_
        return cls(field=field, reversed_=is_reversed, v_type=v_type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "className": self.class_name,
            "version": self.version,
            "field": self.field,
            "reversed": self.reversed,
            "vType": self.v_type.name
        }

    def _convert_value(self, value):
        if value is None:
            return None
        match self.v_type:
            case EnumValueType.datetime_:
                if isinstance(value, datetime):
                    return value
                if isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value)
                    except ValueError:
                        raise Exception(f"Cannot convert {value} to datetime")
                raise Exception(f"Cannot convert {value} to datetime")
            case EnumValueType.int_:
                if isinstance(value, int):
                    return value
                if isinstance(value, float):
                    return int(value)
                if isinstance(value, str):
                    try:
                        return int(value)
                    except ValueError:
                        raise Exception(f"Cannot convert {value} to int")
                raise Exception(f"Cannot convert {value} to int")
            case EnumValueType.floatStrict_:
                if isinstance(value, float):
                    return value
                if isinstance(value, int):
                    return float(value)
                if isinstance(value, str):
                    try:
                        return float(value)
                    except ValueError:
                        raise Exception(f"Cannot convert {value} to float")
                raise Exception(f"Cannot convert {value} to float")
            case EnumValueType.floatEpsilon12_:
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, str):
                    try:
                        return float(value)
                    except ValueError:
                        raise Exception(f"Cannot convert {value} to float (epsilon)")
                raise Exception(f"Cannot convert {value} to float (epsilon)")
            case EnumValueType.boolean_:
                if isinstance(value, bool):
                    return value
                if isinstance(value, int):
                    return value != 0
                if isinstance(value, str):
                    lower = value.lower()
                    if lower in ['true', '1', 'yes', 'y']:
                        return True
                    if lower in ['false', '0', 'no', 'n']:
                        return False
                raise Exception(f"Cannot convert {value} to bool")
            case EnumValueType.string_:
                return str(value)
            case EnumValueType.auto_:
                return value
            case _:
                raise Exception(f"Unknown type: {self.v_type}")

    def get_comparator(self) -> Callable[[Dict[str, Any], Dict[str, Any]], int]:
        def comparator(a: Dict[str, Any], b: Dict[str, Any]) -> int:
            # 型変換
            a_value = self._convert_value(UtilField.get_nested_field_value(a, self.field))
            b_value = self._convert_value(UtilField.get_nested_field_value(b, self.field))
            # null値対応用の処理。
            if a_value is None and b_value is None:
                return 0
            if a_value is None:
                return -1 if self.reversed else 1
            if b_value is None:
                return 1 if self.reversed else -1
            # 比較用の計算。
            match self.v_type:
                case EnumValueType.floatEpsilon12_:
                    diff = float(a_value) - float(b_value)
                    if abs(diff) < 1e-12:
                        result = 0
                    else:
                        result = -1 if diff < 0 else 1
                case _:
                    if isinstance(a_value, bool) and isinstance(b_value, bool):
                        a_int = 1 if a_value else 0
                        b_int = 1 if b_value else 0
                        result = (a_int > b_int) - (a_int < b_int)
                    elif isinstance(a_value, (int, float, str)) and isinstance(b_value, (int, float, str)):
                        if type(a_value) != type(b_value):
                            raise Exception(
                                f'Incompatible types: {a_value} ({type(a_value).__name__}) vs {b_value} ({type(b_value).__name__})')
                        result = (a_value > b_value) - (a_value < b_value)
                    else:
                        raise Exception(
                            f'Field "{self.field}" not comparable: {a_value} ({type(a_value).__name__}), {b_value} ({type(b_value).__name__})')
            return -result if self.reversed else result

        return comparator
