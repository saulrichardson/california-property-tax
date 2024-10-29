import requests
from bs4 import BeautifulSoup
import time
import pymupdf
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    payload = {"ain": ain}
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
    # Open the PDF from bytes
    doc = pymupdf.open(stream=pdf_content, filetype="pdf")
    text = ""

    # Extract text from each page
    for page in doc:
        text += page.get_text("text")

    doc.close()

    # Extract relevant fields with regular expressions
    data = {}

    # 1. Agency rates and amounts
    agency_pattern = re.compile(r'(\w[\w\s]+)\s+\(?(\d{3}\)?[-\d]{0,10})?\s*([\d.]+)\s+\$\s*([\d.,]+)')
    data['agencies'] = [
        {'agency': match[0].strip(), 'rate': match[2], 'amount': match[3]}
        for match in agency_pattern.findall(text)
    ]

    # 2. Current assessed value and taxable value
    assessed_pattern = re.compile(r'CURRENT ASSESSED VALUE\s+TAXABLE VALUE\s+([\d,]+)\s+([\d,]+)')
    match = assessed_pattern.search(text)
    if match:
        data['current_assessed_value'] = match.group(1).replace(',', '')
        data['taxable_value'] = match.group(2).replace(',', '')

    # 3. Exemption amount
    exemption_pattern = re.compile(r'LESS EXEMPTION:\s*\$?\s*([\d,]+)')
    match = exemption_pattern.search(text)
    if match:
        data['exemption'] = match.group(1).replace(',', '')

    # 4. Total taxes paid ("1ST + 2ND" installment total)
    total_tax_pattern = re.compile(r'1ST Installment\s+\$\s*([\d,]+)\s*2ND Installment\s+\$\s*([\d,]+)')
    match = total_tax_pattern.search(text)
    if match:
        first_installment = float(match.group(1).replace(',', ''))
        second_installment = float(match.group(2).replace(',', ''))
        data['total_taxes'] = first_installment + second_installment

    return data

def process_pdf_link(pdf_link, ain):
    """Processes a PDF link: fetches the PDF and extracts data."""
    try:
        pdf_response = requests.get(pdf_link)
        pdf_response.raise_for_status()  # Check for request errors
        pdf_content = pdf_response.content
        pdf_data = extract_data_from_pdf(pdf_content)
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

def process_ains_from_csv(input_csv, output_csv):
    """
    Reads AINs from a CSV file, retrieves PDF links, extracts data from PDFs,
    and writes the data back to the CSV file.
    """
    # Read AINs from CSV
    df = pd.read_csv(input_csv)
    all_pdf_data = []

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_ain = {executor.submit(process_ain, ain): ain for ain in df['AIN']}

        for future in as_completed(future_to_ain):
            ain = future_to_ain[future]
            try:
                pdf_data = future.result()
                all_pdf_data.extend(pdf_data)
            except Exception as e:
                print(f"Error processing AIN {ain}: {e}")

    # Create a DataFrame and save it to CSV
    pdf_data_df = pd.DataFrame(all_pdf_data)
    pdf_data_df.to_csv(output_csv, index=False)
    print(f"Extracted data saved to {output_csv}")


if __name__ == '__main__':
    # Example usage
    input_csv = 'ains.csv'  # Input CSV file containing AINs
    output_csv = 'extracted_data.csv'  # Output CSV file for extracted data
    # Run the processing
    process_ains_from_csv(input_csv, output_csv)