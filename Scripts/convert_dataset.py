from netCDF4 import Dataset
import numpy as np
import json

"""
file: convert_dataset

purpose:
 - convert data from the raw large NetCDF file to a reduced size JSON file
 - only select the variables we want
"""

# Processing constants
KELVIN = 271                # used to convert between Kelvin and Celcius
TOTAL_LAT = 180             # number of latitude int values on earth
TOTAL_LON = 360             # number of longitude int values on earth
LAT_LON_PRECISION = 4       # how much the lat/lon variable is divided (i.e. each integer lat/lon has 4 data points)

coordinates = [[0]*TOTAL_LON for _ in range(TOTAL_LAT)]     # 2D array with values for all coordinates

input_filename = 'EAR5-01-01-2020.nc'       # filename containing raw .nc data
ctd = Dataset(input_filename, 'r')          # Dataset object to interact with


# Pull the variables from the NetCDF file
lat = ctd.variables['latitude']
lon = ctd.variables['longitude']
land_sea_mask = ctd.variables['lsm']
ten_metre_U_wind_component = ctd.variables['u10']
ten_metre_V_wind_component = ctd.variables['v10']
two_metre_temperature = ctd.variables['t2m']
mean_sea_level_pressure = ctd.variables['msl']
mean_wave_direction = ctd.variables['mwd']
sea_surface_temperature = ctd.variables['sst']
total_cloud_cover = ctd.variables['tcc']


def mean(var, lat, lon):
    """
    Given a lat/long, calculate the mean of all data points within the lat/long,
    since our dataset stores lat long in increments of 0.25

    ie) mean(lat,lon + (lat+0.25),lon + (lat+0.5),lon + (lat+0.75...)....etc
    """

    mean = np.mean(var[0, lat:lat+LAT_LON_PRECISION, lon:lon+LAT_LON_PRECISION])

    # Workaround for masked values - might need a better solution in the future
    return -32767 if np.ma.is_masked(mean) else mean


# Iterate over all the lat/lon variables in the original dataset
for curr_lat in range(TOTAL_LAT):
    for curr_lon in range(TOTAL_LON):
        coordinates[curr_lat][curr_lon] = {
            'lat': curr_lat,
            'lon': curr_lon,
            'land_sea_mask': mean(land_sea_mask, curr_lat, curr_lon),
            'ten_metre_U_wind_component': mean(ten_metre_U_wind_component, curr_lat, curr_lon),
            'ten_metre_V_wind_component': mean(ten_metre_V_wind_component, curr_lat, curr_lon),
            'two_metre_temperature': mean(two_metre_temperature, curr_lat, curr_lon),
            'mean_sea_level_pressure': mean(mean_sea_level_pressure, curr_lat, curr_lon),
            'mean_wave_direction': mean(mean_wave_direction, curr_lat, curr_lon),
            'sea_surface_temperature': mean(sea_surface_temperature, curr_lat, curr_lon),
            'total_cloud_cover': mean(total_cloud_cover, curr_lat, curr_lon),
        }


# Save the converted data as a json file after processing
with open('converted_data.json', 'w') as outfile:
    json.dump(coordinates, outfile)
