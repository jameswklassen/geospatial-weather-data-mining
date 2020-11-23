from random import randint
from netCDF4 import Dataset
import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib import colors, cm
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

DATA_FILENAME = 'EAR5-01-01-2020.nc'

OUTPUT_DIR = 'output'
OUTPUT_FORMATS = ['svg', 'png']

NUM_POINTS = 1000
MARKER_SIZE = 0.5

KELVIN = 271

width = 30


def save_file(name):
    """Save the current plot as an .svg in the image directory"""

    for output_format in OUTPUT_FORMATS:
        path = f"{OUTPUT_DIR}/{name}.{output_format}"
        print(f"Writing {path}")
        plt.tight_layout(w_pad=2)
        plt.savefig(path, format=output_format, bbox_inches='tight')


# Open the file
try:
    ctd = Dataset(DATA_FILENAME, 'r')
except FileNotFoundError:
    print(f"File {DATA_FILENAME} not found")
    exit()

# Pull interesting variables from the file
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


# Iterate over these data points to plot
DATA_POINTS = {
    'sea_surface_temperature': {
        'data': sea_surface_temperature,
        'cmap': cm.coolwarm,
        'min': 0 + KELVIN,      # since temperature data is in kelvin
        'max': 30 + KELVIN,
    },
    'sea_level_pressure': {
        'data': mean_sea_level_pressure,
        'cmap': cm.BuPu,
        'min': 96169.8125,
        'max': 104715.8125,
    },
    'total_cloud_cover': {
        'data': total_cloud_cover,
        'cmap': cm.Blues,
        'min': 0.0,
        'max': 1.0,
    },
}


mpl.rcParams['lines.markersize'] = MARKER_SIZE


for index, datapoint in enumerate(DATA_POINTS.items()):
    print(f"Data point: {datapoint[0]}")

    plt.suptitle(datapoint[0], fontsize=16)

    data = datapoint[1]

    map_plot = plt.axes(projection=ccrs.PlateCarree(), label=datapoint[0])
    grid_lines = map_plot.gridlines()
    grid_lines.xformatter = LONGITUDE_FORMATTER
    grid_lines.yformatter = LATITUDE_FORMATTER
    map_plot.coastlines()

    norm = colors.Normalize(vmin=data['min'], vmax=data['max'])

    for point in range(NUM_POINTS):
        i = randint(1, len(lat)-1)
        j = randint(1, len(lon)-1)
        curr_lat = lat[i]
        curr_lon = lon[j]

        map_plot.scatter(
            curr_lon,
            curr_lat,
            marker=",",
            color=data['cmap'](norm(data['data'][0, i, j])),
            transform=ccrs.PlateCarree()
        )

        complete = int(((point+1)/NUM_POINTS)*width)
        print(
            '['
            f"{'=' * complete}"
            f"{' ' * (width - complete - 1)}"
            f"] ({point + 1}/{NUM_POINTS})",
            end='\r'
        )

    print()

    sm = plt.cm.ScalarMappable(cmap=data['cmap'], norm=norm)
    plt.colorbar(sm, shrink=0.5)
    save_file(f"{datapoint[0]}_{NUM_POINTS}")

exit()
