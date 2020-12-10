import matplotlib.pyplot as plt
from matplotlib import colors, cm
import cartopy.crs as ccrs
import json
import numpy as np

from netCDF4 import Dataset

from consts import TOTAL_LAT, TOTAL_LON, INPUT_FILENAME

JSON_FILENAME = 'converted_data.json'

OUTPUT_DIR = 'output'
OUTPUT_FORMATS = ['png']

MARKER_SIZE = 3
MARKER = ","

COLOR_LEVELS = 60
CORNER_SMOOTHING = True

ctd = Dataset(INPUT_FILENAME, 'r')          # Dataset object to interact with

lons = list(range(TOTAL_LON))
lats = list(range(int(TOTAL_LAT/2), int(-TOTAL_LAT/2), -1))


def save_file(name):
    """Save the current plot as an .svg in the image directory"""

    for output_format in OUTPUT_FORMATS:
        path = f"{OUTPUT_DIR}/{name}.{output_format}"
        print(f"Writing {path}")
        plt.savefig(path, format=output_format, bbox_inches='tight', dpi=500)


def color_map(var):
    if var == 'mean_sea_level_pressure':
        return cm.BuPu
    elif var == 'total_cloud_cover':
        return cm.get_cmap('Blues_r')
    else:
        return cm.jet


def plot_thing(data, title, cmap):
    plt.suptitle(title, fontsize=16)
    ax = plt.axes(projection=ccrs.PlateCarree(), label=title)
    plt.contourf(
        lons,
        lats,
        data,
        COLOR_LEVELS,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        corner_mask=CORNER_SMOOTHING,
    )

    ax.coastlines()

    norm = colors.Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(sm, shrink=0.5)

    save_file(title)


if __name__ == '__main__':

    # Open our converted data and read it in
    with open(JSON_FILENAME, 'r') as my_file:
        json_data = my_file.read()
        data = json.loads(json_data)

    for variable in data.keys():
        plot_thing(
            np.array(data[variable], dtype=np.float64),
            variable,
            color_map(variable)
        )
