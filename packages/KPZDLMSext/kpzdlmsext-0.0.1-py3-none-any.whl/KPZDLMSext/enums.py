from enum import IntEnum


class Command(IntEnum):
    CALIBRATE_ALL = 0
    CALIBRATE_A = 1
    CALIBRATE_B = 2
    CALIBRATE_C = 3
    SET_OFFSET = 5
    SET_WORK = 10
    SET_FACTORY = 11


class Status(IntEnum):
    COMPLETE = 0
    BUSY = 1
    PHASE_A_ERROR = 11
    PHASE_B_ERROR = 12
    PHASE_C_ERROR = 13
    UNKNOWN = 255
    TIMEOUT = 256
    NOT_HANDLED = 257
