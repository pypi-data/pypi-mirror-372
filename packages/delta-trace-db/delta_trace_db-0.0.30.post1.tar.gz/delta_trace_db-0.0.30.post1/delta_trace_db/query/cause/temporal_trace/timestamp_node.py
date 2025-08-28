# coding: utf-8
from datetime import datetime, timezone
from typing import Dict, Any
from file_state_manager.cloneable_file import CloneableFile
from delta_trace_db.db.util_copy import UtilCopy

def to_utc_iso(dt: datetime) -> str:
    """
    Dart の timestamp.toUtc().toIso8601String() と同じ挙動で
    UTC ISO8601 文字列に変換する関数。

    - aware datetime（タイムゾーン付き）の場合は UTC に変換
    - naive datetime（タイムゾーンなし）の場合は UTC として扱う
    """
    if dt.tzinfo is None:
        # naive datetime → UTC として扱う
        dt_utc = dt.replace(tzinfo=timezone.utc)
    else:
        # aware datetime → UTC に変換
        dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.isoformat()

class TimestampNode(CloneableFile):
    """軌跡上の各チェックポイントを表すノード。"""

    class_name = "TimestampNode"
    version = "1.post1"

    def __init__(self, timestamp: datetime, location: str, context: Dict[str, Any] = None):
        super().__init__()
        self.timestamp: datetime = timestamp
        self.location: str = location
        self.context: Dict[str, Any] = context if context is not None else {}

    @classmethod
    def from_dict(cls, src: Dict[str, Any]):
        return cls(
            timestamp=datetime.fromisoformat(src["timestamp"]),
            location=src["location"],
            context=src.get("context", {}),
        )

    def clone(self):
        return TimestampNode.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "className": self.class_name,
            "version": self.version,
            "timestamp": to_utc_iso(dt=self.timestamp),
            "location": self.location,
            "context": UtilCopy.jsonable_deep_copy(self.context),
        }
