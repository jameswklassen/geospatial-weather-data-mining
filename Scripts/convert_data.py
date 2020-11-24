from netCDF4 import Dataset
import numpy as np
import json

def mean(var, lat, lon, howmany):
    mean = np.mean(var[0,lat:lat+howmany, lon:lon+howmany])

    # Workaround for masked values - might need a better solution in the future
    return -32767 if np.ma.is_masked(mean) else mean

filename = 'EAR5-01-01-2020.nc'

ctd = Dataset(filename, 'r')

NUM_SLICES = 4
SLICE_SIZE = 0.25

KELVIN = 271

TOTAL_LAT = 180
TOTAL_LON = 360

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


coordinates = [[0]*TOTAL_LON for _ in range(TOTAL_LAT)]


count = 0
MAX = 1000
for curr_lat in range(TOTAL_LAT):

    if count > MAX:
        break
    for curr_lon in range(TOTAL_LON):
        if count > MAX:
            break
        count += 1

        coordinates[curr_lat][curr_lon] = {
            'lat': curr_lat,
            'lon': curr_lon,
            'land_sea_mask': mean(land_sea_mask, curr_lat, curr_lon, NUM_SLICES),
            'ten_metre_U_wind_component': mean(ten_metre_U_wind_component, curr_lat, curr_lon, NUM_SLICES),
            'ten_metre_V_wind_component': mean(ten_metre_V_wind_component, curr_lat, curr_lon, NUM_SLICES),
            'two_metre_temperature': mean(two_metre_temperature, curr_lat, curr_lon, NUM_SLICES),
            'mean_sea_level_pressure': mean(mean_sea_level_pressure, curr_lat, curr_lon, NUM_SLICES),
            'mean_wave_direction': mean(mean_wave_direction, curr_lat, curr_lon, NUM_SLICES),
            'sea_surface_temperature': mean(sea_surface_temperature, curr_lat, curr_lon, NUM_SLICES),
            'total_cloud_cover': mean(total_cloud_cover, curr_lat, curr_lon, NUM_SLICES),
        }

print(coordinates[0])

# Save it once we're done processing
with open('converted_data.json', 'w') as outfile:
    json.dump(coordinates, outfile)    
