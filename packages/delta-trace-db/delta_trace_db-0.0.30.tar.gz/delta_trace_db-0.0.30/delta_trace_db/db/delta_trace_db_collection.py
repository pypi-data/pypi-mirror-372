# coding: utf-8
import functools
from typing import Any, Callable, Dict, List, Set
from file_state_manager.cloneable_file import CloneableFile
from delta_trace_db.db.util_copy import UtilCopy
from delta_trace_db.query.nodes.query_node import QueryNode
from delta_trace_db.query.query import Query
from delta_trace_db.query.query_result import QueryResult


class Collection(CloneableFile):
    class_name = "Collection"
    version = "10"

    def __init__(self):
        super().__init__()
        self._data: List[Dict[str, Any]] = []
        self._serial_num: int = 0
        self.listeners: Set[Callable[[], None]] = set()
        self._is_transaction_mode: bool = False
        self.run_notify_listeners_in_transaction: bool = False

    def change_transaction_mode(self, is_transaction_mode: bool):
        self._is_transaction_mode = is_transaction_mode
        self.run_notify_listeners_in_transaction = False

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "Collection":
        instance = cls()
        instance._data = UtilCopy.jsonable_deep_copy(src.get("data", []))
        instance._serial_num = src.get("serialNum", 0)
        return instance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "className": self.class_name,
            "version": self.version,
            "data": UtilCopy.jsonable_deep_copy(self._data),
            "serialNum": self._serial_num
        }

    def clone(self) -> "Collection":
        return Collection.from_dict(self.to_dict())

    @property
    def raw(self) -> List[Dict[str, Any]]:
        return self._data

    @property
    def length(self) -> int:
        return len(self._data)

    def add_listener(self, cb: Callable[[], None]):
        self.listeners.add(cb)

    def remove_listener(self, cb: Callable[[], None]):
        self.listeners.discard(cb)

    def notify_listeners(self):
        if not self._is_transaction_mode:
            for cb in self.listeners:
                cb()
        else:
            self.run_notify_listeners_in_transaction = True

    def _evaluate(self, record: Dict[str, Any], node: QueryNode) -> bool:
        return node.evaluate(record)

    def add_all(self, q: Query) -> QueryResult:
        add_data = UtilCopy.jsonable_deep_copy(q.add_data)
        added_items = []
        if q.serial_key is not None:
            # 対象キーの存在チェック
            for item in add_data:
                if q.serial_key not in item:
                    return QueryResult(
                        is_success=False,
                        type_=q.type,
                        result=[],
                        db_length=len(self._data),
                        update_count=0,
                        hit_count=0,
                        error_message=f'The target serialKey does not exist. serialKey:{q.serial_key}',
                    )

            for item in add_data:
                serial_num = self._serial_num
                item[q.serial_key] = serial_num
                self._serial_num += 1
                self._data.append(item)
                if q.return_data:
                    added_items.append(item)
        else:
            self._data.extend(add_data)
            if q.return_data:
                added_items.extend(add_data)
        self.notify_listeners()
        return QueryResult(True, q.type, UtilCopy.jsonable_deep_copy(added_items), len(self._data), len(add_data), 0)

    def update(self, q: Query, is_single_target: bool) -> QueryResult:
        if q.return_data:
            r = []
            for item in self._data:
                if self._evaluate(item, q.query_node):
                    item.update(UtilCopy.jsonable_deep_copy(q.override_data))
                    r.append(item)
                    if is_single_target:
                        break
            if r:
                # 要素が空ではないなら通知を発行。
                self.notify_listeners()
            return QueryResult(True, q.type, UtilCopy.jsonable_deep_copy(r), len(self._data), len(r), len(r))
        else:
            count = 0
            for item in self._data:
                if self._evaluate(item, q.query_node):
                    item.update(UtilCopy.jsonable_deep_copy(q.override_data))
                    count += 1
                    if is_single_target:
                        break
            if count > 0:
                self.notify_listeners()
            return QueryResult(True, q.type, [], len(self._data), count, count)

    def delete(self, q: Query) -> QueryResult:
        if q.return_data:
            deleted_items = [item for item in self._data if self._evaluate(item, q.query_node)]
            self._data = [item for item in self._data if not self._evaluate(item, q.query_node)]
            if deleted_items:
                self.notify_listeners()
            return QueryResult(True, q.type, UtilCopy.jsonable_deep_copy(deleted_items), len(self._data),
                               len(deleted_items),
                               len(deleted_items))
        else:
            count = sum(1 for item in self._data if self._evaluate(item, q.query_node))
            self._data = [item for item in self._data if not self._evaluate(item, q.query_node)]
            if count > 0:
                self.notify_listeners()
            return QueryResult(True, q.type, [], len(self._data), count, count)

    def delete_one(self, q: Query) -> QueryResult:
        deleted_items = []
        for i, item in enumerate(self._data):
            if self._evaluate(item, q.query_node):
                deleted_items.append(item)
                del self._data[i]
                break
        if deleted_items:
            self.notify_listeners()
        return QueryResult(True, q.type, UtilCopy.jsonable_deep_copy(deleted_items), len(self._data),
                           len(deleted_items),
                           len(deleted_items))

    def search(self, q: Query) -> QueryResult:
        r: List[Dict[str, Any]] = []
        # 検索
        for item in self._data:
            if self._evaluate(item, q.query_node):
                r.append(item)
        hit_count = len(r)
        # ソートやページングのオプション
        if q.sort_obj is not None:
            sorted_list = list(r)
            sorted_list.sort(key=functools.cmp_to_key(q.sort_obj.get_comparator()))
            r = sorted_list
            if q.offset is not None:
                if q.offset > 0:
                    r = r[q.offset:]
            else:
                if q.start_after is not None:
                    try:
                        index = r.index(q.start_after)
                        if index != -1 and index + 1 < len(r):
                            r = r[index + 1:]
                        elif index != -1 and index + 1 >= len(r):
                            r = []
                    except ValueError:
                        pass
                elif q.end_before is not None:
                    try:
                        index = r.index(q.end_before)
                        if index != -1:
                            r = r[:index]
                    except ValueError:
                        pass
        if q.limit is not None:
            if q.offset is None and q.start_after is None and q.end_before is not None:
                r = r[-q.limit:] if len(r) > q.limit else r
            else:
                r = r[:q.limit]
        return QueryResult(
            is_success=True,
            type_=q.type,
            result=UtilCopy.jsonable_deep_copy(r),
            db_length=len(self._data),
            update_count=0,
            hit_count=hit_count,
        )

    def get_all(self, q: Query) -> QueryResult:
        r = UtilCopy.jsonable_deep_copy(self._data)
        if q.sort_obj:
            r.sort(key=q.sort_obj.get_comparator())
        return QueryResult(True, q.type, r, len(self._data), 0, len(r))

    def conform_to_template(self, q: Query) -> QueryResult:
        for item in self._data:
            keys_to_remove = [k for k in item.keys() if k not in q.template]
            for k in keys_to_remove:
                item.pop(k)
            for k, v in q.template.items():
                if k not in item:
                    item[k] = UtilCopy.jsonable_deep_copy(v)
        self.notify_listeners()
        return QueryResult(True, q.type, [], len(self._data), len(self._data), len(self._data))

    def rename_field(self, q: Query) -> QueryResult:
        r = []
        for item in self._data:
            if q.rename_before not in item:
                return QueryResult(False, q.type, [], len(self._data), 0, 0,
                                   f'The target key does not exist. key:{q.rename_before}')
            if q.rename_after in item:
                return QueryResult(False, q.type, [], len(self._data), 0, 0,
                                   f'An existing key was specified as the new key. key:{q.rename_after}')
        update_count = 0
        for item in self._data:
            item[q.rename_after] = item[q.rename_before]
            del item[q.rename_before]
            update_count += 1
            if q.return_data:
                r.append(item)
        self.notify_listeners()
        return QueryResult(True, q.type, UtilCopy.jsonable_deep_copy(r), len(self._data), update_count, update_count)

    def count(self, q: Query) -> QueryResult:
        return QueryResult(True, q.type, [], len(self._data), 0, len(self._data))

    def clear(self, q: Query) -> QueryResult:
        pre_len = len(self._data)
        self._data.clear()
        if q.reset_serial:
            self._serial_num = 0
        self.notify_listeners()
        return QueryResult(True, q.type, [], 0, pre_len, pre_len)

    def clear_add(self, q: Query) -> QueryResult:
        pre_len = len(self._data)
        self._data.clear()
        if q.reset_serial:
            self._serial_num = 0
        added_items = []
        add_data = UtilCopy.jsonable_deep_copy(q.add_data)
        if q.serial_key is not None:
            # 対象キーの存在チェック
            for item in add_data:
                if q.serial_key not in item:
                    return QueryResult(
                        is_success=False,
                        type_=q.type,
                        result=[],
                        db_length=len(self._data),
                        update_count=0,
                        hit_count=0,
                        error_message=f'The target serialKey does not exist. serialKey:{q.serial_key}',
                    )

            for item in add_data:
                serial_num = self._serial_num
                item[q.serial_key] = serial_num
                self._serial_num += 1
                self._data.append(item)
                if q.return_data:
                    added_items.append(item)
        else:
            self._data.extend(add_data)
            if q.return_data:
                added_items.extend(add_data)
        self.notify_listeners()
        return QueryResult(True, q.type, UtilCopy.jsonable_deep_copy(added_items), len(self._data), pre_len, pre_len)
