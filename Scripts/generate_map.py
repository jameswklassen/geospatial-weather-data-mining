from os import listdir, makedirs
from os.path import isfile, isdir, join, basename
import errno
import json
import argparse
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from matplotlib import colors, cm
import cartopy.crs as ccrs

from consts import TOTAL_LAT, TOTAL_LON, OUTPUT_DIRECTORY, IGNORED_VARIABLES, DEFAULT_K
from utils import get_units, get_english_variable_name, day_str

DEBUG = False

INPUT_DIRECTORY = OUTPUT_DIRECTORY + '/converted'
IMG_DIRECTORY = OUTPUT_DIRECTORY + '/img'

OUTPUT_FORMATS = ['png']
COLOR_LEVELS = 60
CORNER_SMOOTHING = True

lons = [i+1.375 for i in range(TOTAL_LON)]
lats = [i-1.375 for i in range(int(TOTAL_LAT/2), int(-TOTAL_LAT/2), -1)]


def save_file(dir, name):
    """Save the current plot as an .svg in the image directory"""

    dir_path = f"{IMG_DIRECTORY}/{dir}"
    try:
        makedirs(dir_path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    for output_format in OUTPUT_FORMATS:
        path = f"{dir_path}/{name}.{output_format}"

        if DEBUG:
            print(f"Writing {path}")

        plt.savefig(path, format=output_format, bbox_inches='tight', dpi=500)


def color_map(var):
    if var == 'mean_sea_level_pressure':
        return cm.BuPu
    elif var == 'total_cloud_cover':
        return cm.get_cmap('Blues_r')
    else:
        return cm.jet


def plot(data, variable, day, cmap, output_dir=None, ranges=None, k=None):
    """Plot a single variable on a single day"""

    title = get_english_variable_name(variable)
    min, max = ranges

    ax = plt.axes(projection=ccrs.PlateCarree(), label=f"{title}-{day}")
    ax.set_title(title, fontsize=16)
    c = plt.contourf(
        lons,
        lats,
        data,
        COLOR_LEVELS,
        transform=ccrs.PlateCarree(),
        vmin=min,
        vmax=max,
        cmap=cmap,
        corner_mask=CORNER_SMOOTHING,
    )

    # Generate a discrete legend with specific values
    # proxy = [plt.Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in c.collections]
    # ax.legend(proxy, c.levels)

    if k:
        textstr = f"k={k}"
        ax.text(1, -0.05, textstr, transform=ax.transAxes, fontsize=9, horizontalalignment='right', verticalalignment='top')

    textstr = day_str(day)
    ax.text(0, -0.05, textstr, transform=ax.transAxes, fontsize=9, verticalalignment='top')

    ax.coastlines()

    if ranges:
        norm = colors.Normalize(vmin=min, vmax=max)
    else:
        norm = colors.Normalize(vmin=np.nanmin(data), vmax=np.nanmax(data))

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    cb = plt.colorbar(sm, shrink=0.5, orientation='vertical', pad=0.025)
    ticks = cb.get_ticks()
    cb.set_ticks(ticks)
    cb.set_ticklabels([f"{val} {get_units(variable)}" for val in ticks])

    file_dir = f"{output_dir}/{variable}" if output_dir else variable
    save_file(file_dir, day)


def generate_plots(filename, output_dir=None, ranges=None, k=None):
    """Generate plots for all variables given a .json file"""

    if DEBUG:
        print('Generating plot for', filename)

    with open(filename, 'r') as my_file:
        json_data = my_file.read()
        data = json.loads(json_data)

    day = basename(filename).split('.')[0]

    for variable in data.keys():
        if variable in IGNORED_VARIABLES:
            continue

        plot(
            np.array(data[variable], dtype=np.float64),
            variable,
            day,
            color_map(variable),
            output_dir=output_dir,
            ranges=ranges[variable],
            k=k,
        )


def init():
    try:
        makedirs(OUTPUT_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    try:
        makedirs(IMG_DIRECTORY)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input JSON file")
    parser.add_argument("-o", "--output", help="Output subdirectory", default=None)
    parser.add_argument('-k', '--k', help='k value', default=DEFAULT_K)
    args = parser.parse_args()

    init()

    # If input is a single file, easy case
    if args.input and isfile(args.input):
        generate_plots(args.input, args.output, k=args.k)
        exit()

    # Since input isn't a single file, it's either
    #   a) a directory, or
    #   b) not specified
    input_dir = args.input if args.input and isdir(args.input) else INPUT_DIRECTORY

    print("Generating plots for all .json files in", input_dir)

    # Collect all the .json files in input_dir
    files = [f"{input_dir}/{f}" for f in listdir(input_dir) if isfile(join(input_dir, f)) if f.endswith('json') if not f.startswith('range')]

    with open(f"{input_dir}/range.json", 'r') as my_file:
        json_data = my_file.read()
        ranges = json.loads(json_data)

    pool = mp.Pool(mp.cpu_count())
    pool.starmap(generate_plots, [(file, args.output, ranges, args.k) for file in files])
