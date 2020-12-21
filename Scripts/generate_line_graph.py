from os import listdir, makedirs
from os.path import isfile, isdir, join, basename
import errno
import json
import argparse
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt

from consts import TOTAL_LAT, TOTAL_LON, OUTPUT_DIRECTORY, IGNORED_VARIABLES, DEG, DEFAULT_K
from utils import get_units, get_english_variable_name, day_str

DEBUG = False

LON = 185

INPUT_DIRECTORY = OUTPUT_DIRECTORY + '/converted'
IMG_DIRECTORY = OUTPUT_DIRECTORY + '/img'

OUTPUT_FORMATS = ['png']
COLOR_LEVELS = 60
CORNER_SMOOTHING = False

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


def plot(data, variable, day, output_dir=None, ranges=None, k=None):
    """Plot a single variable on a single day"""

    title = get_english_variable_name(variable)

    plt.suptitle(title, fontsize=16)
    ax = plt.axes(label=f"{title}-{day}")
    ax.plot(lats, data[:, LON], color='black')

    ax.set_xlabel('Latitude')

    ax.set_ylim(ranges)
    ax.set_ylabel(f"{get_english_variable_name(variable)} ({get_units(variable)})")

    plt.xticks([90, 45, 0, -45, -90], [f'90{DEG} N', f'45{DEG} N', f'0{DEG}', f'45{DEG} S', f'90{DEG} S'])

    if k:
        textstr = f"k={k}"
        ax.text(1, 1.05, textstr, transform=ax.transAxes, fontsize=9, horizontalalignment='right', verticalalignment='top')

    textstr = day_str(day)
    ax.text(0, 1.05, textstr, transform=ax.transAxes, fontsize=9, verticalalignment='top')

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
            output_dir=output_dir,
            ranges=ranges[variable],
            k=k
        )


def find_lon_with_least_land(data):
    """
    Given a 2d array of data
    return the index of the longitude with the least amount of land
    """
    nonzeros = np.empty(360)
    for lon in range(360):
        arr = np.array(data)
        nonzeros[lon] = np.count_nonzero(arr[:, lon])

    max_idx = np.where(nonzeros == np.amax(nonzeros))

    return max_idx[0]


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
