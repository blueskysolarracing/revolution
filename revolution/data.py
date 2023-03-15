""":mod:`revolution.data` defines the data-related helper classes that
allow different applications to perform data read and/or write in a
readers-writer synchronization.
"""

from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field, replace
from enum import Flag, auto
from logging import getLogger
from threading import Lock
from typing import Any, Generic, TypeVar, cast

_logger = getLogger(__name__)
_T = TypeVar('_T')


@dataclass
class DataAccessor(Generic[_T]):
    """The wrapper class for data access. The underlying data may be
    read from and written to through its attributes.

    The :attr:`mode` denotes which access operations are allowed.
    """

    class Mode(Flag):
        """The enumeration class defining data access modes.

        The flags may be combined to allow multiple operations.
        """
        READ = auto()
        """The read mode."""
        WRITE = auto()
        """The write mode."""

    __initialized = False
    __data: _T
    __mode: Mode

    def __post_init__(self) -> None:
        self.__initialized = True

    def __getattr__(self, name: str) -> Any:
        if not self.__initialized or not hasattr(self.__data, name):
            return self.__getattribute__(name)
        elif self.Mode.READ not in self.__mode:
            raise ValueError('no read permission')
        else:
            return getattr(self.__data, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if not self.__initialized or not hasattr(self.__data, name):
            super().__setattr__(name, value)
        elif self.Mode.WRITE not in self.__mode:
            raise ValueError('no write permission')
        else:
            setattr(self.__data, name, value)

    def close(self) -> None:
        """Close the data accessor.

        After closure, all data access become prohibited and will result
        in an error.

        :return: ``None``.
        """
        self.__mode = self.Mode(0)


@dataclass
class DataManager(Generic[_T]):
    """The wrapper class for data synchronization.

    The underlying data are synchronized such that multiple reader and
    single writer is allowed. Write and read cannot be performed
    simultaneously.
    """

    __data: _T
    __reader_count: int = field(default=0, init=False)
    __reader_lock: Lock = field(default_factory=Lock, init=False)
    __writer_lock: Lock = field(default_factory=Lock, init=False)

    @contextmanager
    def read(self) -> Iterator[_T]:
        """Read from the underlying data.

        :return: A singleton iterator containing the accessor of the
                 underlying data.
        """
        with self.__reader_lock:
            if not self.__reader_count:
                self.__writer_lock.acquire()

            self.__reader_count += 1

        try:
            data_accessor = DataAccessor(self.__data, DataAccessor.Mode.READ)

            with closing(data_accessor):
                yield cast(_T, data_accessor)
        finally:
            with self.__reader_lock:
                self.__reader_count -= 1

                if not self.__reader_count:
                    self.__writer_lock.release()

    @contextmanager
    def write(self) -> Iterator[_T]:
        """Write to the underlying data.

        :return: A singleton iterator containing the accessor of the
                 underlying data.
        """
        data_accessor = DataAccessor(self.__data, DataAccessor.Mode.WRITE)

        with self.__writer_lock, closing(data_accessor):
            yield cast(_T, data_accessor)

    @contextmanager
    def read_and_write(self) -> Iterator[_T]:
        """Read from and write to the underlying data.

        :return: A singleton iterator containing the accessor of the
                 underlying data.
        """
        data_accessor = DataAccessor(
            self.__data,
            DataAccessor.Mode.READ | DataAccessor.Mode.WRITE,
        )

        with self.__writer_lock, closing(data_accessor):
            yield cast(_T, data_accessor)

    @contextmanager
    def copy(self) -> Iterator[_T]:
        """Copy the underlying data.

        :return: A singleton iterator containing the copy of the
                 underlying data.
        """
        with self.read():
            data = replace(self.__data)

        yield data
