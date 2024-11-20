from time import process_time, time
from datetime import datetime, timedelta

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
        if message != "Empty": print_wtime(message)
        print_wspace(f"Total Wall Time: {timedelta(seconds=round(self.wall_total, 6))}")
        print_wspace(f"Total CPU Time: {timedelta(seconds=round(self.cpu_total, 6))}")

def print_wtime(line: str) -> str:
    """Prints out whatever you want with a time added in the front."""
    print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]    {line}")

def print_wspace(line: str) -> str:
    """Prints out whatever you want with 25 spaces added in the front. Intended to compliment print_wtime()"""
    print(f"{' ' * 24} {line}")
