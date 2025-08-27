# coding: utf-8
from typing import Any, Dict

class UtilField:
    """
    (en) Utility for field access used in internal DB processing.
    (ja) DBの内部処理で利用する、フィールドアクセスに関するユーティリティです。
    """

    @staticmethod
    def get_nested_field_value(map_: Dict[str, Any], path: str) -> object | None:
        """
        (en) Access nested fields of a dictionary.
        (ja) 辞書の、ネストされたフィールドにアクセスするための関数です。

        Args:
            map_ (Dict[str, Any]): 探索したいマップ。
            path (str): "."区切りの探索用パス。例: "user.name"

        Returns:
            object | None: 見つかった値、または存在しなければ None
        """
        keys = path.split('.')
        current: object | None = map_
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
