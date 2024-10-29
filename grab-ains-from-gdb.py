import geopandas as gpd
import pandas as pd

def extract_ains_from_gdb(gdb_path, output_file):
    # Read the GDB file
    gdf = gpd.read_file(gdb_path)

    # Extract the AINs (assuming the AINs are stored in a column named 'AIN')
    if 'AIN' not in gdf.columns:
        print("The GDB file does not contain an 'AIN' column.")
        return

    ains = gdf['AIN'].unique()  # Get unique AINs

    # Save to a tidy CSV file
    ains_df = pd.DataFrame(ains, columns=['AIN'])
    ains_df.to_csv(output_file, index=False)
    print(f"AINs extracted and saved to {output_file}")

if __name__ == '__main__':
    gdb_path = '/resources/LACounty_Parcels.gdb' # Not provided in git repository due to size limitations, but you can download it from https://apps.gis.lacounty.gov/hubfiles/LACounty_Parcels.zip
    output_file = 'ains.csv'  # Specify your output file name
    extract_ains_from_gdb(gdb_path, output_file)
