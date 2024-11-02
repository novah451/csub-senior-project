from datetime import datetime

def print_wtime(line: str) -> str:
    print(f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]    {line}")

def print_wspace(line: str) -> str:
    print(f"{' ' * 24} {line}")
