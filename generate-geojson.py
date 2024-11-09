import csv
import json
from datetime import datetime

# Define the paths to your data files
TAX_DATA_PATH = "resources/extracted_tax_data/tax_data_{YEAR}.csv"
ASSESSOR_DATA_PATH = "resources/assessor_data.csv"
OUTPUT_PATH = "build/property_data.geojson"

# Helper function to calculate effective tax rate
def calculate_effective_tax_rate(total_taxes, assessed_value):
    try:
        return (total_taxes / assessed_value) * 100 if assessed_value else 0
    except (TypeError, ZeroDivisionError):
        return 0

# Load assessor data into a dictionary for fast lookup by AIN
def load_assessor_data():
    assessor_data = {}
    with open(ASSESSOR_DATA_PATH, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assessor_data[row['AIN']] = row
    return assessor_data

# Load tax data and merge with assessor data, writing to GeoJSON format
def create_geojson(year):
    # Open the GeoJSON file for writing
    with open(OUTPUT_PATH, 'w') as geojson_file:
        features = []
        assessor_data = load_assessor_data()

        # Read tax data for the specified year
        with open(TAX_DATA_PATH.format(YEAR=year), 'r') as taxfile:
            tax_reader = csv.DictReader(taxfile)
            for tax_row in tax_reader:
                ain = tax_row['AIN']
                assessor_info = assessor_data.get(ain, {})

                # Build GeoJSON properties dictionary with as much detail as possible
                properties = {
                    "AIN": assessor_info.get("AIN", "N/A"),
                    "Address": f"{assessor_info.get('SitusStreet', 'N/A')}, {assessor_info.get('SitusCity', 'N/A')} {assessor_info.get('SitusZipCode', 'N/A')}",
                    "Assessed Value": f"${float(assessor_info.get('CurrentRoll_LandValue', 1)) + float(assessor_info.get('CurrentRoll_ImpValue', 1))}",
                    "Property Tax Bill": f"${tax_row.get('total_taxes', 'N/A')} in {year}",
                    "Effective Tax Rate": f"{calculate_effective_tax_rate(float(tax_row.get('total_taxes', 0)), float(assessor_info.get('CurrentRoll_LandValue', 1)) + float(assessor_info.get('CurrentRoll_ImpValue', 1)))}",
                    "Tax Class": assessor_info.get("UseType", "N/A"),
                    "Tax Rate Comparison": "Data Unavailable",  # Calculate and populate as needed
                }

                # Build the GeoJSON feature for each property
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            float(assessor_info.get('Longitude', 0)),
                            float(assessor_info.get('Latitude', 0))
                        ]
                    },
                    "properties": properties
                }
                features.append(feature)

        # Write GeoJSON structure
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        json.dump(geojson, geojson_file, indent=2)
        print(f"Saved GeoJSON at {OUTPUT_PATH}")

if __name__ == '__main__':
    # Run the function to create a GeoJSON file for a given year
    create_geojson(year=datetime.now().year - 1)  # Adjust year as needed
