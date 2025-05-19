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
import matplotlib.pyplot as plt

clock = Clock()

def save_predictions(args: tuple[Batch, int]):
    prediction, id = args

    PrettyCLI.tprint(f"Processing Batch {id}...")
    clock.start()

    # Total Number of Pressure Levels
    ALV = [(12, 50), (11, 100), (10, 150), (9, 200), (8, 250), (7, 300), 
            (6, 400), (5, 500), (4, 600), (3, 700), (2, 850), (1, 925), (0, 1000)]
    LAT = np.linspace(37, 34, 13, dtype='float32')
    LON = np.linspace(243, 239.25, 16, dtype='float32')
    query_dict = {}
    entry = ''.join(choices(ascii_uppercase + digits, k=10))

    # Surface and Static Only
    for ind_lt, lt in enumerate(LAT):
        for ind_ln, ln in enumerate(LON):
            for ind_apl, atmos_lvl in ALV:
                query_data = [
                    prediction.metadata.time[0],
                    lt,
                    ln,
                    np.int16(atmos_lvl),
                    prediction.surf_vars["2t"][ind_lt, ind_ln],
                    prediction.surf_vars["10u"][ind_lt, ind_ln],
                    prediction.surf_vars["10v"][ind_lt, ind_ln],
                    prediction.surf_vars["msl"][ind_lt, ind_ln],
                    prediction.static_vars["lsm"][ind_lt, ind_ln],
                    prediction.static_vars["slt"][ind_lt, ind_ln],
                    prediction.static_vars["z"][ind_lt, ind_ln],
                    prediction.atmos_vars["t"][ind_apl, ind_lt, ind_ln],
                    prediction.atmos_vars["u"][ind_apl, ind_lt, ind_ln],
                    prediction.atmos_vars["v"][ind_apl, ind_lt, ind_ln], 
                    prediction.atmos_vars["q"][ind_apl, ind_lt, ind_ln],
                    prediction.atmos_vars["z"][ind_apl, ind_lt, ind_ln]
                ]

                query_dict[entry] = query_data
                entry = ''.join(choices(ascii_uppercase + digits, k=10))

    clock.stop(f"Batch {id} Processed!")
    return query_dict

def autorun(s: int):
    PrettyCLI.tprint(f"Program PID: {os.getpid()}")
    STEPS = s

    batch_00: Batch = Batch.from_netcdf("batch/batch_00.nc")
    batch_06: Batch = Batch.from_netcdf("batch/batch_06.nc")

    '''
    fig, (ax0, ax1) = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
    ax0.imshow(batch_00.surf_vars["10u"][0, 0].numpy())
    ax0.set_title(str(batch_00.metadata.time[0]))
    ax0.set_xticks([])
    ax0.set_yticks([])

    ax1.imshow(batch_06.surf_vars["10u"][0, 0].numpy())
    ax1.set_title(str(batch_06.metadata.time[0]))
    ax1.set_xticks([])
    ax1.set_yticks([])

    fig.tight_layout()
    fig.savefig("aaa.png", dpi=300)
    exit(0)
    '''

    PrettyCLI.tprint(f"Building Batch")
    # Building the batch itself
    batch = Batch(
        surf_vars={
            # First select time point 'i' and 'i - 1'. Afterwards, '[None]' inserts a batch dimension of size one
            # THIS SHIT IS BASICALLY GRABBING THE DATA FROM THE PREVIOUS STEP AND THE CURRENT STEP
            # THE CURRENT STEP IS DEFINED BY THE TIME INDEX: i = 1 REFERS TO 2024-11-08 12:00:00
            "2t": torch.from_numpy(np.stack((batch_00.surf_vars["2t"][0, 0].numpy(), batch_06.surf_vars["2t"][0, 0].numpy()), axis=0)[None]),
            "10u": torch.from_numpy(np.stack((batch_00.surf_vars["10u"][0, 0].numpy(), batch_06.surf_vars["10u"][0, 0].numpy()), axis=0)[None]),
            "10v": torch.from_numpy(np.stack((batch_00.surf_vars["10v"][0, 0].numpy(), batch_06.surf_vars["10v"][0, 0].numpy()), axis=0)[None]),
            "msl": torch.from_numpy(np.stack((batch_00.surf_vars["msl"][0, 0].numpy(), batch_06.surf_vars["msl"][0, 0].numpy()), axis=0)[None]),
        },
        static_vars={
            # The static variables are constant, so we just get them for the first time
            # DOWNLOAD THE STATIC VARIABLES THAT REFER TO THE PREVIOUS STEP:
            # EXAMPLE: CURRENT = 2024-11-08 12:00:00 => DOWNLOAD 2024-11-08 06:00:00
            "z": torch.from_numpy(batch_00.static_vars["lsm"].numpy()),
            "slt": torch.from_numpy(batch_00.static_vars["lsm"].numpy()),
            "lsm": torch.from_numpy(batch_00.static_vars["lsm"].numpy()),
        },
        atmos_vars={
            "t": torch.from_numpy(np.stack((batch_00.atmos_vars["t"][0, 0, :].numpy(), batch_06.atmos_vars["t"][0, 0, :].numpy()), axis=0)[None]),
            "u": torch.from_numpy(np.stack((batch_00.atmos_vars["u"][0, 0, :].numpy(), batch_06.atmos_vars["u"][0, 0, :].numpy()), axis=0)[None]),
            "v": torch.from_numpy(np.stack((batch_00.atmos_vars["v"][0, 0, :].numpy(), batch_06.atmos_vars["v"][0, 0, :].numpy()), axis=0)[None]),
            "q": torch.from_numpy(np.stack((batch_00.atmos_vars["q"][0, 0, :].numpy(), batch_06.atmos_vars["q"][0, 0, :].numpy()), axis=0)[None]),
            "z": torch.from_numpy(np.stack((batch_00.atmos_vars["z"][0, 0, :].numpy(), batch_06.atmos_vars["z"][0, 0, :].numpy()), axis=0)[None]),
        },
        metadata=Metadata(
            lat=torch.from_numpy(batch_00.metadata.lat.numpy()),
            lon=torch.from_numpy(batch_00.metadata.lon.numpy()),
            # Converting to 'datetime64[s]' ensures that the output of 'tolist()' gives
            # 'datetime.datetime`s. Note that this needs to be a tuple of length one:
            # one value for every batch element.
            time=batch_06.metadata.time,
            atmos_levels=batch_06.metadata.atmos_levels,
        ),
    )

    PrettyCLI.tprint(f"Batched Built. Loading Model...")
    '''Loading and Running the Model'''
    # the pretrained version does not use LoRA
    # model = Aurora(autocast=True, use_lora=False, timestep=timedelta(hours=1))
    model = Aurora(autocast=True, use_lora=False)
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

    if STEPS == 4:
        batches = preds[-2:]
        print(batches[0].metadata.time)
        print(batches[1].metadata.time)
        batches[0].to_netcdf("batch/batch_00.nc")
        batches[1].to_netcdf("batch/batch_06.nc")
    else:
        batches = preds[0:]
        all_results_in_one: dict = {}
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

        # Slice out the chunk that we only need: 13 by 16
        for index, p in enumerate(batches):
            for key in p.surf_vars:
                batches[index].surf_vars[key] = batches[index].surf_vars[key][0, 0, 212:225, 957:973].numpy()

            for key in p.atmos_vars:
                batches[index].atmos_vars[key] = batches[index].atmos_vars[key][0, 0, :, 212:225, 957:973].numpy()

            for key in p.static_vars:
                batches[index].static_vars[key] = batches[index].static_vars[key][212:225, 957:973].numpy()
            
            result = save_predictions([p, index])
            all_results_in_one.update(result)

        clock.start()
        aurora_df = pd.DataFrame.from_dict(all_results_in_one, orient="index", columns=columns)
        aurora_df = aurora_df.sort_values(by=["time", "lat", "lon"], ascending=[True, True, True])
        clock.stop("Dictionary has been saved as Dataframe!")

        PrettyCLI.tprint(f"Proceeding to saving Dataframe as CSV...")

        clock.start()
        aurora_df.to_csv(f"log/components/forecast/global_predictions_{batches[0].metadata.time[0].date()}.csv", sep=",", index=False)
        clock.stop("Dataframe has been saved as CSV!")

        print("\n", aurora_df, "\n")

if __name__ == "__main__":
    autorun(int(argv[1]))