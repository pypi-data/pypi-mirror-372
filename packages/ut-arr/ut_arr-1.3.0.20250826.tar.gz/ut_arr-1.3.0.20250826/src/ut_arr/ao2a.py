# coding=utf-8

from collections.abc import Iterator
from typing import Any, Annotated

TyArr = list[Any]
TyAo2A = Annotated[list[TyArr], 2]
TyTo3Any = tuple[Any, Any, Any]

TnTo3Any = None | TyTo3Any


# class PoA:
class Ao2A:
    """
    Manage Arrays of two Arrays
    """
    @staticmethod
    def yield_items(
            ao2a: TyAo2A, obj: Any) -> Iterator[TnTo3Any]:
        arr0 = ao2a[0]
        arr1 = ao2a[1]
        if arr0 is None:
            yield None
        elif arr1 is None:
            yield None
        else:
            for item_arr0 in arr0:
                for item_arr1 in arr1:
                    yield (item_arr0, item_arr1, obj)
