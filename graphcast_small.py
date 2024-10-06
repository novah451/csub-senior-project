import datetime
import functools
from graphcast import autoregressive
from graphcast import casting
from graphcast import checkpoint
from graphcast import data_utils
from graphcast import graphcast
from graphcast import normalization
from graphcast import rollout
from graphcast import xarray_jax
from graphcast import xarray_tree
import haiku as hk
import isodate
import jax
import math
import numpy as np
import pandas as pd
from pysolar.radiation import get_radiation_direct
from pysolar.solar import get_altitude
import pytz
from typing import Dict
import xarray

# Initalizing required constants
pi = math.pi
gap = 6                                                     # 6 hour gap between each graphcast predicition
predicition_steps = 4                                       # Tells graphcast to make predicitions for 4 timestamps
watts_to_joules = 3600
first_predicition = datetime.datetime(2024, 1, 1, 18, 0)    # Timestamp for the first prediction
lat_range = range(-90, 91, 1)                               # Latitude range
lon_range = range(0, 360, 1)                                # Longitude range

# Fields to be fetched from the single-level source
single_level_fields = [
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    '2m_temperature',
    'geopotential',
    'land_sea_mask',
    'mean_sea_level_pressure',
    'toa_incident_solar_radiation',
    'total_precipitation'
]

# Fields to be fetched from the pressure-level source
pressure_level_fields = [
    'u_component_of_wind',
    'v_component_of_wind',
    'geopotential',
    'specific_humidity',
    'temperature',
    'vertical_velocity'
]

# Fields that GraphCast will be predicting/returning
prediction_fields = [
    'u_component_of_wind',
    'v_component_of_wind',
    'geopotential',
    'specific_humidity',
    'temperature',
    'vertical_velocity',
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    '2m_temperature',
    'mean_sea_level_pressure',
    'total_precipitation_6hr'
]

# A dictionary containing each coordinate a data variable requires
class AssignCoordinates:
    coordinates = {
        # Single-Level Variables
        '2m_temperature': ['batch', 'lon', 'lat', 'time'],
        'mean_sea_level_pressure': ['batch', 'lon', 'lat', 'time'],
        '10m_v_component_of_wind': ['batch', 'lon', 'lat', 'time'],
        '10m_u_component_of_wind': ['batch', 'lon', 'lat', 'time'],
        'total_precipitation_6hr': ['batch', 'lon', 'lat', 'time'],
        'toa_incident_solar_radiation': ['batch', 'lon', 'lat', 'time'],
        'geopotential_at_surface': ['lon', 'lat'],
        'land_sea_mask': ['lon', 'lat'],
        # Pressure-level Variables
        'temperature': ['batch', 'lon', 'lat', 'level', 'time'],
        'geopotential': ['batch', 'lon', 'lat', 'level', 'time'],
        'u_component_of_wind': ['batch', 'lon', 'lat', 'level', 'time'],
        'v_component_of_wind': ['batch', 'lon', 'lat', 'level', 'time'],
        'vertical_velocity': ['batch', 'lon', 'lat', 'level', 'time'],
        'specific_humidity': ['batch', 'lon', 'lat', 'level', 'time'],
        # Year and Day Progress
        'year_progress_cos': ['batch', 'time'],
        'year_progress_sin': ['batch', 'time'],
        'day_progress_cos': ['batch', 'lon', 'time'],
        'day_progress_sin': ['batch', 'lon', 'time'],
    }

# Load the model
with open(r'model/graphcast/params/GraphCast_small - ERA5 1979-2015 - resolution 1.0 - pressure levels 13 - mesh 2to5 - precipitation input and output.npz', 'rb') as model:
    ckpt = checkpoint.load(model, graphcast.CheckPoint)
    params = ckpt.params
    state = {}
    model_config = ckpt.model_config
    task_config = ckpt.task_config
    print("\nModel description:\n", ckpt.description)
    print("Model license:\n", ckpt.license)

# Load the normalization data
with open(r'model/graphcast/stats/diffs_stddev_by_level.nc', 'rb') as f:
    diffs_stddev_by_level = xarray.load_dataset(f).compute()
with open(r'model/graphcast/stats/mean_by_level.nc', 'rb') as f:
    mean_by_level = xarray.load_dataset(f).compute()
with open(r'model/graphcast/stats/stddev_by_level.nc', 'rb') as f:
    stddev_by_level = xarray.load_dataset(f).compute()

'''Build jitted functions, and possibly initialize random weights'''
# Constructs and wraps the GraphCast Predictor
def construct_wrapped_graphcast(model_config: graphcast.ModelConfig, task_config: graphcast.TaskConfig):
    # Deeper one-step predictor
    predictor = graphcast.GraphCast(model_config, task_config)

    # Modify inputs/outputs to 'graphcast.GraphCast' to handle conversion to from/to float32 to/from BFloat16
    predictor = casting.Bfloat16Cast(predictor)

    # Modify inputs/outputs to 'casting.BFloat16Cast' so the casting to/from BFloat16 happens after applying normalization to the inputs/targets
    predictor = normalization.InputsAndResiduals(
        predictor,
        diffs_stddev_by_level=diffs_stddev_by_level,
        mean_by_level=mean_by_level,
        stddev_by_level=stddev_by_level
    )

    # Wraps everything so the one-step model can produce trajectories
    predictor = autoregressive.Predictor(predictor, gradient_checkpointing=True)
    return predictor

@hk.transform_with_state
def run_forward(model_config, task_config, inputs, targets_template, forcings):
    predictor = construct_wrapped_graphcast(model_config, task_config)
    return predictor(inputs, targets_template=targets_template, forcings=forcings)

@hk.transform_with_state
def loss_fn(model_config, task_config, inputs, targets, forcings):
    predictor = construct_wrapped_graphcast(model_config, task_config)
    loss, diagnostics = predictor.loss(inputs, targets, forcings)
    return xarray_tree.map_structure(
        lambda x: xarray_jax.unwrap_data(x.mean(), require_jax=True), (loss, diagnostics)
    )

def grads_fn(params, state, model_config, task_config, inputs, targets, forcings):
    def _aux(params, state, i, t, f):
        (loss, diagnostics), next_state = loss_fn.apply(
            params, state, jax.random.PRNGKey(0), model_config, task_config, i, t, f
        )
        return loss, (diagnostics, next_state)
    (loss, (diagnostics, next_state)), grads = jax.value_and_grad(
        _aux, has_aux=True)(params, state, inputs, targets, forcings)
    return loss, diagnostics, next_state, grads

# Jax doesn't seem to like passing configs as args through the jit. 
# Passing it in via partial (instead of capture by closure) forces jax to invalidate the jit cache if you change configs
def with_configs(fn):
    return functools.partial(fn, model_config=model_config, task_config=task_config)

# Always pass params and state, so the usage below are simpler
def with_params(fn):
    return functools.partial(fn, params=params, state=state)

# Google's models aren't stateful, so the state is always empty.
# Therefore, just return the predictions.
# This is required by their rollout code, and generally simpler (their words, not mine)
def drop_state(fn):
    return lambda **kw: fn(**kw)[0]

init_jitted = jax.jit(with_configs(run_forward.init))
loss_fn_jitted = drop_state(with_params(jax.jit(with_configs(loss_fn.apply))))
grads_fn_jitted = with_params(jax.jit(with_configs(grads_fn)))
run_forward_jitted = drop_state(with_params(jax.jit(with_configs(run_forward.apply))))

# Needed to run the model (don't know why yet)
class Predictor:
    @classmethod
    def predict(cls, inputs, targets, forcings) -> xarray.Dataset:
        predictions = rollout.chunked_prediction(
            run_forward_jitted,
            rng=jax.random.PRNGKey(0),
            inputs=inputs,
            targets_template=targets,
            forcings=forcings
        )
        return predictions

# A utility function used for ease of coding
# Converting the variable to a datetime object
def toDatetime(dt) -> datetime.datetime:
    if isinstance(dt, datetime.date) and isinstance(dt, datetime.datetime):
        return dt
    elif isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        return datetime.datetime.combine(dt, datetime.datetime.min.time())
    elif isinstance(dt, str):
        if 'T' in dt:
            return isodate.parse_datetime(dt)
        else:
            return datetime.datetime.combine(isodate.parse_date(dt), datetime.datetime.min.time())

# Creating an array full of nan values.
def nans(*args) -> list:
    return np.full((args), np.nan)

# Adding or Subtracting time
def deltaTime(dt, **delta) -> datetime.datetime:
    return dt + datetime.timedelta(**delta)

# Adding a timezone to datetime.datetime variables
def addTimezone(dt, tz = pytz.UTC) -> datetime.datetime:
    dt = toDatetime(dt)
    if dt.tzinfo == None:
        return pytz.UTC.localize(dt).astimezone(tz)
    else:
        return dt.astimezone(tz)

# Retrieving the single and pressure level values from files
def getSingleAndPressureValues():
    # Obtain single level data; rename columns for graphcast to work
    print("    [+] Retrieving single level data")
    singlelevel = xarray.open_dataset('weather_data/graphcast/2024-01-01-single-level.nc', engine='netcdf4').to_dataframe()
    singlelevel = singlelevel.rename(columns = {col:single_level_fields[ind] for ind, col in enumerate(singlelevel.columns.values[2:])})
    singlelevel = singlelevel.rename(columns = {'geopotential': 'geopotential_at_surface'})
    singlelevel = singlelevel.drop(columns=['number', 'expver'])

    # Calculate the sum of the last 6 hours of rainfall
    print("    [+] Calculating sum of rainfall/inserting into dataframe")
    singlelevel = singlelevel.sort_index()
    singlelevel['total_precipitation_6hr'] = singlelevel.groupby(level=[0, 1])['total_precipitation'].rolling(window = 6, min_periods = 1).sum().reset_index(level=[0, 1], drop=True)
    singlelevel.pop('total_precipitation')

    # Obtain pressure level data; fix some stuff with it
    print("    [+] Retrieving pressure level data")
    pressurelevel = xarray.open_dataset('weather_data/graphcast/2024-01-01-pressure-level.nc', engine='netcdf4').to_dataframe()
    pressurelevel = pressurelevel.rename(columns = {col:pressure_level_fields[ind] for ind, col in enumerate(pressurelevel.columns.values[2:])})
    pressurelevel = pressurelevel.drop(columns=['number', 'expver'])

    print("    [+] Returning both single-and-pressure level data")
    return singlelevel, pressurelevel

# Adding sin and cos of the year progress
def addYearProgress(secs, data):
    progress = data_utils.get_year_progress(secs)
    data['year_progress_sin'] = math.sin(2 * pi * progress)
    data['year_progress_cos'] = math.cos(2 * pi * progress)

    return data

# Adding sin and cos for the day progress
def addDayProgress(secs, lon:str, data:pd.DataFrame):
    lons = data.index.get_level_values(lon).unique()
    progress:np.ndarray = data_utils.get_day_progress(secs, np.array(lons))
    prxlon = {lon:prog for lon, prog in list(zip(list(lons), progress.tolist()))}
    data['day_progress_sin'] = data.index.get_level_values(lon).map(lambda x: math.sin(2 * pi * prxlon[x]))
    data['day_progress_cos'] = data.index.get_level_values(lon).map(lambda x: math.cos(2 * pi * prxlon[x]))

    return data

# Adding day and year progress
def integrateProgress(data:pd.DataFrame):
    # print(f"{data.index}\n\n")
    for dt in data.index.get_level_values('time').unique():
        seconds_since_epoch = toDatetime(dt).timestamp()
        data = addYearProgress(seconds_since_epoch, data)
        data = addDayProgress(seconds_since_epoch, 'longitude' if 'longitude' in data.index.names else 'lon', data)
    
    return data

# Getting the solar radiation value with longitude, latitude, and timestamp
def getSolarRadiation(longitude, latitude, dt):
    altitude_degrees = get_altitude(latitude, longitude, addTimezone(dt))
    solar_radiation = get_radiation_direct(dt, altitude_degrees) if altitude_degrees > 0 else 0

    return solar_radiation * watts_to_joules

# Calculating the solar radiation values for timestamps to be predicted
def integrateSolarRadiation(data:pd.DataFrame):
    dates = list(data.index.get_level_values('time').unique())
    coords = [[lat, lon] for lat in lat_range for lon in lon_range]
    values = []

    # For each point of data, get the solar radiation value at a particular coordinate
    for dt in dates:
        values.extend(list(map(lambda coord: {'time': dt, 'lon': coord[1], 'lat': coord[0], 'toa_incident_solar_radiation': getSolarRadiation(coord[1], coord[0], dt)}, coords)))

    values = pd.DataFrame(values).set_index(keys = ['lat', 'lon', 'time'])

    return pd.merge(data, values, left_index=True, right_index=True, how='inner')

# Parsing through each data variable and removing unnecessary indices
def modifyCoordinates(data:xarray.Dataset):
    for var in list(data.data_vars):
        varArray:xarray.DataArray = data[var]
        nonIndices = list(set(list(varArray.coords)).difference(set(AssignCoordinates.coordinates[var])))
        data[var] = varArray.isel(**{coord: 0 for coord in nonIndices})

    data = data.drop_vars('batch')

    return data

def makeXarray(data:pd.DataFrame) -> xarray.Dataset:
    data = data.to_xarray()
    data = modifyCoordinates(data)

    return data

# Adding batch field and renaming some others
def formatData(data:pd.DataFrame) -> pd.DataFrame:
    data = data.rename_axis(index = {'latitude': 'lat', 'longitude': 'lon', 'valid_time': 'time', 'pressure_level': 'level'})
    if 'batch' not in data.index.names:
        data['batch'] = 1
        data = data.set_index('batch', append=True)
    
    return data

def getTargets(dt, data:pd.DataFrame):
    # Creating an array consisting of unique values of each index
    lat, lon, levels, batch = sorted(data.index.get_level_values('lat').unique().tolist()), sorted(data.index.get_level_values('lon').unique().tolist()), sorted(data.index.get_level_values('level').unique().tolist()), data.index.get_level_values('batch').unique().tolist()
    time = [deltaTime(dt, hours = days * gap) for days in range(predicition_steps)]
    target = xarray.Dataset({field: (['lat', 'lon', 'level', 'time'], nans(len(lat), len(lon), len(levels), len(time))) for field in prediction_fields}, coords = {'lat': lat, 'lon': lon, 'level': levels, 'time': time, 'batch': batch})

    return target.to_dataframe()

def getForcings(data:pd.DataFrame):
    # Since forcings data does not contain batch as an index, it is dropped.
    # So are all the columns, since forcings data only has 5, which will be created.
    forcingdf = data.reset_index(level = "level", drop=True).drop(labels=prediction_fields, axis=1)

    # Keeping only the unique indices.
    forcingdf = pd.DataFrame(index = forcingdf.index.drop_duplicates(keep='first'))

    # Adding the sin and cos of day and year progress.
    # Functions are included in the creation of inputs data section.
    forcingdf = integrateProgress(forcingdf)

    print("This part may take a while. Please hold ... \n\n")

    # Integrating the solar radiation values.
    forcingdf = integrateSolarRadiation(forcingdf)

    return forcingdf

if __name__ == '__main__':
    values:Dict[str, xarray.Dataset] = {}

    single, pressure = getSingleAndPressureValues()

    values['inputs'] = pd.merge(pressure, single, left_index=True, right_index=True, how='inner')
    values['inputs'] = formatData(values['inputs'])
    values['inputs'] = integrateProgress(values['inputs'])

    values['targets'] = getTargets(first_predicition, values['inputs'])
    values['forcings'] = getForcings(values['targets'])

    values = {value:makeXarray(values[value]) for value in values}

    # HOLY JESUS CHRIST IT WORKS.
    # Problem: I still don't know how the hell it does anything.
    predictions = Predictor.predict(values['inputs'], values['targets'], values['forcings'])
    predictions.to_dataframe().to_csv('predictions/graphcast/predictions.csv', sep=',')

    print("This file works!")