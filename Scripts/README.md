# Scripts

## Common tasks

### Converting raw `.nc` data to `.json`

```shell
python convert_dataset.py [-i] 
```

By default this will take the data in `Data/EAR5-01-01-2020.nc` file.

Override the input file with `-i` flag

```shell
python convert_dataset.py -i ../Data/my_data.nc
```

### Generating maps from `.json` data

```shell
./generate_all_maps
```

By default, the script uses `.json` files in `/output/converted/` and creates map figures

### Converting map image sequences to gif file

```
./convert_image_sequences
```

By default, this looks for images in `/output/<variable_name>` and writes a .gif file `variable_name.gif`

## File overview

- `consts.py`
  - Contains global constants used across data processing
- `convert_dataset.py`
  - Convert the dataset from the raw `.nc` form, to a trimmed `.json` file with only the values we need.
