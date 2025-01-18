import cdsapi
from pathlib import Path
from sys import argv

def gather_data_for_aurora(download_path: Path, c: cdsapi.Client):
    # Static Variables to be fetched from the single-level source
    static_fields = [
        'geopotential',
        'land_sea_mask',
        'soil_type'
    ]

    # Surface-level Variables to be fetched from the single-level source
    surface_level_fields = [
        '10m_u_component_of_wind',
        '10m_v_component_of_wind',
        '2m_temperature',
        'mean_sea_level_pressure',
    ]

    # Atmospheric variables to be fetched from the pressure-level source
    pressure_level_fields = [
        'u_component_of_wind',
        'v_component_of_wind',
        'geopotential',
        'specific_humidity',
        'temperature',
    ]

    # 13 pressure levels that will be covered
    pressure_levels = [50, 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000]    

    # Download the static variables.
    if not (download_path / f"{argv[1]}-{argv[2]}-{argv[3]}-static.nc").exists():
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": static_fields,
                "year": argv[1],
                "month": argv[2],
                "day": argv[3],
                "time": "00:00",
                "area": [37, 239.25, 34, 243],
                "format": "netcdf",
            },
            str(download_path / f"{argv[1]}-{argv[2]}-{argv[3]}-static.nc"),
        )
        print("Static variables downloaded!")
    else:
        print("Static variables already downloaded!")
    
    # Download the surface-level variables.
    if not (download_path / f"{argv[1]}-{argv[2]}-{argv[3]}-surface-level.nc").exists():
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": surface_level_fields,
                "year": argv[1],
                "month": argv[2],
                "day": argv[3],
                "time": ["00:00", "06:00"],
                "area": [37, 239.25, 34, 243],
                "format": "netcdf",
            },
            str(download_path / f"{argv[1]}-{argv[2]}-{argv[3]}-surface-level.nc"),
        )
        print("Surface-level variables downloaded!")
    else:
        print("Surface-level variables already downloaded!")
    
    # Download the atmospheric variables.
    if not (download_path / f"{argv[1]}-{argv[2]}-{argv[3]}-atmospheric.nc").exists():
        c.retrieve(
            "reanalysis-era5-pressure-levels",
            {
                "product_type": "reanalysis",
                "variable": pressure_level_fields,
                "pressure_level": pressure_levels,
                "year": argv[1],
                "month": argv[2],
                "day": argv[3],
                "time": ["00:00", "06:00"],
                "area": [37, 239.25, 34, 243],
                "format": "netcdf",
            },
            str(download_path / f"{argv[1]}-{argv[2]}-{argv[3]}-atmospheric.nc"),
        )
        print("Atmospheric variables downloaded!")
    else:
        print("Atmospheric variables already downloaded!")

if __name__ == "__main__":
    # Data will be downloaded here
    download_path = Path(f"weather_data/aurora")

    # Connect to the CDS API
    c = cdsapi.Client()

    # Download weather data based on datetime input
    gather_data_for_aurora(download_path, c)