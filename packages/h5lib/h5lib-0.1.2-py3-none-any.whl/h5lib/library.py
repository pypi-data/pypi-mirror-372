# Standard Libraries
from pathlib import Path
from typing import Tuple, Sequence
from dataclasses import make_dataclass
from copy import copy
import re
from warnings import warn
import os

# Relative Imports
from .types import PathLike
from .reader import HDF5Reader, Bookshelf, Book, Page

# Constants
PYI_FILE = Path(__file__).with_suffix(".pyi")
TYPE_ALIASES = "PathLike = str | os.PathLike | Path"
FUNC_DEFS = "def add_file_to_library(file_path: PathLike) -> None: ..."
INDENT = "    "

if not PYI_FILE.exists():
    PYI_FILE.touch()


class BookshelfNotFoundError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


path_pattern = re.compile(r"\w:(?:\\\\\w+)+.hdf5")
libcache_pattern = re.compile(
    r"libcache\s=\s\[(?:\r?\n\s{4}\"\w:(?:\\\\\w+)+.hdf5\",)+"
)

with open(PYI_FILE) as f:
    file_string = f.read()
    libcache_list = re.findall(libcache_pattern, file_string)
    if len(libcache_list) > 0:
        libcache_string = libcache_list[0]
    else:
        libcache_string = ""

libcache = [
    Path(i).__str__() for i in (re.findall(path_pattern, libcache_string))
]


def bind_book(book: Book) -> None:
    """
    Makes a book-like data class and sets the `typed_object` field of the input
    `Book` object to this initialized dataclass.

    Parameters
    ----------
    book: Book
        Book object.

    Returns
    -------
    None
    """

    book_cls = make_dataclass(
        book.name.capitalize(), [(page.name, Page) for page in book.pages]
    )
    bound_book = book_cls(**{page.name: page for page in book.pages})

    book.book_type = book_cls
    book.typed_object = bound_book


def build_bookshelf(file_path: PathLike) -> HDF5Reader:
    """
    Compiles a book shelf object from an HDF5 file. This involves creating an
    `HDF5Reader` object, iterating through the books that are available through
    this class, running `bind_book` on each one and making a dataclass
    corresponding to each book. This dataclass is then initialized with both
    the books and the "loose pages" which are the attributes of the HDF5 root.

    Parameters
    ----------
    file_path: PathLike
        File path to an HDF5 file.

    Returns
    -------
    HDF5Reader
    """
    reader = HDF5Reader(file_path)

    for book in reader.bookshelf.books:
        bind_book(book)

    bookshelf_cls = make_dataclass(
        reader.bookshelf.name,
        [
            (book.name.lower(), book.book_type)
            for book in (reader.bookshelf.books)
        ]
        + [
            (page.name.lower(), Page)
            for page in (reader.bookshelf.loose_pages)
        ],
    )

    books = {
        book.name.lower(): book.typed_object
        for book in (reader.bookshelf.books)
    }
    loose_pages = {
        page.name.lower(): page for page in reader.bookshelf.loose_pages
    }

    bookshelf_constructor = {**books, **loose_pages}
    built_bookshelf = bookshelf_cls(**bookshelf_constructor)

    reader.bookshelf.shelf_type = bookshelf_cls
    reader.bookshelf.typed_object = built_bookshelf

    return reader


class StubFileString:
    """
    Singleton class that handles the creation of the H5Library.pyi Stub File.

    Parameters
    ----------
    import_list: list[Tuple[str, str]]
        List of packages to import.
    starting_bookshelves: list[Bookshelf]
        Starting bookshelf list.

    Methods
    -------

    """

    def __init__(
        self,
        # h5lib: H5Library,
        import_list: list[Tuple[str, str]] = [],
        starting_bookshelves: list[Bookshelf] = [],
    ):
        import_list += [("pathlib", "Path"), ("", "os")]
        self.import_statements = ""
        for i in import_list:
            if len(i[0]) != 0:
                self.import_statements += f"from {i[0]} import {i[1]}\n"
            else:
                self.import_statements += f"import {i[1]}"
        self.bookshelf_list: list[Bookshelf] = []
        self.book_set: set[Tuple[str, Tuple]] = set()
        self.classes = ""
        self.libclass = ""
        self.libcache = "\n\nlibcache = [\n"

        self._write_libcache()

        for shelf in starting_bookshelves:
            self.add_bookshelf(shelf)

    def _write_libcache(self):
        global libcache
        if len(libcache) == 0:
            self.libcache += "]\n"
            warn("Your H5Library is empty. Please add bookshelves.")
            return
        self.libcache = "\n\nlibcache = [\n"
        for shelf in self.bookshelf_list:
            self.libcache += f'{INDENT}"{shelf.path}",\n'
        self.libcache += "]\n"

    def _write_classes(
        self, class_list: list[Tuple[str, Sequence[Tuple[str, str]]]]
    ):
        for class_name, attr_list in class_list:
            self.classes += f"class {class_name}:"
            if len(attr_list) == 0:
                self.classes += f"\n{INDENT}...\n"
            else:
                self.classes += "\n"
            for attr in attr_list:
                self.classes += f"{INDENT}{attr[0]}: {attr[1]}\n"
            self.classes += "\n\n"

    def _write_libclass(self):
        self.libclass = "class H5LibraryClass:\n"
        for i in self.bookshelf_list:
            self.libclass += (
                f"{INDENT}{i.name.lower()}: " f"{i.name.capitalize()}\n"
            )
        self.libclass += (
            f"{INDENT}def add_bookshelf(self, "
            "p: PathLike | Bookshelf) -> None: ...\n\n"
        )
        self.libclass += (
            f"{INDENT}def close_bookshelf(self, p: PathLike) -> None: ..."
        )
        self.libclass += f"{INDENT}def clear(self) -> None: ..."

        self.libclass += "\nH5Library: H5LibraryClass\n"

    def add_bookshelf(self, shelf: Bookshelf) -> None:
        global libcache

        if shelf.path in libcache:
            print(f"{shelf.name.lower()} is an already existing bookshelf.")
            return None

        self.bookshelf_list.append(shelf)
        book_attr_types: dict[str, list[str]] = {}
        old_book_set = copy(self.book_set)
        for book in shelf.books:
            self.book_set.add(
                (
                    book.book_type.__name__,
                    tuple(book.typed_object.__dataclass_fields__.keys()),
                )
            )
            book_attr_types[book.book_type.__name__] = [
                i.type.__name__
                for i in (book.typed_object.__dataclass_fields__.values())
            ]
        book_set_with_types: list[Tuple[str, Sequence[Tuple[str, str]]]] = []
        for class_name, class_attr in self.book_set - old_book_set:
            book_set_with_types.append(
                (
                    class_name,
                    [
                        (attr_name, attr_type)
                        for attr_name, attr_type in zip(
                            class_attr, book_attr_types[class_name]
                        )
                    ],
                )
            )

        self._write_classes(
            [(cls_nm, cls_attrs) for cls_nm, cls_attrs in book_set_with_types]
        )

        self._write_classes(
            [
                (
                    shelf.shelf_type.__name__,
                    [
                        (k.lower(), v.type.__name__)
                        for k, v in (
                            shelf.typed_object.__dataclass_fields__.items()
                        )
                    ],
                )
            ]
        )

        self._write_libclass()

        libcache.append(shelf.path)

        self._write_libcache()

    def compile(self):
        with open(PYI_FILE, "w") as f:
            f.write(self.import_statements)
            f.write("\n\n")
            f.write(TYPE_ALIASES)
            f.write("\n\n\n")
            f.write(FUNC_DEFS)
            f.write("\n\n\n")
            f.write(self.classes)
            f.write(self.libclass)
            f.write(self.libcache)


class H5LibraryClass:
    """
    Represents several HDF5 files (Bookshelves) that have been stubbed to
    enable statically-typed reading.

    Parameters
    ----------
    None

    Methods
    -------
    add_bookshelf()
        Adds book shelf to library.
    close_bookshelf()
        Removes book shelf from library.
    clear()
        Clears all bookshelves from library by deleting thge stub file.

    Examples
    --------
    ```
    from h5lib import H5Library  # warning: No bookshelves in the library.
    mypath = ".../*.hdf5"
    H5Library.add_bookshelf(mypath)
    dataset = H5Library.bookshelf.book.page  # Fields are autocomplete enabled.
    ```

    Notes
    -----
    In order to delete or modify a bookshelf that has been added to the
    H5Library, `close_bookshelf()` must be called on it first.
    """

    def __init__(self) -> None:
        global libcache
        starting_readers = [build_bookshelf(i) for i in libcache]
        self.reader_lookup: dict[str, HDF5Reader] = {
            i: j for i, j in zip(libcache, starting_readers)
        }
        starting_shelves = [i.bookshelf for i in starting_readers]

        self._stub_file = StubFileString(
            import_list=[(".reader", "Page"), (".reader", "Bookshelf")],
            starting_bookshelves=starting_shelves,
        )

        for shelf in starting_shelves:
            setattr(
                self, shelf.shelf_type.__name__.lower(), shelf.typed_object
            )

        self._stub_file._write_libclass()
        self._stub_file.compile()

    def add_bookshelf(self, p: PathLike) -> None:
        """
        Adds a bookshelf object (i.e. an HDF5 file) to the H5Library.

        Parameters
        ----------
        p: PathLike
            File path to the HDF5 file.
        """
        global libcache
        libcache.append(Path(p).__str__())
        reader = build_bookshelf(p)
        self.reader_lookup[p.__str__()] = reader
        shelf = reader.bookshelf

        setattr(self, shelf.shelf_type.__name__.lower(), shelf.typed_object)
        self._stub_file.add_bookshelf(shelf)
        self._stub_file.compile()

    def close_bookshelf(self, p: PathLike) -> None:
        """
        Closes a bookshelf that has already been added to the H5Library.

        Parameters
        ----------
        p: PathLike
            File path to the HDF5 file.

        Raises
        ------
        BookshelfNotFoundError
            If the file path has not been added to the H5Library using
            `add_bookshelf`.
        """
        reader = self.reader_lookup.get(Path(p).__str__())
        if reader is None:
            raise BookshelfNotFoundError(
                f"{p} has not been added to the H5Library yet and thus cannot"
                " be removed."
            )
        reader.close_file()

    def clear(self):
        for rdr in self.reader_lookup.values():
            rdr.close_file()
        os.remove(PYI_FILE)


H5Library = H5LibraryClass()
