# coding: utf-8
from enum import Enum

class EnumQueryType(Enum):
    """
    (en) An enum that defines the type of query.

    (ja) クエリの種類を定義したEnum。
    """
    add = "add"
    update = "update"
    updateOne = "updateOne"
    delete = "delete"
    deleteOne = "deleteOne"
    search = "search"
    getAll = "getAll"
    conformToTemplate = "conformToTemplate"  # DB shape change.
    renameField = "renameField"  # DB field name change.
    count = "count"  # get all items count.
    clear = "clear"  # delete all items.
    clearAdd = "clearAdd"  # clear then add.
