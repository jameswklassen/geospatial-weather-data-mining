# Scripts

## File overview

### Shell Scripts

- `cluster_and_generate`
  - helper script to to generate visualizations
    - runs fcluster on all data
    - generates figures based on clustered data
    - converts image directories to .mp4 files
- `convert_image_sequences`
  - Compiles a sequence of images in into a single video file
- `loop_videos`
  - Finds all .mp4 files and loops each one over a longer period of time

### Python source files

- `cluster.py`
  - Clusters data using a naïve approach
- `consts.py`
  - Contains global constants used across data processing
- `convert.py`
  - Convert the dataset from the raw `.nc` form, to a trimmed `.json` file with only the values we need.
- `fcluster.py`
  - Clusters data using a faster improved approach
- `generate_line_graph.py`
  - Generates line graph figures from .json data
- `generate_map.py`
  - Generates map figures from .json data
- `generate_performance_analysis_graphs.py`
  - Generates performance analysis figures from performance `.csv` data in `Data/performance`
- `test_fcluster_performance.py`
  - Test the performance of our improved clustering algorithm with a variety of synthesized data
- `utils.py`
  - Contains global functions used across data processing

## Common tasks

### Converting raw `.nc` data to `.json`

```shell
python convert.py [-i] 
```

Override the input file with `-i` flag

```shell
python convert.py -i ../Data/my_data.nc
```

Notes:

- Default input file: `/Data/EAR5-01-01-2020.nc`
- Default output location `/Scripts/output/converted`

### Clustering data

#### Improved (fast) clustering

```shell
python fcluster.py [-i] [-o]
```

#### Naive clustering

```shell
python cluster.py [-i] [-o]
```

Parameters (both `cluster.py` and `fcluster.py`)

- `-i` input file/directory
- `-o` output directory

### Generating maps from `.json` data

```shell
python generate_map.py [-i] [-o]
```

Parameters

- `-i` input file/directory
- `-o` output directory

### Converting map image sequences to mp4 file

```shell
./convert_image_sequences [-i]
```

By default, this looks for images in `/output/<variable_name>` and writes a .mp4 file `variable_name.mp4`
