import requests
import csv
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

def fetch_ains(filename='ains.csv'):
    ains_df = pd.read_csv(filename, dtype=str)
    return ains_df['AIN'].tolist()

def fetch_property_data(ain, max_retries=10):
    url = f'https://portal.assessor.lacounty.gov/api/parceldetail?ain={ain}'
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                parcel_data = response.json().get("Parcel", {})
                return flatten_parcel_data(parcel_data) if parcel_data else None
            else:
                print(f"No parcel data found for AIN {ain}.")
                return None
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Max retries reached for AIN {ain}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    return None

def flatten_parcel_data(parcel_data):
    flattened_data = {}
    for key, value in parcel_data.items():
        if not isinstance(value, list):  # Skip list fields
            flattened_data[key] = value
    return flattened_data

def save_to_csv(data, filename='assessor_data.csv'):
    if not data:
        print("No data to save.")
        return
    fields = data[0].keys()
    with open(filename, 'a', newline='') as csvfile:  # Open in append mode
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        if csvfile.tell() == 0:  # Write header only if file is empty
            writer.writeheader()
        writer.writerows(data)

def process_batch(batch, batch_num, total_batches):
    batch_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(fetch_property_data, ain): ain for ain in batch}
        for future in as_completed(futures):
            data = future.result()
            if data:
                batch_data.append(data)
    print(f"Batch {batch_num}/{total_batches} completed.")
    return batch_data

if __name__ == '__main__':
    ains = fetch_ains('ains.csv')
    total_ains = len(ains)
    batch_size = 100  # Define batch size
    total_batches = math.ceil(total_ains / batch_size)

    property_data = []
    for batch_num in range(total_batches):
        start = batch_num * batch_size
        end = min(start + batch_size, total_ains)
        batch = ains[start:end]
        batch_data = process_batch(batch, batch_num + 1, total_batches)

        # Save batch data after each batch
        save_to_csv(batch_data, 'assessor_data.csv')
        property_data.extend(batch_data)

    print("All batches processed and data saved.")
