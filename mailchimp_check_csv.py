import pandas as pd
import numpy as np
import os
import logging

# Set up logging
logging.basicConfig(filename='verification_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define audience files and their corresponding tags
audience_files = {
    'subscribed_2023_membership.csv': '2023 Membership',
    'subscribed_2024_audience.csv': '2024 Membership',
    'subscribed_combined_amazon_CDAM_audience.csv': 'Combined Amazon + CDAM',
    'subscribed_amazon_updates.csv': 'Amazon Updates',
    'subscribed_comm_dev_activities_meeting.csv': 'Community Development Activities Meeting',
    'subscribed_ice_house_tenants.csv': 'Ice House Tenants',
    'subscribed_LVPGH_news_updates_newsletter.csv': '#LVPGH News & Updates Newsletter',
    'subscribed_lawrenceville_businesses.csv': 'Lawrenceville Businesses'
}

# Initialize an empty list to store DataFrames
dataframes = []

# Loop through each file and append the audience tag to the existing 'TAGS' column
for file, audience_tag in audience_files.items():
    # Construct file path
    file_path = os.path.expanduser(f'~/Documents/Mailchimp/{file}')
    
    # Load each CSV file
    df = pd.read_csv(file_path)
    
    # Replace any NaN values in the 'TAGS' column with an empty string for safe concatenation
    df['TAGS'] = df['TAGS'].replace(np.nan, '', regex=True)
    
    # Append the new audience tag to the existing 'TAGS' column, row by row
    df['TAGS'] = df['TAGS'].apply(lambda x: x + ', ' + audience_tag if x else audience_tag)
    
    # Append to the list
    dataframes.append(df)

# Concatenate all DataFrames into a single DataFrame
combined_df = pd.concat(dataframes)

# --- Check 1: Verify Row Counts ---
original_row_count = sum(pd.read_csv(os.path.expanduser(f'~/Documents/Mailchimp/{file}')).shape[0] for file in audience_files.keys())
combined_row_count = combined_df.shape[0]

logging.info(f"Original total row count: {original_row_count}")
logging.info(f"Combined total row count (before grouping): {combined_row_count}")

if original_row_count == combined_row_count:
    logging.info("Row count matches before grouping.")
else:
    logging.warning("Row count mismatch before grouping.")

# --- Check 2: Verify Unique Emails and Tags ---

# Group by 'Email Address' in original_df and consolidate tags
original_data = []
for file, audience_tag in audience_files.items():
    df = pd.read_csv(os.path.expanduser(f'~/Documents/Mailchimp/{file}'))
    df['Source Tag'] = audience_tag
    original_data.append(df)

original_df = pd.concat(original_data)

# Consolidate tags for each email in original data
original_tags_df = original_df.groupby('Email Address')['Source Tag'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()

# Consolidate tags in combined DataFrame
combined_tags_df = combined_df.groupby('Email Address', as_index=False).agg({
    col: 'first' if col != 'TAGS' else lambda x: ', '.join(sorted(set(tag for tag in ', '.join(x).split(', ') if tag and tag.lower() != 'nan')))
    for col in combined_df.columns
})

# Compare tags in combined and original data
verification_df = pd.merge(combined_tags_df[['Email Address', 'TAGS']], original_tags_df, left_on='Email Address', right_on='Email Address', how='outer', suffixes=('_combined', '_original'))
mismatches = verification_df[verification_df['TAGS'] != verification_df['Source Tag']]

if mismatches.empty:
    logging.info("All tags match the original data.")
else:
    logging.warning("There are mismatches in the tags:")
    logging.warning(mismatches.to_string())

# --- Check 3: Verify that All Columns are Present and Correct ---

for file in audience_files.keys():
    df = pd.read_csv(os.path.expanduser(f'~/Documents/Mailchimp/{file}'))
    missing_columns = [col for col in df.columns if col not in combined_df.columns]
    
    if not missing_columns:
        logging.info(f"All columns from {file} are present in the combined file.")
    else:
        logging.warning(f"Missing columns from {file}: {missing_columns}")

# --- Check 4: Manual Spot Check of Sample Rows ---

sample = combined_tags_df.sample(10, random_state=1)
logging.info("Sample rows to verify manually:")
logging.info(sample.to_string())
