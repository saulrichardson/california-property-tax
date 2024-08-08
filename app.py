import os
from flask import Flask, render_template, jsonify
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from flask_frozen import Freezer

if not os.path.exists('static'):
    os.makedirs('static')

app = Flask(__name__)
freezer = Freezer(app)
base_url = os.getenv('BASE_URL', '')

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

@app.route('/data')
def get_data():
    geojson = gdf.to_json()
    return geojson, 200, {'Content-Type': 'application/json'}

@app.route('/')
def index():
    return render_template('index.html', base_url=base_url)

@freezer.register_generator
def index():
    return '/'

if __name__ == '__main__':
    app.run(debug=True)