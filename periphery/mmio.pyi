from ctypes import Structure, c_void_p
from types import TracebackType

long = int

class MMIOError(IOError): ...

class MMIO:
    def __init__(self, physaddr: int | long, size : int | long, path: str = ...) -> None: ...
    def __del__(self) -> None: ...
    def __enter__(self) -> MMIO: ...
    def __exit__(self, t: type[BaseException] | None, value: BaseException | None, traceback: TracebackType | None) -> None: ...
    def read32(self, offset: int | long) -> int: ...
    def read16(self, offset: int | long) -> int: ...
    def read8(self, offset: int | long) -> int: ...
    def read(self, offset: int | long, length: int) -> bytes: ...
    def write32(self, offset: int | long, value: int | long) -> None: ...
    def write16(self, offset: int | long, value: int | long) -> None: ...
    def write8(self, offset: int | long, value: int | long) -> None: ...
    def write(self, offset: int | long, data: bytes | bytearray | list[int]) -> None: ...
    def close(self) -> None: ...
    @property
    def base(self) -> int: ...
    @property
    def size(self) -> int: ...
    @property
    def pointer(self) -> c_void_p: ...