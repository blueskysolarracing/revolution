from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, field, replace
from enum import Flag, auto
from multiprocessing import Lock, get_logger
from multiprocessing.synchronize import Lock as _Lock  # FIXME
from typing import Any, Generic, TypeVar, cast

_logger = get_logger()
_T = TypeVar('_T')


@dataclass
class DataWrapper(Generic[_T]):
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
    __reader_lock: _Lock = field(default_factory=Lock, init=False)
    __writer_lock: _Lock = field(default_factory=Lock, init=False)

    @contextmanager
    def read(self) -> Iterator[_T]:
        with self.__reader_lock:
            if not self.__reader_count:
                self.__writer_lock.acquire()

            self.__reader_count += 1

        try:
            data_wrapper = DataWrapper(self.__data, DataWrapper.Mode.READ)

            with closing(data_wrapper):
                yield cast(_T, data_wrapper)
        finally:
            with self.__reader_lock:
                self.__reader_count -= 1

                if not self.__reader_count:
                    self.__writer_lock.release()

    @contextmanager
    def write(self) -> Iterator[_T]:
        data_wrapper = DataWrapper(self.__data, DataWrapper.Mode.WRITE)

        with self.__writer_lock, closing(data_wrapper):
            yield cast(_T, data_wrapper)

    @contextmanager
    def read_and_write(self) -> Iterator[_T]:
        data_wrapper = DataWrapper(
            self.__data,
            DataWrapper.Mode.READ | DataWrapper.Mode.WRITE,
        )

        with self.__writer_lock, closing(data_wrapper):
            yield cast(_T, data_wrapper)

    @contextmanager
    def copy(self) -> Iterator[_T]:
        with self.read():
            data = replace(self.__data)

        yield data
