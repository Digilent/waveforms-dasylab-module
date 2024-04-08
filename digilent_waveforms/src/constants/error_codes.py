from enum import Enum

# First two digits


# Generic - 00xxxx
class GenericError(Enum):
    UNKNOWN = 000000


# Manager - 01xxxx
class ManagerError(Enum):
    UNKNOWN = 10000


# Analog input subsystem - 02xxxx
class AnalogInputErorr(Enum):
    UNKNOWN = 20000


# Analog output subsystem - 03xxxx
class AnalogOutError(Enum):
    UNKNOWN = 30000
    INTPUT_LENGTH_MISMATCH = 30001
