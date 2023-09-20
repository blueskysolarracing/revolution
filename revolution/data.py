from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field, replace
from enum import auto, Flag
from logging import getLogger
from threading import Lock
from typing import Any, cast, Generic, TypeVar

_logger = getLogger(__name__)
_T = TypeVar('_T')


@dataclass
class DataAccessor(Generic[_T]):
    class Mode(Flag):
        READ = auto()
        WRITE = auto()

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
        self.__mode = self.Mode(0)


@dataclass
class DataManager(Generic[_T]):
    __data: _T
    __reader_count: int = field(default=0, init=False)
    __reader_lock: Lock = field(default_factory=Lock, init=False)
    __writer_lock: Lock = field(default_factory=Lock, init=False)

    @contextmanager
    def read(self) -> Iterator[_T]:
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
        data_accessor = DataAccessor(self.__data, DataAccessor.Mode.WRITE)

        with self.__writer_lock, closing(data_accessor):
            yield cast(_T, data_accessor)

    @contextmanager
    def read_and_write(self) -> Iterator[_T]:
        data_accessor = DataAccessor(
            self.__data,
            DataAccessor.Mode.READ | DataAccessor.Mode.WRITE,
        )

        with self.__writer_lock, closing(data_accessor):
            yield cast(_T, data_accessor)

    @contextmanager
    def copy(self) -> Iterator[_T]:
        with self.read():
            data = replace(self.__data)  # type: ignore[misc, type-var]

        yield data
