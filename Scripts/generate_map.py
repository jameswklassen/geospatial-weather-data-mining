import os
import errno
from datetime import datetime
import argparse
from datetime import date
import matplotlib.pyplot as plt
from matplotlib import colors, cm
import cartopy.crs as ccrs
import json
import numpy as np

from netCDF4 import Dataset

from consts import TOTAL_LAT, TOTAL_LON, OUTPUT_DIRECTORY

JSON_FILENAME = 'converted_data.json'
IMG_DIRECTORY = OUTPUT_DIRECTORY + '/img'
OUTPUT_FORMATS = ['png']

MARKER_SIZE = 3
MARKER = ","

COLOR_LEVELS = 60
CORNER_SMOOTHING = True

lons = [i+1.375 for i in range(TOTAL_LON)]
lats = [i-1.375 for i in range(int(TOTAL_LAT/2), int(-TOTAL_LAT/2), -1)]


def save_file(dir, name):
    """Save the current plot as an .svg in the image directory"""

    dir_path = f"{IMG_DIRECTORY}/{dir}"
    try:
        os.makedirs(dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for output_format in OUTPUT_FORMATS:
        path = f"{dir_path}/{name}.{output_format}"
        print(f"Writing {path}")
        plt.savefig(path, format=output_format, bbox_inches='tight', dpi=500)


def color_map(var):
    if var == 'mean_sea_level_pressure':
        return cm.BuPu
    elif var == 'total_cloud_cover':
        return cm.get_cmap('Blues_r')
    else:
        return cm.jet


def plot_thing(data, variable, day, cmap):
    title = variable

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

    textstr = day_str(day)
    plt.text(0.4, 0.9, textstr, fontsize=12, transform=plt.gcf().transFigure)

    ax.coastlines()

    norm = colors.Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    plt.colorbar(sm, shrink=0.5)

    save_file(variable, day)


def day_str(day):
    """
    Convert an integer day to a date string with format <Month Date>
    e.g. 1 -> "Jan 1"
    """
    padded = f"{int(day)+1:03d}"

    dt = datetime.strptime(padded, "%j")
    return dt.strftime("%B %d")


def init():
    try:
        os.makedirs(OUTPUT_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    try:
        os.makedirs(IMG_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", help="Input JSON file", default=JSON_FILENAME)

    args = parser.parse_args()

    INPUT_FILENAME = args.input

    init()

    # Open our converted data and read it in
    with open(INPUT_FILENAME, 'r') as my_file:
        json_data = my_file.read()
        data = json.loads(json_data)

    day = os.path.basename(INPUT_FILENAME).split('.')[0]

    for variable in data.keys():
        plot_thing(
            np.array(data[variable], dtype=np.float64),
            variable,
            day,
            color_map(variable)
        )
