# coding: utf-8
from abc import ABC, abstractmethod
from typing import Any, Dict
from delta_trace_db.query.nodes.enum_node_type import EnumNodeType


class QueryNode(ABC):
    """Base class for query nodes.

    (en) Returns True if the object matches the calculation.
    (ja) 計算と一致するオブジェクトだった場合はTrueを返します。
    """

    @abstractmethod
    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate the node against a data dictionary."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary."""
        pass

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "QueryNode":
        """Restore a QueryNode object from a dictionary."""
        # 遅延インポート
        from delta_trace_db.query.nodes.logical_node import AndNode, OrNode, NotNode
        from delta_trace_db.query.nodes.comparison_node import FieldEquals, FieldNotEquals, FieldGreaterThan, \
            FieldLessThan, \
            FieldGreaterThanOrEqual, FieldLessThanOrEqual, FieldMatchesRegex, FieldContains, FieldStartsWith, \
            FieldEndsWith, \
            FieldIn, FieldNotIn
        node_type = EnumNodeType[src["type"]]
        match node_type:
            case EnumNodeType.and_:
                return AndNode.from_dict(src)
            case EnumNodeType.or_:
                return OrNode.from_dict(src)
            case EnumNodeType.not_:
                return NotNode.from_dict(src)
            case EnumNodeType.equals_:
                return FieldEquals.from_dict(src)
            case EnumNodeType.notEquals_:
                return FieldNotEquals.from_dict(src)
            case EnumNodeType.greaterThan_:
                return FieldGreaterThan.from_dict(src)
            case EnumNodeType.lessThan_:
                return FieldLessThan.from_dict(src)
            case EnumNodeType.greaterThanOrEqual_:
                return FieldGreaterThanOrEqual.from_dict(src)
            case EnumNodeType.lessThanOrEqual_:
                return FieldLessThanOrEqual.from_dict(src)
            case EnumNodeType.regex_:
                return FieldMatchesRegex.from_dict(src)
            case EnumNodeType.contains_:
                return FieldContains.from_dict(src)
            case EnumNodeType.in_:
                return FieldIn.from_dict(src)
            case EnumNodeType.notIn_:
                return FieldNotIn.from_dict(src)
            case EnumNodeType.startsWith_:
                return FieldStartsWith.from_dict(src)
            case EnumNodeType.endsWith_:
                return FieldEndsWith.from_dict(src)
