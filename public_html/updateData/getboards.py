import os
import shutil


sourcePath = "/home/lrojo1/4910/csub-senior-project/log/components/archive/current"
destPath = "/home/lrojo1/public_html/board_archive2"

dates = [
    "2025-04-10", "2025-04-11", "2025-04-12", "2025-04-13", "2025-04-14",
    "2025-04-15", "2025-04-16", "2025-04-17", "2025-04-18", "2025-04-19",
    "2025-04-20", "2025-04-21", "2025-04-22", "2025-04-23", "2025-04-24",
    "2025-04-25", "2025-04-26", "2025-04-27", "2025-04-28", "2025-04-29",
    "2025-04-30", "2025-05-01"
]

times = ["0-6", "6-12", "12-18", "18-0"]

for date in dates:
    for time in times:
        timePath = os.path.join(sourcePath, date, time)
        if not os.path.isdir(timePath):
            continue
        for filename in os.listdir(timePath):
            if filename.startswith("board") and filename.endswith(".json"):
                src = os.path.join(timePath, filename)
                new_filename = f"{filename}"
                dst = os.path.join(destPath, new_filename)
                shutil.copy2(src, dst)
