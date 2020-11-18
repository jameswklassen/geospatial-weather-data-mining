# 4710 Project

Ryan Froese ([froeser5@myumanitoba.ca](mailto:froeser5@myumanitoba.ca))

James Klassen ([klass167@myumanitoba.ca](mailto:klass167@myumanitoba.ca))

Tyler Loewen ([loewent4@myumanitoba.ca](mailto:loewent4@myumanitoba.ca))

## Contents

- [Deliverables](#Deliverables)
- [Project Outline](#Project-Outline)
- [Schedule](#Schedule)
- [Resources](#Resources)
- [Datasets](#Datasets)
- [Process](#Process)
- [Algorithm](#Algorithm)

## Deliverables

- A project report (e.g., about 10 pages when using the IEEE template)
- For proof-of-concept implementation, in addition to the above report, also submit
  - source code
  - README
  - CSV producing the tables and/or plotted figures/graphs in the Experimental Evaluation section (so that we could modify/redraw the figures)

## Project Outline

1. Introduction (includes motivation, potential real-life applications). At the end of the Introduction (say, Section 1.1), pls explicitly list your contributions of this work (e.g., a new design, an efficient algorithm, additional features, new insights)
2. Background & related work (e.g., point out shortcomings of the existing work, compare & contrast with the existing work)
3. main body (includes description of your new idea, step-by-step illustrative examples, pseudo codes, highlight of any differences between your work vs. existing works)
4. analytical (e.g., theorems) and empirical evaluation (e.g., experiments, tables & figures, explanations on experimental results)
5. conclusions, limitations, and future work
6. references (e.g., cite at least 10 refereed books, journals, and/or conference papers; websites do NOT counted)

## Schedule

### Week 0 (Nov 6)

- [x] Initial meeting
- [x] Decide rough project idea

### Week 1 (Nov 13)

- [x] What data do we want to pull?
- [x] Determine how to get data from AWS into a usable format
- [ ] Selected a visualization tool
- [x] Git repo with contributions (James)
- [ ] Basic data filtering and agglomerating

### Week 2 (Nov 20)

### Week 3 (Nov 27)

### Week 4 (Dec 4)

- [ ] Draft should be done
- [ ] Editing/polish phase starts
- [ ] Determine how to typeset the report

### Week 5 (Dec 11)

- [ ] Done

## Resources

- [ERA5 Dataset](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview)
- [ERA5 Documentation](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation)
- [ERA5 AWS](https://registry.opendata.aws/ecmwf-era5/)

### Examples

- [netCDF4 Python docs](https://unidata.github.io/netcdf4-python/netCDF4/)
- [Working with netCDF4: Example](https://www.earthinversion.com/utilities/reading-NetCDF4-data-in-python/)

### Maps in python

- https://www.youtube.com/watch?v=6GGcEoodLNM
- https://www.youtube.com/watch?v=hA39KSTb3dY

## Dataset

We are using [ERA5](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=overview://www.nodc.noaa.gov/OC5/WOD/pr_wod.html) dataset with the following variables:

- [Land-sea mask](https://apps.ecmwf.int/codes/grib/param-db?id=172)
- [Sea Surface Temperature](https://apps.ecmwf.int/codes/grib/param-db?id=34)
- [Mean sea level pressure](https://apps.ecmwf.int/codes/grib/param-db?id=151)
- [Total cloud cover](https://apps.ecmwf.int/codes/grib/param-db?id=164)
- [10 metre U wind component](https://apps.ecmwf.int/codes/grib/param-db?id=165)
- [10 metre V wind component](https://apps.ecmwf.int/codes/grib/param-db?id=166)
- [2 metre temperature](https://apps.ecmwf.int/codes/grib/param-db?id=167)
- [Mean wave direction](https://apps.ecmwf.int/codes/grib/param-db?id=140230)

All data is from January 1st 2020.

### Coordinate System

- Data is interpolated to a regular lat/lon grid with 0.25 degree increments
- All gridded data is made available in Decimal Degrees, lat/lon, with latitude values in the range [-90;+90] referenced to the equator and longitude values in the range [0;360] referenced to the Greenwich Prime Meridian.

## Process

Fixed time interval dataset using clustering methods and represented using Data Visualization:

- Cluster variables distinct clusters and visually represent them on a map (using coloured regions, arrows, numbers, etc)
  - Clusters could be represented as a geographical region
  - User specify how many different clusters of variables they want represented then data clustered appropriately
  - Change saturation of colour based on salinity/oxygen value, etc

## Algorithm

Clustering algorithm idea:

- Determine min/max range
- Input number of desired clusters, evenly split the clusters among that range in the form of temperature ranges
- Adjust the groups one by one until they’re all roughly even, same # of points or same geographical area
- Plot them with different colours on a map projection
