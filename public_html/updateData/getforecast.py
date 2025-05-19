import os
import shutil

sourcePath = "/home/lrojo1/4910/csub-senior-project/log/components/forecast"
destPath = "/home/lrojo1/public_html/board_archive2"

dates = [
    "2025-05-01", "2025-05-02"
]

for filename in os.listdir(sourcePath):
    if filename.startswith("board") and filename.endswith(".json"):
        if any(date in filename for date in dates):
            src = os.path.join(sourcePath, filename)
            new_filename = f"{filename}"
            dst = os.path.join(destPath, new_filename)
            shutil.copy2(src, dst)

