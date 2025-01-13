import pandas as pd

# Load the CSV file
#df = pd.read_csv("merged_shape_business_data.csv")

# Count rows where 'Business Name' is not empty
#business_count = df['Business Name'].notna().sum()

#print(f"Number of rows with an entry in the 'Business Name' column: {business_count}")

# import pandas as pd
# import re

# # Function to clean and standardize addresses
# def clean_address(address):
#     if pd.isna(address):
#         return "", ""
#     address = address.lower().strip()  # Convert to lowercase and trim
#     address = re.sub(r',\s*pittsburgh', '', address)  # Remove ", Pittsburgh"
#     # Separate number and street
#     match = re.match(r'(\d+)\s+(.*)', address)
#     if match:
#         number = match.group(1)
#         street = match.group(2)
#         # Standardize street type abbreviations
#         street = re.sub(r'\b(street|st)\b', 'st', street)
#         street = re.sub(r'\b(avenue|ave)\b', 'ave', street)
#         street = re.sub(r'\b(boulevard|blvd)\b', 'blvd', street)
#         street = re.sub(r'\b(road|rd)\b', 'rd', street)
#         street = re.sub(r'\b(suite|ste)\b', 'ste', street)
#         street = re.sub(r'\b(apartment|apt)\b', 'apt', street)
#         street = re.sub(r'\s+', ' ', street)  # Remove extra spaces
#         return number, street.strip()
#     return "", address.strip()

# # Load the datasets
# lawrenceville_data = pd.read_csv('lawrenceville_data_clean.csv')
# bounding_data = pd.read_csv('cleaned_addresses_with_flags.csv')

# # Clean and split address components
# lawrenceville_data[['Street_Number', 'Street_Name']] = lawrenceville_data['FULL_ADDRE'].apply(clean_address).apply(pd.Series)
# bounding_data[['Street_Number', 'Street_Name']] = bounding_data['Address_bounding'].apply(clean_address).apply(pd.Series)

# # Perform a full outer join on 'Street_Number' and 'Street_Name' columns
# merged_data = pd.merge(
#     lawrenceville_data,
#     bounding_data,
#     how='outer',
#     left_on=['Street_Number', 'Street_Name'],
#     right_on=['Street_Number', 'Street_Name'],
#     suffixes=('_lawrenceville', '_bounding')
# )

# # Select and rename columns as necessary for the final output, using 'Address_bounding' if 'FULL_ADDRE' is missing
# merged_data['Address'] = merged_data['FULL_ADDRE'].combine_first(merged_data['Address_bounding'])

# # Create the final output structure
# final_data = merged_data[['Address', 'Name_bounding', 'Street_bounding', 'Rating_bounding', 'Latitude_bounding', 'Longitude_bounding', 'flag']]

# # Rename columns to match the original structure
# final_data.columns = [
#     'Address', 'Business Name', 'Street', 'Rating', 'Latitude', 'Longitude', 'Flag'
# ]

# # Save the result to a new CSV file
# final_data.to_csv('merged_shape_business_data_2.csv', index=False)

# print("Merged data saved to 'merged_shape_business_data_2.csv'")

# import pandas as pd
# import re

# # Load the dataset
# data = pd.read_csv('merged_shape_business_data_2.csv')

# # Function to clean addresses
# def clean_address(address):
#     address = address.replace('"', '')
#     # Remove ", Millvale" at the end, case-insensitive
#     address = re.sub(r',.*$', '', address)
#     # Further standardization can be added here if necessary
#     return address.strip()

# # Apply the cleaning function to the 'Address' column
# data['Address'] = data['Address'].apply(clean_address)

# # Save the cleaned data to a new CSV file
# data.to_csv('cleaned_merged_shape_business_data.csv', index=False)

# print("Cleaned data saved to 'cleaned_merged_shape_business_data.csv'")

import re 
# Load your data
#lawrenceville_data = pd.read_csv('lawrenceville_data_cleaned_updated.csv')

# # Convert address and business name columns to lowercase for case-insensitive comparison
# lawrenceville_data['Address'] = lawrenceville_data['Address'].str.lower()
# lawrenceville_data['Business Name'] = lawrenceville_data['Business Name'].str.lower()

# # Function to standardize apartment address formats
# def standardize_address(address):
#     # Replace variations of "apt" with a consistent format
#     address = re.sub(r'\bapt\b', 'apartment', address)  # Replace 'apt' with 'apartment'
#     return address

# # Apply the standardization to the Address column
# lawrenceville_data['Address'] = lawrenceville_data['Address'].apply(standardize_address)

# # Iterate through the rows to clear 'Business Name' if it matches an 'Address'
# for idx, row in lawrenceville_data.iterrows():
#     # Check for equality ignoring case
#     if row['Business Name'] == row['Address']:
#         lawrenceville_data.at[idx, 'Business Name'] = ''

# import pandas as pd
# from fuzzywuzzy import fuzz

# # Load the CSV file
# df = pd.read_csv('lawrenceville_data_with_business_info.csv')  # Replace with the actual filename

# # Function to check if the address matches the majority of the characters in the business name
# def is_similar(address, business_name, threshold=80):
#     # Check for NaN values
#     if pd.isna(address) or pd.isna(business_name):
#         return False
#     # Calculate similarity ratio
#     similarity = fuzz.ratio(address.lower(), business_name.lower())
#     return similarity >= threshold

# # Apply the function to determine if the business name should be cleared
# df['Business Name'] = df.apply(
#     lambda row: '' if is_similar(str(row['Address']), str(row['Business Name'])) else row['Business Name'],
#     axis=1
# )

# # Save the cleaned DataFrame to a new CSV
# df.to_csv('cleaned_lawrenceville_data_with_business_info.csv', index=False)

df = pd.read_csv("cleaned_lawrenceville_data_with_business_info.csv")

#Count rows where 'Business Name' is not empty
business_count = df['Business Name'].notna().sum()

print(f"Number of rows with an entry in the 'Business Name' column: {business_count}")
