from enum import IntEnum

from iclib.mcp23s17 import Port, PortRegisterBit, Register


class Direction(IntEnum):
    FORWARD: int = 0
    BACKWARD: int = 1


PRBS = (
    PortRegisterBit
    | tuple[PortRegisterBit, bool]
    | tuple[Port, Register, int]
    | tuple[tuple[Port, Register, int], bool]
)
