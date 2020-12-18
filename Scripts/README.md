# Scripts

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

- `-i` input file/directiory
- `-o` output directory

### Generating maps from `.json` data

```shell
python generate_map.py [-i] [-o]
```

Parameters

- `-i` input file/directiory
- `-o` output directory

### Converting map image sequences to gif file

```shell
./convert_image_sequences [-i]
```

By default, this looks for images in `/output/<variable_name>` and writes a .mp4 file `variable_name.mp4`

## File overview

- `cluster.py`
  - Clusters data using a naïve approach
- `consts.py`
  - Contains global constants used across data processing
- `convert.py`
  - Convert the dataset from the raw `.nc` form, to a trimmed `.json` file with only the values we need.
- `fcluster.py`
  - Clusters data using a faster improved approach
- `generate_map.py`
  - Generates map figures from .json data
