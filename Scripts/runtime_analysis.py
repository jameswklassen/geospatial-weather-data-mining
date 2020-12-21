import csv
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

FILENAME = 'runtime_analysis.csv'
IMG_DIRECTORY = 'output'
OUTPUT_FORMATS = ['png']


def save_file(name):
    """Save the current plot as an .svg in the image directory"""

    for output_format in OUTPUT_FORMATS:
        path = f"{IMG_DIRECTORY}/{name}.{output_format}"

        print(f"Writing {path}")

        plt.savefig(path, format=output_format, bbox_inches='tight', dpi=500)


def plot(data):
    title = 'Number of operations'

    plt.suptitle(title, fontsize=16)

    ax = plt.axes(label=title)

    ax.ticklabel_format()

    x = data.get(data.columns[0])
    ax.set_xlabel('Dataset size')
    ax.set_ylabel('Number of operations')

    relevant_cols = [1, 3, 5, 0]

    for col in [data.columns[i] for i in relevant_cols]:
        ax.plot(x, data.get(col), label=col)

    ax.legend()

    save_file(title)

    # More stuff

    title = 'Ratio of operations / datasize'

    plt.suptitle(title, fontsize=16)

    ax = plt.axes(label=title)
    ax.ticklabel_format()
    # ax.ticklabel_format(style='plain')

    x = data.get(data.columns[0])
    ax.set_xlabel('Dataset size')
    ax.set_ylabel('Number of operations / datasize')

    relevant_cols = [2, 4, 6]

    for col in [data.columns[i] for i in relevant_cols]:
        ax.plot(x, data.get(col), label=col)

    ax.legend()
    save_file('Ratio of operationsdatasize')


def panda():
    # my_data = pd.read_csv(FILENAME, sep=',', header=0, usecols=[0, 1, 2, 3])
    data = pd.read_csv(FILENAME, sep=',', header=0)
    print(data.get(data.columns[1]))
    plot(data)


if __name__ == '__main__':
    panda()
