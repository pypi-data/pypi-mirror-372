from enum import Enum

class LogLevel(Enum):
    NO_LOG = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

_log_level = LogLevel.INFO

def set_level(mode: LogLevel):
    global _log_level
    _log_level = mode

def info(*args):
    if _log_level.value >= LogLevel.INFO.value:
        print('\033[94m[INFO]\033[00m', *args) # blue

def warning(*args):
    if _log_level.value >= LogLevel.WARNING.value:
        print('\033[93m[WARNING]\033[00m', *args) # yellow

def error(*args):
    if _log_level.value >= LogLevel.ERROR.value:
        print('\033[91m[ERROR]\033[00m', *args) # red

def debug(*args):
    if _log_level.value >= LogLevel.DEBUG.value:
        print('\033[92m[DEBUG]\033[00m', *args) # green