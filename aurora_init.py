from aurora import Aurora
from aurora import Batch
from aurora import Metadata
from aurora import rollout
from borealis import Clock
from borealis import PrettyCLI
from datetime import date
from datetime import timedelta
from multiprocessing import Pool
from random import choices
from string import ascii_uppercase
from string import digits
from sys import argv
from tqdm import tqdm

import numpy as np
import os
from pathlib import Path
import pandas as pd
import torch
import time
import xarray as xr

clock = Clock()

if __name__ == "__main__":
    # Path towards the weather data SPECIFIC TO AURORA
    path = Path("weather_data/aurora")

    CURRENT_TIME = date(int(argv[1]), int(argv[2]), int(argv[3]))
    TOMORROW_TIME = CURRENT_TIME + timedelta(days=1)

    # Path towards where the predictions are saved
    SAVE = f"predictions/aurora/global_predictions_{CURRENT_TIME}.csv"

    # How many predictions will be made
    STEPS = 4

    PrettyCLI.tprint(f"Program PID: {os.getpid()}")

    '''Preparing a Batch'''
    # Convert the downloaded data to an aurora.Batch -> required by model
    static_vars_ds = xr.open_dataset(path / f"{argv[1]}-{argv[2]}-{argv[3]}-static.nc", engine='netcdf4')
    surf_vars_ds = xr.open_dataset(path / f"{argv[1]}-{argv[2]}-{argv[3]}-surface-level.nc", engine='netcdf4')
    atmos_vars_ds = xr.open_dataset(path / f"{argv[1]}-{argv[2]}-{argv[3]}-atmospheric.nc", engine='netcdf4')

    # Select this time index in the downloaded data
    i = 1

    print(surf_vars_ds.valid_time.values.astype("datetime64[s]").tolist())
    PrettyCLI.tprint(f"Building Batch")

    # Building the batch itself
    batch = Batch(
        surf_vars={
            # First select time point 'i' and 'i - 1'. Afterwards, '[None]' inserts a batch dimension of size one
            # THIS SHIT IS BASICALLY GRABBING THE DATA FROM THE PREVIOUS STEP AND THE CURRENT STEP
            # THE CURRENT STEP IS DEFINED BY THE TIME INDEX: i = 1 REFERS TO 2024-11-08 12:00:00
            "2t": torch.from_numpy(surf_vars_ds["t2m"].values[None]),
            "10u": torch.from_numpy(surf_vars_ds["u10"].values[None]),
            "10v": torch.from_numpy(surf_vars_ds["v10"].values[None]),
            "msl": torch.from_numpy(surf_vars_ds["msl"].values[None]),
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
    # model = Aurora(autocast=True, use_lora=False, timestep=timedelta(hours=1))
    model = Aurora(autocast=True, use_lora=False)
    # model = Aurora(use_lora=False)
    model.load_checkpoint("microsoft/aurora", "aurora-0.25-pretrained.ckpt")

    # Set model to evalulation mode
    model.eval()
    model = model.to("cuda")

    PrettyCLI.tprint(f"Model Loaded and Ready. Running Model...")
    PrettyCLI.spprint("NOTICE: THE FOLLOWING FEW STEPS WILL TAKE A MINUTE. PLEASE BE PATIENT :)")
    clock.start()

    # total number of predictions = 29 (pulling number out of my ass)
    with torch.inference_mode():
        preds: list[Batch] = [pred.to("cpu") for pred in rollout(model, batch, steps=STEPS)]

    model = model.to("cpu")
    torch.cuda.empty_cache()
    
    clock.stop(f"Model finished running. Predictions have been made!")

    PrettyCLI.tprint(f"Saving Predictions as Dictionary...")

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

    batches = preds[-2:]
    print(batches[0].metadata.time)
    print(batches[1].metadata.time)
    batches[0].to_netcdf("batch/batch_00.nc")
    batches[1].to_netcdf("batch/batch_06.nc")