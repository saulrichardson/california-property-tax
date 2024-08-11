# LA Property Tax Map

## Overview

The LA Property Tax Map is a Flask application that visualizes property tax data for Los Angeles on an interactive map. Each property is displayed as a circle, color-coded based on the ratio of its tax bill to its market value. This application provides an intuitive way to explore and analyze property tax rates across different locations in Los Angeles.

### Requirements

- Python 3.6+
- GeoPandas
- Pandas
- Shapely

### Deployment
As of August 7, 2024, pushing to `main` results in create-map.py being run-- necessary files are put in the build directory, which is then pushed to the `gh-pages` branch. This results in Github Page's automatic deployment and the site can then be found [here](https://saulrichardson.github.io/california-property-tax). To deploy a version of this app with the [LA Paracels GDB](https://apps.gis.lacounty.gov/hubfiles/LACounty_Parcels.zip), push the codebase with the production-ready change to prod.
