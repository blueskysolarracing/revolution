from enum import IntEnum


class Direction(IntEnum):
    FORWARD = 0
    BACKWARD = 1


PRBS = tuple[int, int]