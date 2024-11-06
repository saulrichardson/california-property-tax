# LA Property Tax Map

### Overview
The three main Python scripts are designed to retrieve property tax data and details for each AIN (property) and organize it for data analysis and visualization.

`grab-ains-from-gdb.py`: Given a GDB that points to every valid AIN in Los Angeles county, creates a CSV file of only the AINs.

`grab-parse-tax-bills.py`: Sends POST requests to retrieve property tax bill PDF links from [LA's property tax bill API](https://ttc.lacounty.gov/secured-property-tax-results), which returns a block of HTML that includes some number of tax bills from over the years. The script then downloads each PDF, extracts values like fiscal year, taxable values, and total tax due using regular expressions, and stores the data in separate CSVs by fiscal year.

`generate-accessor-data-csv.py`: Sends GET requests to the [LA Assessor API](https://portal.assessor.lacounty.gov/) to retrieve parcel details based on AINs and saves these details to a single CSV file.

### Deployment
As of August 7, 2024, pushing to `main` results in create-map.py being run-- necessary files are put in the build directory, which is then pushed to the `gh-pages` branch. This results in GitHub Page's automatic deployment and the site can then be found [here](https://saulrichardson.github.io/california-property-tax). To deploy a new version of this app, push the codebase with the production-ready change to the main branch.

### Thoughts

Due to GitHub's file size limitations, the GDB file used to gain access to every AIN in Los Angeles county is not uploaded to this repository. It can be found [here](https://hub.arcgis.com/datasets/lacounty::la-county-parcel-map-service/about3), downloaded, and then preferably dropped in the repository's `resources` directory. This directory listed in the repository's `.gitignore` file, stopping all of its content from being uploaded to GitHub. The same goes for `tax_data.csv`, which approached 1.62GB.

The process of converting all of this data to an accessible GeoJSON is still a work in progress and this `README.md` will be updated accordingly.

In the case you choose to use these scripts to scrape this same data yourself, you can modify the `__main__` method yourself in order to point it at different repositories and automate different processes.
