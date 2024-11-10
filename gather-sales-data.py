import requests
import csv
import time

# Constants
BASE_URL = "https://egispais.gis.lacounty.gov/pais/rest/services/PAIS/pais_sales_parcels/MapServer/0/query"
CSV_FILENAME = "resources/la_sales_data.csv"
CHUNK_SIZE = 1000  # Number of records per request

def fetch_sales_data(offset=0, chunk_size=CHUNK_SIZE):
    """
    Fetch sales data from the LA County Assessor's GIS service, supporting pagination.

    :param offset: The starting record offset for pagination
    :param chunk_size: The number of records to fetch per request
    :return: JSON data with the sales records
    """
    params = {
        'f': 'json',
        'where': '1=1',  # Query to select all sales
        'returnGeometry': 'true',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',  # Request all fields
        'outSR': '4326',
        'resultOffset': offset,
        'resultRecordCount': chunk_size
    }

    response = requests.get(BASE_URL, params=params)

    # Check for request success
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def write_to_csv(data, filename=CSV_FILENAME, fieldnames=None):
    """
    Write data to CSV periodically to avoid memory overflow.

    :param data: List of records to write to CSV
    :param filename: CSV file name
    :param fieldnames: List of fields to write as headers
    """
    # If the file doesn't exist, write the headers
    file_exists = False
    try:
        with open(filename, 'r', newline='') as f:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # Write headers only once
        writer.writerows(data)

    print(f"Written {len(data)} records to {filename}")

def extract_sales_from_response(response):
    """
    Extract and format sales data from the API response.

    :param response: API JSON response
    :return: List of formatted sales records
    """
    if 'features' not in response:
        return [], []

    sales_data = []
    all_fields = set()  # Track all unique fields across records

    for feature in response['features']:
        # Extract fields from the 'attributes' part of each feature
        sales_record = feature['attributes']
        sales_data.append(sales_record)
        all_fields.update(sales_record.keys())  # Add all keys from the current record to the field set

    return sales_data, list(all_fields)

def fetch_and_save_all_sales():
    """
    Fetch all sales data with pagination and save it periodically to CSV.
    """
    offset = 0
    all_sales_fetched = False
    all_fields = set()  # To hold all unique fields encountered

    while not all_sales_fetched:
        print(f"Fetching records starting from offset {offset}...")

        response = fetch_sales_data(offset=offset)

        if response and 'features' in response:
            sales_data, fields = extract_sales_from_response(response)

            if sales_data:
                all_fields.update(fields)  # Update all_fields with any new fields
                write_to_csv(sales_data, filename=CSV_FILENAME, fieldnames=all_fields)

                # Update the offset for the next request
                offset += CHUNK_SIZE
                time.sleep(1)  # Sleep to avoid overwhelming the server
            else:
                print("No more records found.")
                all_sales_fetched = True
        else:
            print("Error fetching or no data returned.")
            all_sales_fetched = True

if __name__ == "__main__":
    # Start fetching and saving the sales data
    fetch_and_save_all_sales()