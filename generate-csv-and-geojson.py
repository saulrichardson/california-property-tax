import csv
import os
import signal
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import geojson
import pandas as pd
import requests

property_data = []

def signal_handler(sig, frame):
    print("Received signal to terminate. Saving data before exiting...")
    save_to_csv(property_data, 'tax_data.csv')  # Save to CSV
    save_to_geojson(property_data, 'tax_data.geojson')  # Save to GeoJSON
    exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def fetch_ains(filename='ains.csv'):
    ains_df = pd.read_csv(filename, dtype=str)
    return ains_df['AIN'].tolist()

def flatten_parcel_data(parcel_data):
    """ Flattens the Parcel data by ignoring list fields (e.g., 'SubParts'). """
    flat_data = {}
    for key, value in parcel_data.items():
        # Skip list fields (like 'SubParts') and nested lists
        if not isinstance(value, list):
            flat_data[key] = value
    return flat_data

def fetch_property_data(ain, max_retries=5):
    url = f'https://portal.assessor.lacounty.gov/api/parceldetail?ain={ain}'
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                parcel_data = response.json().get("Parcel", {})
                if parcel_data:
                    # Flatten the parcel data and ignore list fields like 'SubParts'
                    data = flatten_parcel_data(parcel_data)
                    data['AIN'] = ain  # Ensure AIN is present
                    return data
                else:
                    print(f"No parcel data found for AIN {ain}.")
                    return None
            else:
                print(f"Failed to fetch data for AIN {ain}, status code: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print(f"Request for AIN {ain} timed out. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching AIN {ain}: {e}")

        wait_time = 2 ** attempt
        print(f"Retrying in {wait_time} seconds...")
        time.sleep(wait_time)

    print(f"Max retries reached for AIN {ain}.")
    return None

def save_to_csv(data, filename='tax_data.csv'):
    if not data:
        print("No data to save.")
        return

    temp_filename = f"{filename}.tmp"  # Temporary file
    fields = data[0].keys()
    with open(temp_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    os.rename(temp_filename, filename)
    print(f"Data saved to {filename}")

def save_to_geojson(data, filename='tax_data.geojson'):
    features = []
    for record in data:
        try:
            point = geojson.Point((float(record['Longitude']), float(record['Latitude'])))
            feature = geojson.Feature(geometry=point, properties={
                k: v for k, v in record.items() if k not in ['Longitude', 'Latitude']
            })
            features.append(feature)
        except ValueError:
            print(f"Skipping AIN {record['AIN']} due to missing or invalid coordinates.")

    feature_collection = geojson.FeatureCollection(features)
    with open(filename, 'w') as f:
        geojson.dump(feature_collection, f)
    print(f"GeoJSON data saved to {filename}")

if __name__ == '__main__':
    ains = fetch_ains('ains.csv')
    total_ains = len(ains)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_property_data, ain): ain for ain in ains}
        for index, future in enumerate(as_completed(futures)):
            ain = futures[future]
            try:
                data = future.result()
                if data:
                    property_data.append(data)
            except Exception as e:
                print(f"Error fetching data for AIN {ain}: {e}")

            percentage_complete = (index + 1) / total_ains * 100
            if percentage_complete in [2, 5, 10, 25, 50, 75, 80, 90, 100]:
                print(f"Progress: {percentage_complete:.2f}% completed.")

    # Save data to CSV and GeoJSON at the end
    save_to_csv(property_data, 'tax_data.csv')
    save_to_geojson(property_data, 'tax_data.geojson')