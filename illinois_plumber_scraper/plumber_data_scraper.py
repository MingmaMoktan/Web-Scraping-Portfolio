import time
import requests
import pandas as pd

url = "https://webapps1.chicago.gov/licensedcontractors/allcontractors/paginated/plumbing"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://webapps1.chicago.gov/licensedcontractors/plumbing",
}

params = {
    "draw": "1",
    "search[value]": "",
    "search[regex]": "false",
    "order[0][column]": "1",
    "order[0][dir]": "asc",
    "columns[0][data]": "licenseNo",
    "columns[0][name]": "LICENSENO",
    "columns[1][data]": "name",
    "columns[1][name]": "NAME",
    "columns[2][data]": "address",
    "columns[2][name]": "ADDRESS",
    "columns[3][data]": "phone",
    "columns[3][name]": "PHONE",
    "columns[4][data]": "licenseExpDate",
    "columns[4][name]": "LICENSEEXPDATE",
    "columns[5][data]": "insBond_ExpDt",
    "columns[5][name]": "INSBOND_EXPDT",
    "columns[6][data]": "lic_Inactive",
    "columns[6][name]": "LIC_INACTIVE",
}

session = requests.Session()
session.headers.update(headers)

all_records = []
start = 0
length = 100
total_records = 1

print("Starting extraction...")

while start < total_records:
    params["start"] = str(start)
    params["length"] = str(length)
    params["_"] = str(int(time.time() * 1000))

    response = session.get(url, params=params)

    if response.status_code != 200:
        print(f"Request failed with status code {response.status_code}")
        break

    try:
        data = response.json()
        total_records = int(data.get("recordsTotal", 0))
        rows = data.get("data", [])
        all_records.extend(rows)

        print(f"Fetched {len(all_records)} of {total_records} records...")
        start += length
        time.sleep(0.5)
    except Exception as e:
        print(f"Error parsing response at offset {start}: {e}")
        break

if all_records:
    df = pd.DataFrame(all_records)
    
    columns_map = {
        "licenseNo": "License Number",
        "name": "Name",
        "address": "Address",
        "phone": "Phone",
        "licenseExpDate": "License Expiration Date",
        "insBond_ExpDt": "Bond Expiration Date",
        "lic_Inactive": "License Inactive?"
    }
    df = df.rename(columns=columns_map)

    output_filename = "illinois_plumbers_data.csv"
    df.to_csv(output_filename, index=False)
    print(f"Done. Saved {len(df)} records to {output_filename}")