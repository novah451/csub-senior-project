from aurora import Aurora
from aurora import Batch
from aurora import Metadata
from aurora import rollout
from borealis import Clock
from borealis import PrettyCLI
import numpy as np
import os
from pathlib import Path
import pandas as pd
import torch
import xarray as xr

clock = Clock()
PrettyCLI.tprint(f"Program PID: {os.getpid()}")

# Path towards the weather data SPECIFIC TO AURORA
path = Path("weather_data/aurora")

# Path towards where the predictions are saved
SAVE = "predictions/aurora/predictions.csv"

# How many predictions will be made
STEPS = 4

# Total Number of Pressure Levels
ALV = [(12, 50), (11, 100), (10, 150), (9, 200), (8, 250), (7, 300), 
       (6, 400), (5, 500), (4, 600), (3, 700), (2, 850), (1, 925), (0, 1000)]

'''Preparing a Batch'''
# Convert the downloaded data to an aurora.Batch -> required by model
static_vars_ds = xr.open_dataset(path / "static.nc", engine='netcdf4')
surf_vars_ds = xr.open_dataset(path / "2024-11-08-surface-level.nc", engine='netcdf4')
atmos_vars_ds = xr.open_dataset(path / "2024-11-08-atmospheric.nc", engine='netcdf4')

# Select this time index in the downloaded data
i = 1

PrettyCLI.tprint(f"Building Batch")

# Building the batch itself
batch = Batch(
    surf_vars={
        # First select time point 'i' and 'i - 1'. Afterwards, '[None]' inserts a batch dimension of size one
        # THIS SHIT IS BASICALLY GRABBING THE DATA FROM THE PREVIOUS STEP AND THE CURRENT STEP
        # THE CURRENT STEP IS DEFINED BY THE TIME INDEX: i = 1 REFERS TO 2024-11-08 12:00:00
        "2t": torch.from_numpy(surf_vars_ds["t2m"].values[[i - 1, i]][None]),
        "10u": torch.from_numpy(surf_vars_ds["u10"].values[[i - 1, i]][None]),
        "10v": torch.from_numpy(surf_vars_ds["v10"].values[[i - 1, i]][None]),
        "msl": torch.from_numpy(surf_vars_ds["msl"].values[[i - 1, i]][None]),
    },
    static_vars={
        # The static variables are constant, so we just get them for the first time
        # DOWNLOAD THE STATIC VARIABLES THAT REFER TO THE PREVIOUS STEP:
        # EXAMPLE: CURRENT = 2024-11-08 12:00:00 => DOWNLOAD 2024-11-08 06:00:00
        "z": torch.from_numpy(static_vars_ds["z"].values[0]),
        "slt": torch.from_numpy(static_vars_ds["slt"].values[0]),
        "lsm": torch.from_numpy(static_vars_ds["lsm"].values[0]),
    },
    atmos_vars={
        "t": torch.from_numpy(atmos_vars_ds["t"].values[[i - 1, i]][None]),
        "u": torch.from_numpy(atmos_vars_ds["u"].values[[i - 1, i]][None]),
        "v": torch.from_numpy(atmos_vars_ds["v"].values[[i - 1, i]][None]),
        "q": torch.from_numpy(atmos_vars_ds["q"].values[[i - 1, i]][None]),
        "z": torch.from_numpy(atmos_vars_ds["z"].values[[i - 1, i]][None]),
    },
    metadata=Metadata(
        lat=torch.from_numpy(surf_vars_ds.latitude.values),
        lon=torch.from_numpy(surf_vars_ds.longitude.values),
        # Converting to 'datetime64[s]' ensures that the output of 'tolist()' gives
        # 'datetime.datetime`s. Note that this needs to be a tuple of length one:
        # one value for every batch element.
        time=(surf_vars_ds.valid_time.values.astype("datetime64[s]").tolist()[i],),
        atmos_levels=tuple(int(level) for level in atmos_vars_ds.pressure_level.values),
    ),
)

PrettyCLI.tprint(f"Batched Built. Loading Model...")

'''Loading and Running the Model'''
# the pretrained version does not use LoRA
model = Aurora(use_lora=False)
model.load_checkpoint("microsoft/aurora", "aurora-0.25-pretrained.ckpt")

# Set model to evalulation mode
model.eval()
model = model.to("cpu")

PrettyCLI.tprint(f"Model Loaded and Ready. Running Model...")
PrettyCLI.spprint("NOTICE: THE FOLLOWING FEW STEPS WILL TAKE A MINUTE. PLEASE BE PATIENT :)")
clock.start()

with torch.inference_mode():
    preds = [pred.to("cpu") for pred in rollout(model, batch, steps=STEPS)]

clock.stop(f"Model finished running. Predictions have been made!")
PrettyCLI.tprint(f"Saving Predictions to Dictionary...")

columns = [
    # Metadata
    "time",
    "lat", 
    "lon", 
    "level", 
    # Surface Level Variables
    "2m_temperature", 
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "mean_sea_level_pressure",
    # Static Variables
    "land_sea_mask",
    "soil_type",
    "surface_geopotential",
    # Atmospheric Variables
    "temperature",
    "u_component_of_wind", 
    "v_component_of_wind", 
    "specific_humidity",
    "geopotential"
]

# aurora_df = pd.DataFrame(columns=columns)
LAT = np.arange(90, -90, -0.25, dtype='float32')
LON = np.arange(0, 360, 0.25, dtype='float32')
entry = 0
query_dict = {}

for i in range(0, STEPS):
    prediction = preds[i]

    PrettyCLI.tprint(f"Processing Batch {i}...")
    clock.start()

    # Surface and Static Only
    for ind_lt, lt in enumerate(LAT):
        for ind_ln, ln in enumerate(LON):
            for ind_apl, atmos_lvl in ALV:
                query_data = [
                    prediction.metadata.time[0],
                    lt,
                    ln,
                    np.int16(atmos_lvl),
                    float(prediction.surf_vars["2t"][0, 0, ind_lt, ind_ln]),
                    float(prediction.surf_vars["10u"][0, 0, ind_lt, ind_ln]),
                    float(prediction.surf_vars["10v"][0, 0, ind_lt, ind_ln]),
                    float(prediction.surf_vars["msl"][0, 0, ind_lt, ind_ln]),
                    float(prediction.static_vars["lsm"][ind_lt, ind_ln]),
                    float(prediction.static_vars["slt"][ind_lt, ind_ln]),
                    float(prediction.static_vars["z"][ind_lt, ind_ln]),
                    float(prediction.atmos_vars["t"][0, 0, ind_apl, ind_lt, ind_ln]),
                    float(prediction.atmos_vars["u"][0, 0, ind_apl, ind_lt, ind_ln]),
                    float(prediction.atmos_vars["v"][0, 0, ind_apl, ind_lt, ind_ln]), 
                    float(prediction.atmos_vars["q"][0, 0, ind_apl, ind_lt, ind_ln]),
                    float(prediction.atmos_vars["z"][0, 0, ind_apl, ind_lt, ind_ln])
                ]

                query_dict[entry] = query_data
                entry += 1

    clock.stop(f"Batch {i} Processed!")

    # off-load query_dict to Dataframe at halfway point -> Prevent Crashing?
    if i == 1:
        PrettyCLI.tprint("2 out of 4 Batches Complete, Now Offloading to DataFrame...")
        clock.start()
        half_aurora_df = pd.DataFrame.from_dict(query_dict, orient="index", columns=columns)
        # half_aurora_df[columns[4:]] = half_aurora_df[columns[4:]].astype('float32')
        query_dict = {}
        entry = 0
        clock.stop("Offload Complete; Dictionary Wiped; Proceeding with the 2 remaining Batches...")

del preds
del batch

PrettyCLI.tprint(f"Final Predictions are now stored in Dictionary!")
PrettyCLI.tprint(f"Proceeding to saving Dictionary as Dataframe...")
clock.start()

aurora_df = pd.DataFrame.from_dict(query_dict, orient="index", columns=columns)
# aurora_df[columns[4:]] = aurora_df[columns[4:]].astype('float32')
del query_dict

clock.stop("Dictionary has been saved as Dataframe!")

PrettyCLI.tprint("Now concatenating the two DataFrames into one...")
clock.start()

aurora_df = pd.concat([half_aurora_df, aurora_df], ignore_index=True)
del half_aurora_df

clock.stop("Both DataFrames successfully merged!")

PrettyCLI.tprint(f"Proceeding to saving Dataframe as CSV...")
clock.start()

aurora_df.to_csv(SAVE, sep=",", index=False)

clock.stop("Dataframe has been saved as CSV!")

print("\n", aurora_df, "\n")
