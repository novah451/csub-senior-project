import os
import shutil

sourcePath = "/home/lrojo1/4910/csub-senior-project/log/components/forecast"
destPath = "/home/lrojo1/public_html/eval"

eval_files = [
    ("2025-05-01", "evaluation_12-18.csv", "1200-1800"),
    ("2025-05-01", "evaluation_18-00.csv", "1800-0000"),
    ("2025-05-02", "evaluation_00-06.csv", "0000-0600"),
    ("2025-05-02", "evaluation_06-12.csv", "0600-1200"),
]

for file_date, original_name, formatted_time in eval_files:
    src = os.path.join(sourcePath, original_name)
    new_name = f"{file_date}_evaluation_{formatted_time}.csv"
    dst = os.path.join(destPath, new_name)
    shutil.copy2(src, dst)

