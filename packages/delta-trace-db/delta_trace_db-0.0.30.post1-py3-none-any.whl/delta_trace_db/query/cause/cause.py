# coding: utf-8
from typing import Optional, Dict, Any
from file_state_manager.cloneable_file import CloneableFile
from delta_trace_db.db.util_copy import UtilCopy
from delta_trace_db.query.cause.actor import Actor
from delta_trace_db.query.cause.temporal_trace.temporal_trace import TemporalTrace


class Cause(CloneableFile):
    class_name = "Cause"
    version = "1"

    def __init__(self, who: Actor, when: TemporalTrace, what: str, why: str, from_: str, serial: Optional[str] = None,
                 chain_parent_serial: Optional[str] = None, context: Optional[Dict[str, Any]] = None,
                 confidence_score: float = 1.0):
        super().__init__()
        self.serial = serial
        self.chain_parent_serial = chain_parent_serial
        self.who = who
        self.when = when
        self.what = what
        self.why = why
        self.from_ = from_
        self.context = context
        self.confidence_score = confidence_score

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "Cause":
        return cls(
            serial=src.get("serial"),
            chain_parent_serial=src.get("chainParentSerial"),
            who=Actor.from_dict(src["who"]),
            when=TemporalTrace.from_dict(src["when"]),
            what=src["what"],
            why=src["why"],
            from_=src["from"],
            context=src.get("context"),
            confidence_score=src.get("confidenceScore", 1.0),
        )

    def clone(self) -> "Cause":
        return Cause.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "className": self.class_name,
            "version": self.version,
            "serial": self.serial,
            "chainParentSerial": self.chain_parent_serial,
            "who": self.who.to_dict(),
            "when": self.when.to_dict(),
            "what": self.what,
            "why": self.why,
            "from": self.from_,
            "context": UtilCopy.jsonable_deep_copy(self.context),
            "confidenceScore": self.confidence_score,
        }
