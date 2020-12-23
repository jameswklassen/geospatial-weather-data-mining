import os

YEAR = 2019

TOTAL_LON = 360             # number of longitude int values on earth
TOTAL_LAT = 180             # number of latitude int values on earth
DAYS_IN_YEAR = 365                  # number of days in a year
KELVIN = 273.15             # used to convert between Kelvin and Celsius

DEFAULT_K = 25
DATA_DIRECTORY = os.getcwd() + '/../Data'
CONVERTED_DIRECTORY = DATA_DIRECTORY + '/converted'
CLUSTERED_DIRECTORY = DATA_DIRECTORY + '/clustered'
FCLUSTERED_DIRECTORY = DATA_DIRECTORY + '/fclustered'
VISUALS_DIRECTORY = os.getcwd() + '/../Visuals'

VARIABLES = [
    'two_metre_temperature',
    'mean_sea_level_pressure',
    'sea_surface_temperature',
]

DEG = u'\N{DEGREE SIGN}'
