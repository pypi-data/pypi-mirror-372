from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class ListDatasetsSort(Enums.KnownString):
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
    def of_unknown(val: str) -> "ListDatasetsSort":
        if not isinstance(val, str):
            raise ValueError(f"Value of ListDatasetsSort must be a string (encountered: {val})")
        newcls = Enum("ListDatasetsSort", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(ListDatasetsSort, getattr(newcls, "_UNKNOWN"))
