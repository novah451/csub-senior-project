# from borealiscli import print_wtime
from pathlib import Path
from os import makedirs
from google.cloud import storage
from borealis.borealiscli import PrettyCLI

__all__ = ["setup_folders"]

def setup_log():
    log_path = Path("log/")
    if not log_path.exists():
        PrettyCLI.tprint("No Log Folder Detected. Generating ...")
        log_path.mkdir(parents=True, exist_ok=True)
        makedirs(log_path / "aurora")
        makedirs(log_path / "graphcast")
        PrettyCLI.tprint("Log Folder Successfully Created ...")
    else:
        # print("[!]    Log Folder Detected! No Further Action Required ...")
        PrettyCLI.tprint("Log Folder Detected! No Further Action Required ...")

def setup_model():
    model_path = Path("model/")
    if not model_path.exists():
        PrettyCLI.tprint("No model folder detected. Generating ...")
        '''Setup subdirectories'''
        model_path.mkdir(parents=True, exist_ok=True)
        makedirs(model_path / "aurora")
        makedirs(model_path / "graphcast")
        makedirs(model_path / "graphcast/params")
        makedirs(model_path / "graphcast/stats")
        PrettyCLI.tprint("Model Folder Successfully Created ...")
        '''Add files for GraphCast'''
        PrettyCLI.tprint("Adding Required Files for GraphCast. THIS MAY TAKE A MINUTE ...")
        # Initialise a client
        storage_client = storage.Client.create_anonymous_client()
        # Create a bucket object for our bucket
        bucket = storage_client.get_bucket("dm_graphcast")
        # Create a blob object from the filepath
        blob_1 = bucket.blob("params/GraphCast - ERA5 1979-2017 - resolution 0.25 - pressure levels 37 - mesh 2to6 - precipitation input and output.npz")
        blob_2 = bucket.blob("stats/diffs_stddev_by_level.nc")
        blob_3 = bucket.blob("stats/mean_by_level.nc")
        blob_4 = bucket.blob("stats/stddev_by_level.nc")
        # Download the file to a destination
        blob_1.download_to_filename(model_path / "graphcast/params/GraphCast - ERA5 1979-2017 - resolution 0.25 - pressure levels 37 - mesh 2to6 - precipitation input and output.npz")
        blob_2.download_to_filename(model_path / "graphcast/stats/diffs_stddev_by_level.nc")
        blob_3.download_to_filename(model_path / "graphcast/stats/mean_by_level.nc")
        blob_4.download_to_filename(model_path / "graphcast/stats/stddev_by_level.nc")
        PrettyCLI.tprint("All Required GraphCast Files Downloaded ...")
    else:
        # print("[!]    Model Folder Detected! No Further Action Required ...")
        PrettyCLI.tprint("Model Folder Detected! No Further Action Required ...")

def setup_prediction():
    prediction_path = Path("predictions/")
    if not prediction_path.exists():
        PrettyCLI.tprint("No Prediction Folder Detected. Generating ...")
        prediction_path.mkdir(parents=True, exist_ok=True)
        makedirs(prediction_path / "aurora")
        makedirs(prediction_path / "graphcast")
        PrettyCLI.tprint("Prediction Folder Successfully Created ...")
    else:
        # print("[!]    Prediction Folder Detected! No Further Action Required ...")
        PrettyCLI.tprint("Prediction Folder Detected! No Further Action Required ...")

def setup_weather():
    weather_path = Path("weather_data/")
    if not weather_path.exists():
        PrettyCLI.tprint("No Weather Folder Detected. Generating ...")
        weather_path.mkdir(parents=True, exist_ok=True)
        makedirs(weather_path / "archive")
        makedirs(weather_path / "aurora")
        makedirs(weather_path / "graphcast")
        PrettyCLI.tprint("Weather Folder Successfully Created ...")
    else:
        # print("[!]    Weather Folder Detected! No Further Action Required ...")
        PrettyCLI.tprint("Weather Folder Detected! No Further Action Required ...")

def setup_folders() -> None:
    setup_log()
    setup_model()
    setup_prediction()
    setup_weather()