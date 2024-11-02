import cdsapi
from pathlib import Path
from sys import argv

if argv[1] != "aurora" and argv[1] != "graphcast":
    print("Command line argument is not a valid option, try again\n")
    exit(0)

# Data will be downloaded here
download_path = Path(f"weather_data/{argv[1]}")

# Connect to the CDS API
c = cdsapi.Client()

def gather_data_for_graphcast():
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

    # 37 pressure levels that will be covered
    pressure_levels = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 125, 
                       150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 550, 600,
                       650, 700, 750, 775, 800, 825, 850, 875, 900, 925, 950, 975, 1000]

    # Download the single-level variables.
    if not (download_path / "2024-01-01-single-level.nc").exists():
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": single_level_fields,
                # "grid": "1.0/1.0",
                "year": ["2024"],
                "month": ["1"],
                "day": ["1"],
                "time": ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00"],
                "data_format": "netcdf",
            },
            str(download_path / "2024-01-01-single-level.nc"),
        )
        print("Single-Level Variables Downloaded!")
    else:
        print("Single-Level Variables Already Downloaded!")

    # Download the pressure-level variables
    if not (download_path / "2024-01-01-pressure-level.nc").exists():
        c.retrieve(
            "reanalysis-era5-pressure-levels",
            {
                "product_type": "reanalysis",
                "variable": pressure_level_fields,
                # "grid": "1.0/1.0",
                "year": ["2024"],
                "month": ["1"],
                "day": ["1"],
                "time": ["06:00", "12:00"],
                "pressure_level": pressure_levels,
                "data_format": "netcdf",
            },
            str(download_path / "2024-01-01-pressure-level.nc"),
        )
        print("Pressure-Level Variables Downloaded!")
    else:
        print("Pressure-Level Variables Already Downloaded!")

def gather_data_for_aurora():
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
    if not (download_path / "static.nc").exists():
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": static_fields,
                "year": "2023",
                "month": "01",
                "day": "01",
                "time": "00:00",
                "format": "netcdf",
            },
            str(download_path / "static.nc"),
        )
        print("Static variables downloaded!")
    else:
        print("Static variables already downloaded!")
    
    # Download the surface-level variables.
    if not (download_path / "2023-01-01-surface-level.nc").exists():
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": surface_level_fields,
                "year": "2023",
                "month": "01",
                "day": "01",
                "time": ["00:00", "06:00", "12:00", "18:00"],
                "format": "netcdf",
            },
            str(download_path / "2023-01-01-surface-level.nc"),
        )
        print("Surface-level variables downloaded!")
    else:
        print("Surface-level variables already downloaded!")
    
    # Download the atmospheric variables.
    if not (download_path / "2023-01-01-atmospheric.nc").exists():
        c.retrieve(
            "reanalysis-era5-pressure-levels",
            {
                "product_type": "reanalysis",
                "variable": pressure_level_fields,
                "pressure_level": pressure_levels,
                "year": "2023",
                "month": "01",
                "day": "01",
                "time": ["00:00", "06:00", "12:00", "18:00"],
                "format": "netcdf",
            },
            str(download_path / "2023-01-01-atmospheric.nc"),
        )
        print("Atmospheric variables downloaded!")
    else:
        print("Atmospheric variables already downloaded!")

if __name__ == "__main__":
    if argv[1] == "aurora":
        gather_data_for_aurora()
    elif argv[1] == "graphcast":
        gather_data_for_graphcast()