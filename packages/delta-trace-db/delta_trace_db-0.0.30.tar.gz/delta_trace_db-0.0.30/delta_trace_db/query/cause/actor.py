from typing import Any, Dict, List, Optional

from file_state_manager.util_object_hash import UtilObjectHash

from delta_trace_db.db.util_copy import UtilCopy
from delta_trace_db.query.cause.enum_actor_type import EnumActorType
from delta_trace_db.query.cause.permission import Permission


# 深いコレクション比較（Dart の DeepCollectionEquality 相当）
def deep_collection_equals(a: Any, b: Any) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        return all(deep_collection_equals(a[k], b[k]) for k in a)
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        if len(a) != len(b):
            return False
        return all(deep_collection_equals(x, y) for x, y in zip(a, b))
    else:
        return a == b


class Actor:
    className = "Actor"
    version = "3"

    def __init__(
            self,
            actor_type: EnumActorType,
            actor_id: str,
            roles: List[str],
            permissions: List[str],
            collection_permissions: Optional[Dict[str, Permission]] = None,
            context: Optional[Dict[str, Any]] = None,
    ):
        self.actor_type = actor_type
        self.actor_id = actor_id
        self.roles = roles
        self.permissions = permissions
        self.collection_permissions = collection_permissions
        self.context = context

    @classmethod
    def from_dict(cls, src: Dict[str, Any]) -> "Actor":
        m_collection_permissions: Optional[Dict[str, Dict[str, Any]]] = None
        if src.get("collectionPermissions") is not None:
            m_collection_permissions = {
                k: v for k, v in src["collectionPermissions"].items()
            }

        collection_permissions: Optional[Dict[str, Permission]] = None
        if m_collection_permissions is not None:
            collection_permissions = {
                key: Permission.from_dict(value)
                for key, value in m_collection_permissions.items()
            }

        return cls(
            actor_type=EnumActorType[src["type"]],
            actor_id=src["id"],
            roles=list(src.get("roles", [])),
            permissions=list(src.get("permissions", [])),
            collection_permissions=collection_permissions,
            context=src.get("context"),
        )

    def clone(self) -> "Actor":
        return Actor.from_dict(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        m_collection_permissions: Optional[Dict[str, Dict[str, Any]]] = None
        if self.collection_permissions is not None:
            m_collection_permissions = {
                key: value.to_dict()
                for key, value in self.collection_permissions.items()
            }

        return {
            "className": self.className,
            "version": self.version,
            "type": self.actor_type.name,
            "id": self.actor_id,
            "roles": self.roles,
            "permissions": self.permissions,
            "collectionPermissions": m_collection_permissions,
            "context": UtilCopy.jsonable_deep_copy(self.context),
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Actor):
            return False
        return (
                self.actor_type == other.actor_type
                and self.actor_id == other.actor_id
                and self.roles == other.roles  # 順序あり比較
                and self.permissions == other.permissions  # 順序あり比較
                and deep_collection_equals(
            self.collection_permissions, other.collection_permissions
        )
                and deep_collection_equals(self.context, other.context)
        )

    def __hash__(self) -> int:
        return hash((
            self.actor_type,
            self.actor_id,
            UtilObjectHash.calc_list(self.roles),
            UtilObjectHash.calc_list(self.permissions),
            UtilObjectHash.calc_map(self.context),
        ))
