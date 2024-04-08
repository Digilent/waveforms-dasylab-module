from enum import Enum
from .dwfconstants import *


class OutputFunction(Enum):
    DC = funcDC
    SINE = funcSine
    SQUARE = funcSquare
    TRIANGLE = funcTriangle
    RAMPUP = funcRampUp
    RAMPDOWN = funcRampDown
    NOISE = funcNoise
    PULSE = funcPulse
    TRAPEZIUM = funcTrapezium
    SINE_POWER = funcSinePower
    CUSTOM_PATTERN = funcCustomPattern
    PLAY_PATTERN = funcPlayPattern
    CUSTOM = funcCustom
    PLAY = funcPlay


class InstrumentStartMode(Enum):
    STOP = 0
    START = 1
    APPLY = 3
