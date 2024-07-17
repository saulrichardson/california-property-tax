# Property Taxes in California
```
California's Prop 13 keeps the assessed value of any real property back at year it was last sold. They are not reassessed each year according to a property's
current market value. This can be a good thing for families who own and have lived in their house for a long time, but it also opens legal loopholes for others
to artificially keep their property taxes low even though it has changed hands. Golf clubs in Los Angeles use complex ownership structures to ensure that when
members buy stakes in the club, no more than a 50% interest changes hands. Commercial real estate can be sold without changing who is on the title by selling the
LLC that owns property instead of the property itself. Strategies like these can prevent properties from being reassessed and keep a property's tax bill incredibly low
relative to its actual market value.

This project aims to understand how disconnected property tax revenues and market values really are, especially in high-value areas where wealthy
individuals/corporations can take advantage of Prop 13. Our project will have the additional benefit of unifying local county property tax data into a single
map—something that doesn't exist at the state level. 
```

# Los Angeles Real Estate Parcel Mapping Project

## Project Overview
This project maps real estate parcels in Los Angeles, associates them with tax bills and property values, and visualizes the data. It involves processing a geodatabase (GDB), web scraping tax information, and creating interactive maps.

## Files and Scripts
- `location-to-ain.py`: Extracts location and AIN from the GDB file.
- `apn-to-tax.py`: Fetches tax information for each AIN.
- `create-map.py`: Creates visual maps of parcels with tax and property value information.
- `data-analysis.py`: Analyzes the collected data and generates insights.

## Setup
1. Clone the repository.
2. Install Pipenv: `pip install pipenv`.
3. Install dependencies: `pipenv install` (or `poetry install` if using Poetry).
4. Activate the environment: `pipenv shell` (or `poetry shell` if using Poetry).
5. Run the scripts in the following order:
    - `python apn-to-location.py`
    - `python apn-to-tax.py`
    - `python create-map.py`
    - `python data-analysis.py`

## Dependencies
- beautifulsoup4
- requests
- geopandas
- folium
- matplotlib
- pandas

## Usage
1. Extract APN to location data using `apn-to-location.py`.
2. Fetch tax information using `apn-to-tax.py`.
3. Create visual maps using `create-map.py`.
4. Perform data analysis using `data-analysis.py`.
