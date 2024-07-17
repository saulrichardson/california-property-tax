"""
Creates location data for user provided APNs
"""
import geopandas as gpd
import pandas as pd

def show_x_rows(gdb_file, rows):
    gdf = gpd.read_file(gdb_file, rows=rows)
    print(gdf.head())


def process_large_gdb(gdb_file, chunk_size=10000):
    offset = 0
    processed_chunks = []

    while True:
        gdf = gpd.read_file(gdb_file, rows=chunk_size, skiprows=offset)
        if gdf.empty:
            break

        # Filter out rows without AINs or APNs
        gdf_filtered = gdf.dropna(subset=['AIN', 'APN'])
        processed_chunks.append(gdf_filtered)

        offset += chunk_size

    # Combine all processed chunks
    combined_gdf = gpd.GeoDataFrame(pd.concat(processed_chunks, ignore_index=True))
    combined_gdf.to_file('data/processed/filtered_data.geojson', driver='GeoJSON')

    return combined_gdf

if __name__ == '__main__':
    gdb_file = "resources/LACounty_Parcels.gdb"

    show_x_rows(gdb_file, 1000)
    #combined_data = process_large_gdb(gdb_file)
