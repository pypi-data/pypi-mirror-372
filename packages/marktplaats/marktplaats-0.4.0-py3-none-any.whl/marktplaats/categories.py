from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypedDict, TypeVar

from typing_extensions import Self


if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from types import NotImplementedType


class L1Category:
    def __init__(self, id_: int, name: str) -> None:
        self.id = id_
        self.name = name

    @classmethod
    def from_name(cls, name: str) -> Self:
        orig_name = name
        name = name.lower()
        try:
            l1_category = _l1_categories_raw.get_data()[name]
        except KeyError as err:
            msg = f"Unknown L1 category name: {orig_name}"
            raise ValueError(msg) from err
        id_, name = l1_category["id"], l1_category["name"]
        return cls(id_, name)

    @classmethod
    def from_id(cls, id_: int, name: str = "Unknown") -> None:
        cls(id_, name)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, L1Category):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class L2Category:
    def __init__(self, id_: int, name: str, parent: L1Category) -> None:
        self.id = id_
        self.name = name
        self.parent = parent

    @classmethod
    def from_name(cls, name: str) -> Self:
        orig_name = name
        name = name.lower()
        try:
            l2_category = _l2_categories_raw.get_data()[name]
        except KeyError as err:
            msg = f"Unknown L2 category name: {orig_name}"
            raise ValueError(msg) from err
        return cls(
            id_=l2_category["id"],
            name=l2_category["name"],
            parent=L1Category.from_name(l2_category["parent"]),
        )

    @classmethod
    def from_id(cls, id_: int, parent: L1Category, name: str = "Unknown") -> None:
        cls(id_, name, parent)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> NotImplementedType | bool:
        if not isinstance(other, L2Category):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


def category_from_name(name: str) -> L1Category | L2Category:
    try:
        return L1Category.from_name(name)
    except ValueError:
        return L2Category.from_name(name)


KT = TypeVar("KT")
VT = TypeVar("VT")


class LazyWrapper(Generic[KT, VT]):
    def __init__(self, filename: Path) -> None:
        self.filename = filename
        self._data: Mapping[KT, VT] | None = None

    def get_data(self) -> Mapping[KT, VT]:
        if self._data is None:
            self._build_data()
            assert self._data is not None  # noqa: S101 Assert for typechecker
        return self._data

    def _build_data(self) -> None:
        with self.filename.open() as file:
            self._data = json.load(file)


def get_l1_categories() -> Iterator[L1Category]:
    for category in _l1_categories_raw.get_data().values():
        yield L1Category(category["id"], category["name"])


def get_l2_categories() -> Iterator[L2Category]:
    for category in _l2_categories_raw.get_data().values():
        parent = L1Category.from_name(category["parent"])
        yield L2Category(category["id"], category["name"], parent)


def get_subcategories(l1_category: L1Category) -> Iterator[L2Category]:
    return (cat for cat in get_l2_categories() if cat.parent == l1_category)


def get_l2_categories_by_parent() -> Mapping[L1Category, list[L2Category]]:
    categories = defaultdict(list)
    for category in get_l2_categories():
        categories[category.parent].append(category)
    return categories


class _L1CategoryData(TypedDict):
    id: int
    name: str


class _L2CategoryData(TypedDict):
    id: int
    name: str
    parent: str


_l1_categories_file = (Path(__file__).parent / "l1_categories.json").resolve()
_l1_categories_raw: LazyWrapper[str, _L1CategoryData] = LazyWrapper(_l1_categories_file)
_l2_categories_file = (Path(__file__).parent / "l2_categories.json").resolve()
_l2_categories_raw: LazyWrapper[str, _L2CategoryData] = LazyWrapper(_l2_categories_file)
