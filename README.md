# LA Property Tax Map

### Overview
The two main Python scripts are designed to retrieve property tax data and details for each AIN (property) and organize it for data analysis and visualization.

*First Script*: Sends POST requests to retrieve property tax bill PDF links, then downloads each PDF, extracts values like fiscal year, taxable values, and total tax due using regular expressions, and stores the data in separate CSVs by fiscal year.

*Second Script*: Sends GET requests to a different API to retrieve parcel details based on AINs and saves these details to a single CSV file.

### Deployment
As of August 7, 2024, pushing to `main` results in create-map.py being run-- necessary files are put in the build directory, which is then pushed to the `gh-pages` branch. This results in Github Page's automatic deployment and the site can then be found [here](https://saulrichardson.github.io/california-property-tax). To deploy a version of this app with the [LA Paracels GDB](https://apps.gis.lacounty.gov/hubfiles/LACounty_Parcels.zip), push the codebase with the production-ready change to prod.
