import time
import inspect
import os

GRAY    = "\033[90m"
GREEN   = "\033[32m"
CYAN    = "\033[36m"
YELLOW  = "\033[33m"
RED     = "\033[31m"
MAGENTA = "\033[35m"
BRIGHT  = "\033[1m"
WHITE   = "\033[37m"
RESET   = "\033[0m"

def timestamp() -> str:
    return time.strftime("%I:%M:%S %p")

def caller_info():
    frame = inspect.stack()[2]
    filename = os.path.basename(frame.filename)
    line = frame.lineno
    return f"in {filename} at line {line}"

class Debug:
    @staticmethod
    def info(text: str) -> None:
        print(GRAY + f"[{timestamp()} " + GREEN + "INFO" + GRAY + "]" + RESET + " " +
              GRAY + f"[{caller_info()}]" + RESET + " " +
              WHITE + text + RESET)

    @staticmethod
    def debug(text: str) -> None:
        print(GRAY + f"[{timestamp()} " + CYAN + "DEBUG" + GRAY + "]" + RESET + " " +
              GRAY + f"[{caller_info()}]" + RESET + " " +
              WHITE + text + RESET)

    @staticmethod
    def warn(text: str) -> None:
        print(GRAY + f"[{timestamp()} " + YELLOW + "WARNING" + GRAY + "]" + RESET + " " +
              GRAY + f"[{caller_info()}]" + RESET + " " +
              WHITE + text + RESET)

    @staticmethod
    def err(text: str) -> None:
        print(GRAY + f"[{timestamp()} " + RED + "ERROR" + GRAY + "]" + RESET + " " +
              GRAY + f"[{caller_info()}]" + RESET + " " +
              WHITE + text + RESET)

    @staticmethod
    def succ(text: str) -> None:
        print(GRAY + f"[{timestamp()} " + BRIGHT + MAGENTA + "SUCCESS" + GRAY + "]" + RESET + " " +
              GRAY + f"[{caller_info()}]" + RESET + " " +
              WHITE + text + RESET)

__version__ = "0.1.0"
__all__ = ["Debug"]