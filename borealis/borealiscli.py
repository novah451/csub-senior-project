from time import process_time, time
from datetime import datetime, timedelta

__all__ = ["Clock", "PrettyCLI"]

class Clock():
    def __init__(self):
        self.wall_start = None
        self.cpu_start = None
        self.wall_stop = None
        self.cpu_stop = None
        self.wall_total = None
        self.cpu_total = None

    def start(self) -> None:
        self.wall_start = time()
        self.cpu_start = process_time()
    
    def stop(self, message: str = "Empty") -> None:
        self.wall_stop = time()
        self.cpu_stop = process_time()
        self.wall_total = self.wall_stop - self.wall_start
        self.cpu_total = self.cpu_stop - self.cpu_start
        if message != "Empty": PrettyCLI.tprint(message)
        PrettyCLI.spprint(f"Total Wall Time: {timedelta(seconds=round(self.wall_total, 6))}")
        PrettyCLI.spprint(f"Total CPU Time: {timedelta(seconds=round(self.cpu_total, 6))}")

class PrettyCLI():
    def tprint(line: str) -> None:
        """Prints out whatever you want with a time added in the front."""
        print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]    {line}")
    
    def tinput(line: str) -> int:
        """Takes in string for an input and adds time to the front."""
        return int(input(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]    {line}"))

    def spprint(line: str) -> None:
        """Prints out whatever you want with 25 spaces added in the front. Intended to compliment tprint()"""
        print(f"{' ' * 24} {line}")
