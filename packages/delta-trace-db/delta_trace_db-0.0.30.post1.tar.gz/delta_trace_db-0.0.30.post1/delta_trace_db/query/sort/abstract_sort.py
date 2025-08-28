# coding: utf-8
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict


class AbstractSort(ABC):
    """Base class for sort objects.

    (en) Comparison function for sorting.
    (ja) ソート用の比較関数です。
    """

    @abstractmethod
    def get_comparator(self) -> Callable[[Dict[str, Any], Dict[str, Any]], int]:
        """Return a comparator function for sorting."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the object to a dictionary."""
        pass

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "AbstractSort":
        """Restore a sort object from a dictionary."""
        # 遅延インポート
        from delta_trace_db.query.sort.single_sort import SingleSort
        from delta_trace_db.query.sort.multi_sort import MultiSort
        class_name = src.get("className")
        if class_name == SingleSort.class_name:
            return SingleSort.from_dict(src)
        elif class_name == MultiSort.class_name:
            return MultiSort.from_dict(src)
        else:
            raise ValueError(f"Unknown sort class: {class_name}")
