# coding: utf-8
from typing import Any, Dict, Optional

from delta_trace_db.query.cause.permission import Permission
from delta_trace_db.query.query import Query
from delta_trace_db.query.transaction_query import TransactionQuery


class UtilQuery:
    """
    (en) Utilities for query processing.
    (ja) クエリ処理用のユーティリティです。
    """

    @staticmethod
    def convert_from_json(src: Dict[str, Any]) -> Any:
        """
        (en) Restores a Query or TransactionQuery class from a JSON dict.
        (ja) JSONのdictから、QueryまたはTransactionQueryクラスを復元します。

        Args:
            src (Dict[str, Any]): The dict of Query or TransactionQuery class.

        Returns:
            Query | TransactionQuery

        Raises:
            ValueError: If you pass an incorrect class.
        """
        try:
            if src.get("className") == "Query":
                return Query.from_dict(src)
            elif src.get("className") == "TransactionQuery":
                return TransactionQuery.from_dict(src)
            else:
                raise ValueError(f"Unsupported query class: {src.get('className')}")
        except Exception:
            raise ValueError("Unsupported object")

    @staticmethod
    def check_permissions(q: Query, collection_permissions: Optional[Dict[str, Permission]]) -> bool:
        if collection_permissions is None:
            return True
        if q.target not in collection_permissions:
            return False

        # allowsのチェック
        p = collection_permissions[q.target]
        if q.type in p.allows:
            return True

        return False
