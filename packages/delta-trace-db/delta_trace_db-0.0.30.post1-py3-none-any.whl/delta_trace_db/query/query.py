# coding: utf-8
from typing import Any, Dict, List, Optional
from delta_trace_db.query.enum_query_type import EnumQueryType
from delta_trace_db.query.nodes.query_node import QueryNode
from delta_trace_db.query.sort.abstract_sort import AbstractSort
from delta_trace_db.query.cause.cause import Cause
from delta_trace_db.db.util_copy import UtilCopy


class Query:
    className: str = "Query"
    version: str = "5"

    def __init__(
            self,
            target: str,
            type_: EnumQueryType,
            add_data: Optional[List[Dict[str, Any]]] = None,
            override_data: Optional[Dict[str, Any]] = None,
            template: Optional[Dict[str, Any]] = None,
            query_node: Optional[QueryNode] = None,
            sort_obj: Optional[AbstractSort] = None,
            offset: Optional[int] = None,
            start_after: Optional[Dict[str, Any]] = None,
            end_before: Optional[Dict[str, Any]] = None,
            rename_before: Optional[str] = None,
            rename_after: Optional[str] = None,
            limit: Optional[int] = None,
            return_data: bool = False,
            must_affect_at_least_one: bool = True,
            serial_key: Optional[str] = None,
            reset_serial: bool = False,
            cause: Optional[Cause] = None,
    ):
        self.target = target
        self.type = type_
        self.add_data = add_data
        self.override_data = override_data
        self.template = template
        self.query_node = query_node
        self.sort_obj = sort_obj
        self.offset = offset
        self.start_after = start_after
        self.end_before = end_before
        self.rename_before = rename_before
        self.rename_after = rename_after
        self.limit = limit
        self.return_data = return_data
        self.must_affect_at_least_one = must_affect_at_least_one
        self.serial_key = serial_key
        self.reset_serial = reset_serial
        self.cause = cause

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "Query":
        return cls(
            target=src["target"],
            type_=EnumQueryType[src["type"]],
            add_data=src.get("addData"),
            override_data=src.get("overrideData"),
            template=src.get("template"),
            query_node=QueryNode.from_dict(src["queryNode"])
            if src.get("queryNode")
            else None,
            sort_obj=AbstractSort.from_dict(src["sortObj"])
            if src.get("sortObj")
            else None,
            offset=src.get("offset"),
            start_after=src.get("startAfter"),
            end_before=src.get("endBefore"),
            rename_before=src.get("renameBefore"),
            rename_after=src.get("renameAfter"),
            limit=src.get("limit"),
            return_data=src.get("returnData", False),
            must_affect_at_least_one=src.get("mustAffectAtLeastOne", True),
            serial_key=src.get("serialKey", None),
            reset_serial=src.get("resetSerial", False),
            cause=Cause.from_dict(src["cause"]) if src.get("cause") else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "className": self.className,
            "version": self.version,
            "target": self.target,
            "type": self.type.name,
            "addData": (
                [dict(UtilCopy.jsonable_deep_copy(d)) for d in self.add_data]
                if self.add_data is not None
                else None
            ),
            "overrideData": UtilCopy.jsonable_deep_copy(self.override_data),
            "template": UtilCopy.jsonable_deep_copy(self.template),
            "queryNode": self.query_node.to_dict() if self.query_node else None,
            "sortObj": self.sort_obj.to_dict() if self.sort_obj else None,
            "offset": self.offset,
            "startAfter": UtilCopy.jsonable_deep_copy(self.start_after),
            "endBefore": UtilCopy.jsonable_deep_copy(self.end_before),
            "renameBefore": self.rename_before,
            "renameAfter": self.rename_after,
            "limit": self.limit,
            "returnData": self.return_data,
            "mustAffectAtLeastOne": self.must_affect_at_least_one,
            "serialKey": self.serial_key,
            "resetSerial": self.reset_serial,
            "cause": self.cause.to_dict() if self.cause else None,
        }

    def clone(self) -> "Query":
        return Query.from_dict(self.to_dict())
