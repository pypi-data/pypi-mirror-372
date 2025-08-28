# coding: utf-8
from typing import Any

class UtilCopy:
    _max_depth = 100  # 安全な再帰深度上限

    @staticmethod
    def jsonable_deep_copy(value: Any, depth: int = 0) -> Any:
        """
        JSON互換型のみを再帰的にディープコピーします。
        非対応の型や再帰深度超過は ValueError を投げます。

        Args:
            value: コピー対象
            depth: 内部用の再帰深度カウンタ（外部から設定不要）

        Returns:
            コピーされたオブジェクト
        """
        if depth > UtilCopy._max_depth:
            raise ValueError(f'Exceeded max allowed nesting depth ({UtilCopy._max_depth})')

        if isinstance(value, dict):
            return {k: UtilCopy.jsonable_deep_copy(v, depth=depth+1) for k, v in value.items()}
        elif isinstance(value, list):
            return [UtilCopy.jsonable_deep_copy(v, depth=depth+1) for v in value]
        elif isinstance(value, (str, int, float, bool)) or value is None:
            return value
        else:
            raise ValueError(f'Unsupported type for JSON deep copy: {type(value)}')
