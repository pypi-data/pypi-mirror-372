# coding: utf-8
from typing import Any, Dict, List, Set, Callable, Optional

from file_state_manager.cloneable_file import CloneableFile

from delta_trace_db.db.delta_trace_db_collection import Collection
from delta_trace_db.query.cause.permission import Permission
from delta_trace_db.query.enum_query_type import EnumQueryType
from delta_trace_db.query.query import Query
from delta_trace_db.query.query_execution_result import QueryExecutionResult
from delta_trace_db.query.query_result import QueryResult
from delta_trace_db.query.transaction_query import TransactionQuery
from delta_trace_db.query.transaction_query_result import TransactionQueryResult
from delta_trace_db.query.util_query import UtilQuery


class DeltaTraceDatabase(CloneableFile):
    class_name = "DeltaTraceDatabase"
    version = "9"

    def __init__(self):
        super().__init__()
        self._collections: Dict[str, Collection] = {}

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "DeltaTraceDatabase":
        instance = cls()
        instance._collections = cls._parse_collections(src)
        return instance

    @staticmethod
    def _parse_collections(src: Dict[str, Any]) -> Dict[str, Collection]:
        raw = src.get("collections")
        if not isinstance(raw, dict):
            raise ValueError("Invalid format: 'collections' should be a dict")
        result: Dict[str, Collection] = {}
        for key, value in raw.items():
            if not isinstance(value, dict):
                raise ValueError(f"Invalid format: value of collection '{key}' is not a dict")
            result[key] = Collection.from_dict(value)
        return result

    def collection(self, name: str) -> Collection:
        if name in self._collections:
            return self._collections[name]
        col = Collection()
        self._collections[name] = col
        return col

    def collection_to_dict(self, name: str) -> Dict[str, Any]:
        return self._collections.get(name).to_dict() if name in self._collections else {}

    def collection_from_dict(self, name: str, src: Dict[str, Any]) -> Collection:
        col = Collection.from_dict(src)
        self._collections[name] = col
        return col

    def collection_from_dict_keep_listener(self, name: str, src: Dict[str, Any]) -> Collection:
        col = Collection.from_dict(src)
        listeners_buf: Set[Callable[[], None]] = self._collections.get(
            name).listeners if name in self._collections else set()
        self._collections[name] = col
        if listeners_buf:
            self._collections[name].listeners = listeners_buf
        return col

    def clone(self) -> "DeltaTraceDatabase":
        return DeltaTraceDatabase.from_dict(self.to_dict())

    @property
    def raw(self) -> Dict[str, Collection]:
        return self._collections

    def to_dict(self) -> Dict[str, Any]:
        return {
            "className": self.class_name,
            "version": self.version,
            "collections": {k: v.to_dict() for k, v in self._collections.items()},
        }

    def add_listener(self, target: str, cb: Callable[[], None]):
        self.collection(target).add_listener(cb)

    def remove_listener(self, target: str, cb: Callable[[], None]):
        self.collection(target).remove_listener(cb)

    def execute_query_object(self, query: Any,
                             collection_permissions: Optional[Dict[str, Permission]] = None) -> QueryExecutionResult:
        if isinstance(query, Query):
            return self.execute_query(query, collection_permissions=collection_permissions)
        elif isinstance(query, TransactionQuery):
            return self.execute_transaction_query(query, collection_permissions=collection_permissions)
        elif isinstance(query, dict):
            if query.get("className") == "Query":
                return self.execute_query(Query.from_dict(query), collection_permissions=collection_permissions)
            elif query.get("className") == "TransactionQuery":
                return self.execute_transaction_query(TransactionQuery.from_dict(query),
                                                      collection_permissions=collection_permissions)
            else:
                raise ValueError(f"Unsupported query class: {query.get('className')}")
        else:
            raise ValueError(f"Unsupported query type: {type(query)}")

    def execute_query(self, q: Query, collection_permissions: Optional[Dict[str, Permission]] = None) -> QueryResult:
        # パーミッションのチェック
        if not UtilQuery.check_permissions(q=q, collection_permissions=collection_permissions):
            return QueryResult(
                is_success=False,
                type_=q.type,
                result=[],
                db_length=-1,
                update_count=0,
                hit_count=0,
                error_message="Operation not permitted."
            )
        col = self.collection(q.target)
        try:
            match q.type:
                case EnumQueryType.add:
                    r = col.add_all(q)
                case EnumQueryType.update:
                    r = col.update(q, is_single_target=False)
                case EnumQueryType.updateOne:
                    r = col.update(q, is_single_target=True)
                case EnumQueryType.delete:
                    r = col.delete(q)
                case EnumQueryType.deleteOne:
                    r = col.delete_one(q)
                case EnumQueryType.search:
                    r = col.search(q)
                case EnumQueryType.getAll:
                    r = col.get_all(q)
                case EnumQueryType.conformToTemplate:
                    r = col.conform_to_template(q)
                case EnumQueryType.renameField:
                    r = col.rename_field(q)
                case EnumQueryType.count:
                    r = col.count(q)
                case EnumQueryType.clear:
                    r = col.clear(q)
                case EnumQueryType.clearAdd:
                    r = col.clear_add(q)
            # must_affect_at_least_oneの判定。
            if q.type in (
                    EnumQueryType.add,
                    EnumQueryType.update,
                    EnumQueryType.updateOne,
                    EnumQueryType.delete,
                    EnumQueryType.deleteOne,
                    EnumQueryType.conformToTemplate,
                    EnumQueryType.renameField,
                    EnumQueryType.clear,
                    EnumQueryType.clearAdd,
            ):
                if q.must_affect_at_least_one and r.update_count == 0:
                    return QueryResult(
                        is_success=False,
                        type_=q.type,
                        result=[],
                        db_length=len(col.raw),
                        update_count=0,
                        hit_count=r.hit_count,
                        error_message="No data matched the condition (mustAffectAtLeastOne=True)"
                    )
            return r
        except Exception as e:
            print(f"{self.class_name},execute_query: {e}")
            return QueryResult(
                is_success=False,
                type_=q.type,
                result=[],
                db_length=len(col.raw),
                update_count=-1,
                hit_count=-1,
                error_message=str(e)
            )

    def execute_transaction_query(self, q: TransactionQuery,
                                  collection_permissions: Optional[
                                      Dict[str, Permission]] = None) -> TransactionQueryResult:
        results: List[QueryResult] = []
        try:
            buff: Dict[str, Dict[str, Any]] = {}
            for i in q.queries:
                if i.target not in buff:
                    buff[i.target] = self.collection_to_dict(i.target)
                    self.collection(i.target).change_transaction_mode(True)
            try:
                for i in q.queries:
                    results.append(self.execute_query(i, collection_permissions=collection_permissions))
            except Exception:
                for key, val in buff.items():
                    self.collection_from_dict_keep_listener(key, val)
                    self.collection(key).change_transaction_mode(False)
                print(f"{self.class_name},execute_transaction_query: Transaction failed")
                return TransactionQueryResult(is_success=False, results=[], error_message="Transaction failed")

            # rollback if any query failed
            if any(not r.is_success for r in results):
                for key, val in buff.items():
                    self.collection_from_dict_keep_listener(key, val)
                    self.collection(key).change_transaction_mode(False)
                print(f"{self.class_name},execute_transaction_query: Transaction failed")
                return TransactionQueryResult(is_success=False, results=[], error_message="Transaction failed")

            # commit: notify listeners
            for key in buff.keys():
                col = self.collection(key)
                need_callback = getattr(col, "run_notify_listeners_in_transaction", False)
                col.change_transaction_mode(False)
                if need_callback:
                    col.notify_listeners()
            return TransactionQueryResult(is_success=True, results=results)
        except Exception as e:
            print(f"{self.class_name},execute_transaction_query: {e}")
            return TransactionQueryResult(is_success=False, results=[], error_message="Unexpected Error")
