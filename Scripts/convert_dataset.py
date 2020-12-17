import os
import errno
import json
import argparse
from netCDF4 import Dataset
import numpy as np
import multiprocessing as mp
from consts import TOTAL_LAT, TOTAL_LON, DAYS_IN_YEAR, KELVIN, VARIABLES, DATA_DIRECTORY, OUTPUT_DIRECTORY

"""
file: convert_dataset

purpose:
 - convert data from the raw large NetCDF file to a reduced size JSON file
 - only select the variables we want
"""

DEFAULT_INPUT_FILENAME = DATA_DIRECTORY + '/EAR5-01-01-2020.nc'
DEFAULT_CONVERSION_DIRECTORY = OUTPUT_DIRECTORY + '/converted'

COMPRESS = True

LAT_LON_PRECISION = 4       # how many pieces lat/lon is divided into (i.e. each integer lat/lon has 4 data points)
MASK_THRESHOLD = 5          # might need to tweak this, the values seem to be within 0-256, but not fully understood yet


def mean(var, day, lat, lon):
    """
    Given date & lat/long, calculate the mean of all data points within the lat/long for that date,
    since our dataset stores lat long in increments of 0.25

    ie) mean(lat,lon + (lat+0.25),lon + (lat+0.5),lon + (lat+0.75...)....etc
    """

    values = var[day, (LAT_LON_PRECISION*lat):(LAT_LON_PRECISION*(lat+LAT_LON_PRECISION)), (LAT_LON_PRECISION*lon):(LAT_LON_PRECISION*(lon+LAT_LON_PRECISION))]

    # if there are too many masked values return null
    if np.ma.count_masked(values) > MASK_THRESHOLD:
        return None

    return np.mean(values)


def process_data(input_filename, day, lat_start, lat_end):
    """
    Process data over the lat range (lat_start, lat_end)
    """

    print(f"{lat_start:<3} to {lat_end:<3}")

    data = {var: [['-']*TOTAL_LON for _ in range(TOTAL_LAT)] for var in VARIABLES}

    ctd = Dataset(input_filename, 'r')

    two_metre_temperature = ctd.variables['t2m']
    mean_sea_level_pressure = ctd.variables['msl']
    sea_surface_temperature = ctd.variables['sst']
    total_cloud_cover = ctd.variables['tcc']

    for lat in range(lat_start, lat_end):
        for lon in range(TOTAL_LON):
            mean_sea_surface_temperature = mean(sea_surface_temperature, day, lat, lon)

            # if sea surface temp is None:
            # don't care about any other data -> set all to None
            if mean_sea_surface_temperature is None:
                for variable in VARIABLES:
                    data[variable][lat][lon] = None
            else:
                data['two_metre_temperature'][lat][lon] = mean(two_metre_temperature, day, lat, lon) - KELVIN
                data['mean_sea_level_pressure'][lat][lon] = mean(mean_sea_level_pressure, day, lat, lon) / 1000
                data['sea_surface_temperature'][lat][lon] = mean_sea_surface_temperature - KELVIN
                data['total_cloud_cover'][lat][lon] = mean(total_cloud_cover, day, lat, lon)

    return data


def convert_data_for_day(day):
    print("Converting data for", day)

    data = {var: [['-']*TOTAL_LON for _ in range(TOTAL_LAT)] for var in VARIABLES}

    pool = mp.Pool(mp.cpu_count())

    # Pool.starmap is multithreading magic
    results = pool.starmap(process_data, [(INPUT_FILENAME, day, i, i+10) for i in range(0, TOTAL_LAT, 10)])

    # Merge all the partial results and we're done
    for result in results:
        for var in VARIABLES:
            for lat in range(TOTAL_LAT):
                for lon in range(TOTAL_LON):
                    if result[var][lat][lon] != '-':
                        data[var][lat][lon] = result[var][lat][lon]

    try:
        os.makedirs(DEFAULT_CONVERSION_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    with open(f"{DEFAULT_CONVERSION_DIRECTORY}/{day}.json", 'w') as outfile:
        json.dump(data, outfile)


def init():
    try:
        os.makedirs(OUTPUT_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    try:
        os.makedirs(DEFAULT_CONVERSION_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input file", default=DEFAULT_INPUT_FILENAME)
    parser.add_argument("-c", "--compress", type=bool, help="Compress", default=True)

    args = parser.parse_args()

    INPUT_FILENAME = args.input
    OUTPUT_FILENAME = args.output

    print("input file", INPUT_FILENAME)
    print("output file:", OUTPUT_FILENAME)
    print("compress", args.compress)

    init()

    ctd = Dataset(INPUT_FILENAME, 'r')

    for day in range(DAYS_IN_YEAR):
        convert_data_for_day(day)
