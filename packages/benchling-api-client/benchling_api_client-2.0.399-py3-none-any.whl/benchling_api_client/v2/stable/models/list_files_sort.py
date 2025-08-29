from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListFilesSort(Enums.KnownString):
    MODIFIEDAT = "modifiedAt"
    NAME = "name"
    CREATEDAT = "createdAt"
    MODIFIEDATASC = "modifiedAt:asc"
    NAMEASC = "name:asc"
    CREATEDATASC = "createdAt:asc"
    MODIFIEDATDESC = "modifiedAt:desc"
    NAMEDESC = "name:desc"
    CREATEDATDESC = "createdAt:desc"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "ListFilesSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListFilesSort must be a string (encountered: {val})")
        newcls = Enum("ListFilesSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListFilesSort, getattr(newcls, "_UNKNOWN"))
