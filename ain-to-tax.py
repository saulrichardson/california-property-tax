"""
Webscrapper that pulls property tax bill for user provided APNs
"""
# TODO: FIX THIS BC IT DOESN'T WORK'
from requests_html import HTMLSession
from lxml.html.clean import Cleaner
import pandas as pd

def fetch_tax_data(ain):
    url = f'https://portal.assessor.lacounty.gov/parceldetail/{ain}'
    session = HTMLSession()
    response = session.get(url)

    try:

        # Extract data
        data = {}
        data['AIN'] = ain

        # Find the table containing tax values
        table = response.html.find('.table-condensed', first=True)
        if not table:
            print("Tax value table not found.")
            return None

        # Look for the row containing Improvements
        rows = table.find('tr')
        for row in rows:
            columns = row.find('td')
            if len(columns) > 1 and columns[0].text.strip() == 'Improvements':
                assessed_value = columns[2].text.strip().replace('$', '').replace(',', '')
                data['Assessed Value'] = int(assessed_value)
                break

        return data

    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def save_to_csv(data, filename):
    df = pd.DataFrame(data, index=[0])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == '__main__':
    ain = '5138015053'  # Example AIN
    tax_data = fetch_tax_data(ain)

    if tax_data:
        print(tax_data)
        #save_to_csv(tax_data, 'tax_data.csv')
