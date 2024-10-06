from pathlib import Path
from os import makedirs
from google.cloud import storage

weather_path = Path("weather_data/")
if not weather_path.exists():
    weather_path.mkdir(parents=True, exist_ok=True)
    makedirs(weather_path / "archive")
    makedirs(weather_path / "aurora")
    makedirs(weather_path / "graphcast")

prediction_path = Path("predictions/")
if not prediction_path.exists():
    prediction_path.mkdir(parents=True, exist_ok=True)
    makedirs(prediction_path / "aurora")
    makedirs(prediction_path / "graphcast")

log_path = Path("log/")
if not log_path.exists():
    log_path.mkdir(parents=True, exist_ok=True)
    makedirs(log_path / "aurora")
    makedirs(log_path / "graphcast")

model_path = Path("model/graphcast/params")
if not model_path.exists():
    model_path.mkdir(parents=True, exist_ok=True)
    # Initialise a client
    storage_client = storage.Client.create_anonymous_client()
    # Create a bucket object for our bucket
    bucket = storage_client.get_bucket("dm_graphcast")
    # Create a blob object from the filepath
    blob = bucket.blob("params/GraphCast_small - ERA5 1979-2015 - resolution 1.0 - pressure levels 13 - mesh 2to5 - precipitation input and output.npz")
    # Download the file to a destination
    blob.download_to_filename(model_path / "GraphCast_small - ERA5 1979-2015 - resolution 1.0 - pressure levels 13 - mesh 2to5 - precipitation input and output.npz")
