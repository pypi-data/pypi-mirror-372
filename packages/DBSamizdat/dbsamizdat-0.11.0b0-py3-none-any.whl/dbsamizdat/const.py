from enum import Enum, IntFlag, auto

class txstyle(Enum):
    CHECKPOINT = 'checkpoint'
    JUMBO = 'jumbo'
    DRYRUN = 'dryrun'

class env(IntFlag):
    API = auto()
    CLI = auto()
    DJANGO = auto()
