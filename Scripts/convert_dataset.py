from netCDF4 import Dataset
import numpy as np
import json
import multiprocessing as mp
from consts import TOTAL_LAT, TOTAL_LON, KELVIN, INPUT_FILENAME, VARIABLES


"""
file: convert_dataset

purpose:
 - convert data from the raw large NetCDF file to a reduced size JSON file
 - only select the variables we want
"""

LAT_LON_PRECISION = 4       # how many pieces lat/lon is divided into (i.e. each integer lat/lon has 4 data points)
MASK_THRESHOLD = 5          # might need to tweak this, the values seem to be within 0-256, but not fully understood yet


def mean(var, lat, lon):
    """
    Given a lat/long, calculate the mean of all data points within the lat/long,
    since our dataset stores lat long in increments of 0.25

    ie) mean(lat,lon + (lat+0.25),lon + (lat+0.5),lon + (lat+0.75...)....etc
    """

    values = var[0, (LAT_LON_PRECISION*lat):(LAT_LON_PRECISION*(lat+LAT_LON_PRECISION)), (LAT_LON_PRECISION*lon):(LAT_LON_PRECISION*(lon+LAT_LON_PRECISION))]

    # if there are too many masked values return null
    if np.ma.count_masked(values) > MASK_THRESHOLD:
        return None

    return np.mean(values)


def process_data(lat_start, lat_end):
    """
    Process data over the lat range (lat_start, lat_end)
    """

    print(f"start: {lat_start} end: {lat_end}")

    data = {var: [['-']*TOTAL_LON for _ in range(TOTAL_LAT)] for var in VARIABLES}

    ctd = Dataset(INPUT_FILENAME, 'r')

    ten_metre_U_wind_component = ctd.variables['u10']
    ten_metre_V_wind_component = ctd.variables['v10']
    two_metre_temperature = ctd.variables['t2m']
    mean_sea_level_pressure = ctd.variables['msl']
    sea_surface_temperature = ctd.variables['sst']
    total_cloud_cover = ctd.variables['tcc']

    for lat in range(lat_start, lat_end):
        for lon in range(TOTAL_LON):
            mean_sea_surface_temperature = mean(sea_surface_temperature, lat, lon)

            # if sea surface temp is None:
            # don't care about any other data -> set all to None
            if mean_sea_surface_temperature is None:
                for variable in VARIABLES:
                    data[variable][lat][lon] = None
            else:
                data['ten_metre_U_wind_component'][lat][lon] = mean(ten_metre_U_wind_component, lat, lon)
                data['ten_metre_V_wind_component'][lat][lon] = mean(ten_metre_V_wind_component, lat, lon)
                data['two_metre_temperature'][lat][lon] = mean(two_metre_temperature, lat, lon) - KELVIN
                data['mean_sea_level_pressure'][lat][lon] = mean(mean_sea_level_pressure, lat, lon) / 1000
                data['sea_surface_temperature'][lat][lon] = mean_sea_surface_temperature - KELVIN
                data['total_cloud_cover'][lat][lon] = mean(total_cloud_cover, lat, lon)

    return data


if __name__ == '__main__':
    # data dictionary to store each data point as an array of values
    data = {var: [['-']*TOTAL_LON for _ in range(TOTAL_LAT)] for var in VARIABLES}

    pool = mp.Pool(mp.cpu_count())

    # Pool.starmap is multithreading magic
    results = pool.starmap(process_data, [(i, i+10) for i in range(0, TOTAL_LAT, 10)])

    # Merge all the partial results and we're done
    for result in results:
        for var in VARIABLES:
            for lat in range(TOTAL_LAT):
                for lon in range(TOTAL_LON):
                    if result[var][lat][lon] != '-':
                        data[var][lat][lon] = result[var][lat][lon]

    # Save the converted data as a json file after processing
    with open('converted_data.json', 'w') as outfile:
        json.dump(data, outfile)
