import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

# Input and output file paths
input_csv = "Lawrenceville_Master_List.csv"
output_csv = "output_property_data.csv"
new_records_csv = "new_records_property_data.csv"

# Read the input CSV
data = pd.read_csv(input_csv)

print("Initial Data Preview:")
print(data.head())

# Ensure the 'Address' column exists
if 'Address' not in data.columns:
    raise ValueError("The input CSV must have a column named 'Address'.")

# Fill NaN values and ensure the column is a string
data['Address'] = data['Address'].fillna('').astype(str)

# Normalize addresses by removing "1/2"
data['Address'] = data['Address'].str.replace(r'\s1/2', '', regex=True)

# Extract StreetNumber and StreetName
data['StreetNumber'] = data['Address'].str.extract(r'^(\d+)\s')[0]
data['StreetName'] = data['Address'].str.extract(r'^\d+\s(.+)')[0]

print("Extracted StreetNumber and StreetName:")
print(data[['Address', 'StreetNumber', 'StreetName']].head())

# Check existing output file to resume progress
processed_addresses = set()
if os.path.exists(output_csv):
    existing_data = pd.read_csv(output_csv)
    processed_addresses = set(existing_data['Address'].tolist())
    print(f"Found {len(processed_addresses)} already-processed addresses.")

# Filter data to exclude already-processed addresses
data = data[~data['Address'].isin(processed_addresses)]
print(f"{len(data)} addresses remaining to process.")

# Initialize Selenium WebDriver
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Uncomment to run in headless mode
driver = webdriver.Chrome(options=options)

output_data = []
new_data = []  # To store new records for separate CSV

# Function to handle the "I Agree" button
def handle_i_agree_button(driver):
    try:
        agree_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "agreeBtn"))
        )
        driver.execute_script("arguments[0].click();", agree_button)
        print("Clicked the 'I Agree' button.")
    except Exception:
        print("'I Agree' button not found or already handled.")

# Function to check for the results table and click the first Parcel ID link
def check_results_table_and_click(driver):
    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchResultGV"))
        )
        print("Results table found.")

        first_parcel_link = table.find_element(By.XPATH, ".//tr[2]/td[1]/a")
        first_parcel_link.click()
        print("Clicked on the first Parcel ID link.")
        return True
    except Exception as e:
        print("Results table not found or unable to click the Parcel ID link:", e)
        return False

# Function to retrieve data from the website
def retrieve_data(driver):
    # Extract General Info
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "MainContent_Header1_GeneralInfo"))
    )
    general_info_tab = driver.find_element(By.ID, "MainContent_Header1_GeneralInfo")
    general_info_tab.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "MainContent_schoolDistrictLbl"))
    )

    general_info = {
        "School District": driver.find_element(By.ID, "MainContent_schoolDistrictLbl").text,
        "Tax Code": driver.find_element(By.ID, "MainContent_taxCodeLbl").text,
        "Class": driver.find_element(By.ID, "MainContent_classLbl").text,
        "Use Code": driver.find_element(By.ID, "MainContent_useCodeLbl").text,
        "Neighborhood Code": driver.find_element(By.ID, "MainContent_neighborhoodCodeLbl").text,
        "Owner Code": driver.find_element(By.ID, "MainContent_ownerCodeLbl").text,
        "Recording Date": driver.find_element(By.ID, "MainContent_recordingDateLbl").text,
        "Sale Date": driver.find_element(By.ID, "MainContent_saleDateLbl").text,
        "Sale Price": driver.find_element(By.ID, "MainContent_salePrice").text,
        "Lot Area": driver.find_element(By.ID, "MainContent_lotAreaLbl").text,
    }

    # Extract Tax Info
    tax_info_tab = driver.find_element(By.ID, "MainContent_Header1_TaxInfo")
    tax_info_tab.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "MainContent_netTax"))
    )

    tax_info = {
        "Net Tax Due": driver.find_element(By.ID, "MainContent_netTax").text,
        "Gross Tax Due": driver.find_element(By.ID, "MainContent_grossTax").text,
        "Millage Rate": driver.find_element(By.ID, "MainContent_milageRate").text,
        "Taxable Market Value": driver.find_element(By.ID, "MainContent_taxableValue").text,
        "Lot and Block": driver.find_element(By.ID, "MainContent_parcelID").text,
    }

    # Extract Owner History
    owner_history_tab = driver.find_element(By.ID, "MainContent_Header1_OwnerHistory")
    owner_history_tab.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
    )

    owner_history = []
    rows = driver.find_elements(By.CSS_SELECTOR, ".table.table-striped.table-condensed tbody tr")
    for r in rows:
        cols = r.find_elements(By.TAG_NAME, "td")
        if len(cols) >= 3:
            owner_history.append({
                "Owner": cols[0].text,
                "Sale Date": cols[1].text,
                "Sale Price": cols[2].text,
            })

    return general_info, tax_info, owner_history

# Iterate over the DataFrame
for index, row in data.iterrows():
    try:
        print(f"Processing Address: {row['Address']} -> StreetNumber: {row['StreetNumber']}, StreetName: {row['StreetName']}")

        # Navigate to the website
        driver.get("https://www2.alleghenycounty.us/RealEstate/search.aspx")

        # Handle the "I Agree" button
        handle_i_agree_button(driver)

        # Enter house number
        house_number_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "houseNumberTxtBox"))
        )
        house_number_input.clear()
        house_number_input.send_keys(row['StreetNumber'])

        # Enter street name
        street_name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "streetNameTxtBox"))
        )
        street_name_input.clear()
        street_name_input.send_keys(row['StreetName'])

        # Click the "Search" button
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "searchBtn"))
        )
        driver.execute_script("arguments[0].click();", search_button)
        print("Clicked the 'Search' button.")

        # Check results table and click the first Parcel ID link
        if not check_results_table_and_click(driver):
            print(f"No results for address: {row['Address']}")
            continue

        # Retrieve data
        general_info, tax_info, owner_history = retrieve_data(driver)

        # Combine all data
        record = {
            "Address": row['Address'],
            **general_info,
            **tax_info,
            "Owner History": owner_history,
        }
        output_data.append(record)
        new_data.append(record)  # Add to the new records list

    except Exception as e:
        print(f"Error processing address {row['Address']}: {e}")

# Close the browser
driver.quit()

# Save the output to a CSV (append mode)
if output_data:
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)

# Save new records separately
if new_data:
    new_data_df = pd.DataFrame(new_data)
    new_data_df.to_csv(new_records_csv, index=False)
    print(f"New data saved to {new_records_csv}.")

print("Processing completed.")
