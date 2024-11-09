import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

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
    'ASSESSED_VALUE': [10000, 25000, 60000]
}
csv_df = pd.DataFrame(csv_data)

# Update GeoDataFrame with CSV data
def update_dataframe_with_csv(gdf, csv_df):
    csv_df = csv_df.set_index('APN')
    gdf = gdf[gdf['APN'].isin(csv_df.index)]  # Keep only rows with matching CSV entries
    gdf['TAX_BILL'] = gdf['APN'].map(csv_df['TAX_BILL'])
    gdf['ASSESSED_VALUE'] = gdf['APN'].map(csv_df['ASSESSED_VALUE'])
    gdf['RATIO'] = gdf['TAX_BILL'] / gdf['ASSESSED_VALUE']
    return gdf

gdf = update_dataframe_with_csv(gdf, csv_df)

def save_geojson_to_file(gdf, file_path):
    geojson = gdf.to_json()
    with open(file_path, 'w') as file:
        file.write(geojson)
    print(f"GeoJSON data saved to {file_path}")

if __name__ == "__main__":
    save_geojson_to_file(gdf, 'build/data.json')