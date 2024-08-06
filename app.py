from flask import Flask, render_template
import folium
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from flask_frozen import Freezer

app = Flask(__name__)
freezer = Freezer(app)

# Sample GeoDataFrame data
data = {
    'APN': ['123', '456', '789'],
    'geometry': [Point(-118.25, 34.05), Point(-118.30, 34.10), Point(-118.35, 34.15)]
}
gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")

# Sample CSV DataFrame data
csv_data = {
    'APN': ['123', '456', '789'],
    'TAX_BILL': [1000, 2000, 3000],
    'MARKET_VALUE': [10000, 25000, 60000]
}
csv_df = pd.DataFrame(csv_data)

# Update GeoDataFrame with CSV data
def update_dataframe_with_csv(gdf, csv_df):
    csv_df = csv_df.set_index('APN')
    gdf['TAX_BILL'] = gdf['APN'].map(csv_df['TAX_BILL'])
    gdf['MARKET_VALUE'] = gdf['APN'].map(csv_df['MARKET_VALUE'])
    gdf['RATIO'] = gdf['TAX_BILL'] / gdf['MARKET_VALUE']
    return gdf

gdf = update_dataframe_with_csv(gdf, csv_df)

# Function to determine color based on ratio
def color_based_on_ratio(ratio):
    if ratio < 0.1:
        return 'green'
    elif ratio < 0.3:
        return 'yellow'
    elif ratio < 0.5:
        return 'orange'
    else:
        return 'red'

@app.route('/')
def index():
    # Create a map centered around the average location
    m = folium.Map(location=[gdf.geometry.y.mean(), gdf.geometry.x.mean()], zoom_start=10)

    # Add circles to the map
    for _, row in gdf.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color=color_based_on_ratio(row['RATIO']),
            fill=True,
            fill_color=color_based_on_ratio(row['RATIO']),
            popup=f"APN: {row['APN']}<br>TAX BILL: {row['TAX_BILL']}<br>MARKET VALUE: {row['MARKET_VALUE']}"
        ).add_to(m)

    # Save the map as an HTML file
    map_path = 'static/map.html'
    m.save(map_path)
    return render_template('index.html', map_file='map.html')

@freezer.register_generator
def index():
    return '/'

if __name__ == '__main__':
    app.run(debug=True)