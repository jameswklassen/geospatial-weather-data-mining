import os

TOTAL_LON = 360             # number of longitude int values on earth
TOTAL_LAT = 180             # number of latitude int values on earth
DAYS_IN_YEAR = 365                  # number of days in a year
KELVIN = 273.15             # used to convert between Kelvin and Celsius

DEFAULT_K = 25
DATA_DIRECTORY = os.getcwd() + '/../Data'
OUTPUT_DIRECTORY = 'output'
CONVERTED_DIRECTORY = OUTPUT_DIRECTORY + '/converted'
CLUSTERED_DIRECTORY = OUTPUT_DIRECTORY + '/clustered'
FCLUSTERED_DIRECTORY = OUTPUT_DIRECTORY + '/fclustered'

VARIABLES = [
    'two_metre_temperature',
    'mean_sea_level_pressure',
    'sea_surface_temperature',
    'total_cloud_cover'
]
