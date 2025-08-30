# Standard Libraries
from dataclasses import dataclass, field, make_dataclass
from typing import Any, Protocol
from pathlib import Path

# Dependencies
import numpy as np
import h5py as h5  # type: ignore

# Relative Imports
from .types import PathLike

# from .lazy_hdf5_loader import create_lazy_hdf5_dataclass


class GenericDataclass(Protocol):
    __dataclass_fields__: dict[str, Any]


def default_typed_object() -> GenericDataclass:
    DynamicDataclass = make_dataclass(
        "DynamicDataclass", [("foo", int, field(default=42))]
    )
    return DynamicDataclass()


class Page:
    """
    Class representing an HDF5 dataset. This is the lowest level of the HDF5
    hierarchy.

    Parameters
    ----------
    name: str
    h5data: h5.Datasets | np.ndarray

    Attributes
    ----------
    name: str
    shape: Tuple of integers

    Notes
    -----
    This object acts as an array-like object. To read the whole dataset use an
    ellipsis:
    ```python
    data = Page[...]
    ```
    """

    def __init__(self, name: str, h5data: h5.Dataset | np.ndarray) -> None:
        self.name = name
        self._h5data = h5data
        self.shape = self._h5data.shape

    def __getitem__(self, key):
        return self._h5data[key]

    def __array__(self, dtype=None):
        if dtype:
            return self._h5data[...].astype(dtype)
        return self._h5data[...]


@dataclass
class Book:
    """
    Class that represents an HDF5 Group.

    Attributes
    ----------
    name: str
    pages: list of Page
    book_type: type
    typed_object: GenericDataclass

    Notes
    -----
    `book_type` and `typed_object` are initialized with Null values and are
    replaced when `bind_book` is called on the object.
    """

    name: str
    pages: list[Page] = field(default_factory=list)
    book_type: type = str  # This is the class of the object below.
    typed_object: GenericDataclass = field(
        default_factory=default_typed_object
    )


@dataclass
class Bookshelf:
    """
    Represents an entire HDF5 file.

    Attributes
    ----------
    name: str
    path: str
    books: list of Book
    loose_pages: list of Page
    shelf_type: type
    typed_object: GenericDataclass
    """

    name: str
    path: str
    books: list[Book] = field(default_factory=list)
    loose_pages: list[Page] = field(default_factory=list)
    shelf_type: type = str  # Class of the object below.
    typed_object: GenericDataclass = field(
        default_factory=default_typed_object
    )


class HDF5Reader:
    """
    Lazily reads an HDF5 file. The attributes will be dynamically generated
    upon instantiation, and datasets will be loaded into memory when they are
    first called.

    Parameters
    ----------
    h5_path: PathLike
        Path to *.hdf5 file.
    """

    def __init__(self, h5_path: PathLike):
        self._file = h5.File(h5_path, "r")
        self.bookshelf: Bookshelf = Bookshelf(
            Path(h5_path).stem.__str__().capitalize(),
            Path(h5_path).__str__().replace("\\", "\\\\"),
        )
        self._file.visititems(self._visitor)
        if len(self._file.attrs) > 0:
            for attr_name, attr in self._file.attrs.items():
                if not (
                    isinstance(attr, h5.Dataset) | isinstance(attr, np.ndarray)
                ):
                    continue

                attr_page: Page = Page(name=attr_name, h5data=attr)
                self.bookshelf.loose_pages.append(attr_page)

    def _visitor(self, name, obj):
        if isinstance(obj, h5.Group):
            all_keys: list[str] = (  # type: ignore
                list(obj.keys()) + list(obj.attrs.keys())  # type: ignore
            )  # type: ignore

            all_vals: list[h5.Dataset | np.ndarray] = (  # type: ignore
                list(obj.values()) + list(obj.attrs.values())  # type: ignore
            )  # type: ignore

            cls_constr: Book = Book(  # type: ignore
                name=str(name),  # type: ignore
                pages=[
                    (Page(k, v)) for k, v in zip(all_keys, all_vals)
                ],  # type: ignore
            )  # type: ignore

            self.bookshelf.books.append(cls_constr)

    def close_file(self):
        self._file.close()
