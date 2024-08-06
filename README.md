# LA Property Tax Map

## Overview

The LA Property Tax Map is a Flask application that visualizes property tax data for Los Angeles on an interactive map. Each property is displayed as a circle, color-coded based on the ratio of its tax bill to its market value. This application provides an intuitive way to explore and analyze property tax rates across different locations in Los Angeles.

### Requirements

- Python 3.6+
- Flask
- Frozen-Flask
- Folium
- GeoPandas
- Pandas
- Shapely

### Deployment
As of August 6, 2024, pushing to `main` results in build_app.py being run-- the Flask app files generated are saved into a build directory, which is then pushed to the `gh-pages` branch. This results in Github Page's automatic deployment and the site can then be found [here](https://saulrichardson.github.io/california-property-tax). To deploy a version of this app with the [LA Paracels GDB](https://apps.gis.lacounty.gov/hubfiles/LACounty_Parcels.zip), push the codebase with the production-ready change to prod. A runner will download the GDB, and run whatever is in the prod version of build_app.py.

### Usage

1. **Run the Flask application**:
    ```bash
    python app.py
    ```

2. **Access the application**:
   Open your web browser and navigate to `http://127.0.0.1:5000` to view the map.
