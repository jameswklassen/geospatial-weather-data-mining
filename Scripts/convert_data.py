from netCDF4 import Dataset
import numpy as np
import json
import multiprocessing as mp

KELVIN = 273.15
TOTAL_LAT = 180
TOTAL_LON = 360
NUM_SLICES = 4
SLICE_SIZE = 0.25

variables = [
    'ten_metre_U_wind_component',
    'ten_metre_V_wind_component',
    'two_metre_temperature',
    'mean_sea_level_pressure',
    'mean_wave_direction',
    'sea_surface_temperature',
    'total_cloud_cover'
]

def mean(var, lat, lon, howmany):
    mean = np.mean(var[0,lat:lat+howmany, lon:lon+howmany])

    # Workaround for masked values - might need a better solution in the future
    return None if np.ma.is_masked(mean) else mean

def process_data(lat_start, lat_end):
    print(f"start: {lat_start} end: {lat_end}")
    
    coordinates = {variables[i]:[['-']*TOTAL_LON for _ in range(TOTAL_LAT)] for i in range(len(variables))}

    filename = 'EAR5-01-01-2020.nc'
    ctd = Dataset(filename, 'r')

    ten_metre_U_wind_component = ctd.variables['u10']
    ten_metre_V_wind_component = ctd.variables['v10']
    two_metre_temperature = ctd.variables['t2m']
    mean_sea_level_pressure = ctd.variables['msl']
    mean_wave_direction = ctd.variables['mwd']
    sea_surface_temperature = ctd.variables['sst']
    total_cloud_cover = ctd.variables['tcc']

    for curr_lat in range(lat_start, lat_end):
        for curr_lon in range(TOTAL_LON):
            x = mean(sea_surface_temperature, curr_lat, curr_lon, NUM_SLICES)
            if x is None:
                coordinates['ten_metre_U_wind_component'][curr_lat][curr_lon] = None
                coordinates['ten_metre_V_wind_component'][curr_lat][curr_lon] = None
                coordinates['two_metre_temperature'][curr_lat][curr_lon] = None
                coordinates['mean_sea_level_pressure'][curr_lat][curr_lon] = None
                coordinates['mean_wave_direction'][curr_lat][curr_lon] = None
                coordinates['sea_surface_temperature'][curr_lat][curr_lon] = None
                coordinates['total_cloud_cover'][curr_lat][curr_lon] = None
            else:
                coordinates['ten_metre_U_wind_component'][curr_lat][curr_lon] = mean(ten_metre_U_wind_component, curr_lat, curr_lon, NUM_SLICES)
                coordinates['ten_metre_V_wind_component'][curr_lat][curr_lon] = mean(ten_metre_V_wind_component, curr_lat, curr_lon, NUM_SLICES)
                coordinates['two_metre_temperature'][curr_lat][curr_lon] = mean(two_metre_temperature, curr_lat, curr_lon, NUM_SLICES) - KELVIN
                coordinates['mean_sea_level_pressure'][curr_lat][curr_lon] = mean(mean_sea_level_pressure, curr_lat, curr_lon, NUM_SLICES) / 1000
                coordinates['mean_wave_direction'][curr_lat][curr_lon] = mean(mean_wave_direction, curr_lat, curr_lon, NUM_SLICES)
                coordinates['sea_surface_temperature'][curr_lat][curr_lon] = x - KELVIN
                coordinates['total_cloud_cover'][curr_lat][curr_lon] = mean(total_cloud_cover, curr_lat, curr_lon, NUM_SLICES)

    return coordinates

pool = mp.Pool(mp.cpu_count())

# Pool.starmap is multithreading magic
results = pool.starmap(process_data, [(i, i+10) for i in range(0,TOTAL_LAT,10)])

coordinates = {variables[i]:[['-']*TOTAL_LON for _ in range(TOTAL_LAT)] for i in range(len(variables))}

# Merge all the partial results and we're done
for result in results:
    for var in variables:
        for i in range(TOTAL_LAT):
            for j in range(TOTAL_LON):
                if result[var][i][j] != '-':
                    coordinates[var][i][j] = result[var][i][j]

# Save it once we're done processing
with open('converted_data.json', 'w') as outfile:
    json.dump(coordinates, outfile)
