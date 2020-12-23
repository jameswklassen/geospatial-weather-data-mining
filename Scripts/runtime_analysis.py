import pandas as pd
import matplotlib.pyplot as plt

FILENAMES = ['operations.csv', 'operations_ratio.csv']
IMG_DIRECTORY = 'output'
OUTPUT_FORMATS = ['png']


def save_file(name):
    """Save the current plot as an .svg in the image directory"""

    for output_format in OUTPUT_FORMATS:
        path = f"{IMG_DIRECTORY}/{name}.{output_format}"

        print(f"Writing {path}")

        plt.savefig(path, format=output_format, bbox_inches='tight', dpi=500)


def operations():
    title = 'Number of operations'
    input_file = 'operations.csv'
    output_file = 'operations'

    data = pd.read_csv(input_file, sep=',', header=0)

    plt.suptitle(title, fontsize=16)

    ax = plt.axes(label=title)
    ax.set_xlabel('Dataset size')
    ax.set_ylabel('Number of operations')
    ax.ticklabel_format(useMathText=True, useOffset=False)

    dataset_size = data.get(data.columns[0])

    for col in data.columns:
        if col == data.columns[0]:
            ax.plot(dataset_size, data.get(col), label=col, color='grey', alpha=0.5, linestyle='--')
        else:
            ax.plot(dataset_size, data.get(col), label=col)

    ax.legend()

    save_file(output_file)


def operations_ratio():
    title = 'Ratio of operations over dataset size'
    input_file = 'operations_ratio.csv'
    output_file = 'operations_ratio'

    data = pd.read_csv(input_file, sep=',', header=0)

    plt.suptitle(title, fontsize=16)

    ax = plt.axes(label=title)
    ax.set_xlabel('Dataset size')
    ax.set_ylabel('Number of operations / dataset size')
    ax.ticklabel_format(useMathText=True)

    dataset_size = data.get(data.columns[0])

    for col in data.columns:
        if col != data.columns[0]:
            ax.plot(dataset_size, data.get(col), label=col)

    ax.legend()

    save_file(output_file)


if __name__ == '__main__':
    operations()
    operations_ratio()
