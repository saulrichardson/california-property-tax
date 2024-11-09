import requests
from bs4 import BeautifulSoup
import time
import pymupdf
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import os


# Define constants
API_URL = "https://ttc.lacounty.gov/secured-property-tax-results"
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
}

def get_pdf_links(ain, max_retries=5):
    """
    Sends a POST request with the specified AIN to retrieve property tax PDF links.
    Implements exponential backoff for retries in case of failures.
    """
    payload = {
        "ain": ain,
        "timestamp": int(time.time())  # Adds a Unix timestamp like in the curl command
    }
    retries = 0

    while retries < max_retries:
        try:
            response = requests.post(API_URL, headers=HEADERS, data=payload)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            return ain, parse_pdf_links(response.text)

        except requests.RequestException as e:
            # Exponential backoff
            wait_time = 2 ** retries
            print(f"Error fetching data for AIN {ain}: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1

    print(f"Failed to fetch data for AIN {ain} after {max_retries} retries.")
    return ain, []

def parse_pdf_links(html_content):
    """
    Parses the HTML content to find PDF links in the property tax bill table.
    Returns a list of URLs to PDF tax bills.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    pdf_links = []

    # Locate the table with id 'TaxBillsTable' and extract all PDF links
    table = soup.find("table", id="TaxBillsTable")
    if not table:
        print("No tax bill table found.")
        return pdf_links

    for link in table.find_all("a", href=True):
        pdf_url = link["href"]
        pdf_links.append(pdf_url)

    return pdf_links

def extract_data_from_pdf(pdf_content):
    """
    Extracts data from PDF content provided as bytes.
    """
    text = ""

    # Extract text from each page
    for page in pdf_content:
        text += page.get_text("text")

    pdf_content.close()

    # Initialize a dictionary to store extracted data
    data = {}

    # Extract total tax due with a flexible pattern
    total_tax_pattern = re.compile(r'\$([\d,]+\.\d{2})\s*DUE (?:NOVEMBER|FEBRUARY) \d{1,2}, \d{4}', re.MULTILINE)
    match = total_tax_pattern.search(text)
    if match:
        data['total_taxes'] = match.group(1).replace(',', '')

    # Extract fiscal year
    year_pattern = re.compile(r'FISCAL YEAR JULY 1, (\d{4}) TO JUNE 30, \d{4}', re.MULTILINE)
    year_match = year_pattern.search(text)
    if year_match:
        data['fiscal_year'] = year_match.group(1)

    # Extract land values
    taxable_value_pattern = re.compile(r'TAXABLE VALUE\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+([\d,]+)', re.MULTILINE)
    taxable_value_match = taxable_value_pattern.search(text)
    if taxable_value_match:
        data['taxable_land_value'] = taxable_value_match.group(1).replace(',', '')
        data['taxable_improvements'] = taxable_value_match.group(3).replace(',', '')

    # Extract land value
    land_value_pattern = re.compile(r'LAND\s*([\d,]+)', re.MULTILINE)
    land_value_match = land_value_pattern.search(text)
    if land_value_match:
        data['land_value'] = land_value_match.group(1).replace(',', '')

    ### Regex pattern does not match field name because of parsing issue
    # Extract total value
    improvements_value_pattern = re.compile(r'IMPROVEMENTS\s+([\d,]+)', re.MULTILINE)
    improvements_value_match = improvements_value_pattern.search(text)
    if improvements_value_match:
        data['total_value'] = improvements_value_match.group(1).replace(',', '')

    # Extract total value (if available)
    total_value_pattern = re.compile(r'TOTAL\s+([\d,]+)', re.MULTILINE)
    total_value_match = total_value_pattern.search(text)
    if total_value_match:
        data['total_value'] = total_value_match.group(1).replace(',', '')

    print(data)
    return data

def process_pdf_link(pdf_link, ain):
    """Processes a PDF link: fetches the PDF and extracts data."""
    try:
        # Extract the token from the URL
        base_url, token_param = pdf_link.split('?')
        token = token_param.split('=')[1]  # Get the token value after '='

        # Define headers with Authorization
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
        }

        # Use a session to manage cookies, if required
        session = requests.Session()

        # Make request with session and headers
        pdf_response = session.get(base_url, headers=headers)
        pdf_response.raise_for_status()  # Check for request errors
        pdf_content = pdf_response.content

        # Process the PDF content
        pdf_data = extract_data_from_pdf(pymupdf.open(stream=pdf_content, filetype="pdf"))
        pdf_data['AIN'] = ain  # Add AIN to the data
        return pdf_data
    except requests.RequestException as e:
        print(f"Error downloading PDF for AIN {ain} from {pdf_link}: {e}")
        return None

def process_ain(ain):
    """Processes a single AIN: gets PDF links and extracts data from each PDF."""
    print(f"Processing AIN: {ain}")
    ain, pdf_links = get_pdf_links(ain)

    pdf_data_list = []
    with ThreadPoolExecutor() as executor:
        future_to_pdf_link = {executor.submit(process_pdf_link, pdf_link, ain): pdf_link for pdf_link in pdf_links}

        for future in as_completed(future_to_pdf_link):
            pdf_data = future.result()
            if pdf_data is not None:
                pdf_data_list.append(pdf_data)

    return pdf_data_list


def process_ains_from_csv(input_csv, output_folder, batch_size=50):
    """
    Reads AINs from a CSV file, retrieves PDF links, extracts data from PDFs,
    and writes the data to separate CSV files for each fiscal year in batches.
    """
    # Create output folder if it doesn’t exist
    os.makedirs(output_folder, exist_ok=True)

    # Read AINs from CSV
    df = pd.read_csv(input_csv)
    ains = df['AIN']

    data_by_year = defaultdict(list)
    batch_count = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []

        # Process AINs in batches
        for i, ain in enumerate(ains, start=1):
            futures.append(executor.submit(process_ain, ain))

            # When the batch size is reached or it's the last item, save progress
            if i % batch_size == 0 or i == len(ains):
                # Collect completed futures
                for future in as_completed(futures):
                    try:
                        pdf_data = future.result()
                        for record in pdf_data:
                            fiscal_year = record.get('fiscal_year')
                            if fiscal_year:
                                data_by_year[fiscal_year].append(record)
                    except Exception as e:
                        print(f"Error processing AIN: {e}")

                # Save data by fiscal year after each batch
                save_data_by_year(data_by_year, output_folder)

                # Reset batch variables
                batch_count += 1
                print(f"Batch {batch_count} saved.")
                data_by_year.clear()  # Clear data after each batch is saved
                futures.clear()  # Reset futures for the next batch

def save_data_by_year(data_by_year, output_folder):
    """
    Saves data grouped by fiscal year to separate CSV files.
    Appends to existing files if they already exist.
    """
    for fiscal_year, records in data_by_year.items():
        output_csv = f"{output_folder}/tax_data_{fiscal_year}.csv"

        # Append to CSV if it exists; otherwise, create a new one
        mode = 'a' if os.path.exists(output_csv) else 'w'
        header = mode == 'w'

        year_df = pd.DataFrame(records)
        year_df.to_csv(output_csv, mode=mode, index=False, header=header)


if __name__ == '__main__':
    # Example usage
    input_csv = 'ains2.csv'  # Input CSV file containing AINs
    output_csv = 'extracted_tax_data'  # Output directory for tax data CSVs
    # Run the processing
    process_ains_from_csv(input_csv, output_csv)