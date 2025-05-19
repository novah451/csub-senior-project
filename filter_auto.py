from datetime import datetime
from datetime import timedelta
from itertools import product
from sys import argv

import numpy as np
import pandas as pd

CURRENT_TIME = datetime(int(argv[1]), int(argv[2]), int(argv[3]), int(argv[4]), 0, 0)

aurora_data = pd.read_csv(f"log/components/forecast/local_predictions_{CURRENT_TIME.date()}.csv")
aurora_data['time'] = pd.to_datetime(aurora_data['time'], format='ISO8601')
times = aurora_data["time"].unique()
pairs = list(zip(times, times[1:]))

for previous, current in pairs:
    save = f"log/components/forecast/local_predictions_{previous.hour:02d}-{current.hour:02d}.csv"
    data = aurora_data[(aurora_data['time'] >= previous) & (aurora_data['time'] <= current)]
    data = data.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
    data.to_csv(save, na_rep='null', index=False)