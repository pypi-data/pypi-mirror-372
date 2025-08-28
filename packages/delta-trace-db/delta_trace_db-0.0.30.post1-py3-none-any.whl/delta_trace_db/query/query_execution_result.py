# coding: utf-8
from abc import ABC
from typing import Dict, Any

from file_state_manager.cloneable_file import CloneableFile


class QueryExecutionResult(CloneableFile, ABC):
    def __init__(self, is_success: bool):
        super().__init__()
        self.is_success: bool = is_success

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "QueryExecutionResult":
        # 遅延インポート
        from delta_trace_db.query.query_result import QueryResult
        from delta_trace_db.query.transaction_query_result import TransactionQueryResult
        class_name = src.get("className")
        if class_name == "QueryResult":
            return QueryResult.from_dict(src)
        elif class_name == "TransactionQueryResult":
            return TransactionQueryResult.from_dict(src)
        else:
            raise ValueError("QueryExecutionResult: The object cannot be converted.")
