# 4710 Project

Ryan Froese ([froeser5@myumanitoba.ca](mailto:froeser5@myumanitoba.ca))

James Klassen ([klass167@myumanitoba.ca](mailto:klass167@myumanitoba.ca))

Tyler Loewen ([loewent4@myumanitoba.ca](mailto:loewent4@myumanitoba.ca))

## Contents

- [Deliverables](#Deliverables)
- [Project Outline](#Project-Outline)
- [Schedule](#Schedule)
- [Resources](#Resources)
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

- [ ] Initial meeting
- [ ] Decide rough project idea

### Week 1 (Nov 13)

- [ ] What data do we want to pull?
- [ ] Determine how to get data from AWS into a usable format
- [ ] Selected a visualization tool 
- [ ] Git repo with contributions (James)

### Week 2 (Nov 20)

### Week 3 (Nov 27)

### Week 4 (Dec 4)

- [ ] Draft should be done
- [ ] Editing/polish phase starts
- [ ] Determine how to typeset the report

### Week 5 (Dec 11)

- [ ] Done

## Resources

- [AWS Information page](https://registry.opendata.aws/noaa-wod/)
- [AWS Dataset](https://noaa-wod-pds.s3.amazonaws.com/index.html)
- [NOAA Website](https://www.nodc.noaa.gov/OC5/WOD/pr_wod.html)
- [High resolution water surface temperature](https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1)
- [World Ocean Database: code tables](https://www.nodc.noaa.gov/OC5/WOD/wod_codes.html)
  - [Acronyms](https://www.ncei.noaa.gov/access/world-ocean-database-select/bin/builder.pl)

### Maps in python:

- https://www.youtube.com/watch?v=6GGcEoodLNM
- https://www.youtube.com/watch?v=hA39KSTb3dY

Data Available we want to use?

- Water Temperature
- Salinity

Fixed time interval dataset using clustering methods and represented using Data Visualization:

- Cluster water temperature and salinity data into distinct clusters and visually represent them on a map (using coloured regions)
  - Clusters could be represented as a geographical region
  - User specify how many different clusters of temperature they want represented then data clustered appropriately
  - Change saturation of colour based on salinity value

## Algorithm

Clustering algorithm idea:

- Determine min/max range
- Input # of desired clusters, evenly split the clusters among that range in the form of temperature ranges
- Adjust the groups one by one until they’re all roughly even, same # of points or same geographical area
- Plot them w/ different colours on a map projection
