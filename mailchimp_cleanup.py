import pandas as pd
import numpy as np
import os
import re

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

# Function to clean and standardize tags
def clean_tags(tags):
    # Remove extra quotes and whitespace
    tags = [re.sub(r'^"|"$', '', tag.strip()) for tag in tags.split(',')]
    # Deduplicate tags
    return ', '.join(sorted(set(filter(None, tags))))

# Loop through each file and append the audience tag to the existing 'TAGS' column
for file, audience_tag in audience_files.items():
    # Construct file path
    file_path = os.path.expanduser(f'~/Documents/Mailchimp/{file}')
    
    # Load each CSV file
    df = pd.read_csv(file_path)
    
    # Replace any NaN values in the 'TAGS' column with an empty string for safe concatenation
    df['TAGS'] = df['TAGS'].fillna('')
    
    # Append the new audience tag to the existing 'TAGS' column, removing duplicates and cleaning tags
    df['TAGS'] = df['TAGS'].apply(lambda x: clean_tags(f"{x}, {audience_tag}" if x else audience_tag))
    
    # Append to the list
    dataframes.append(df)

# Concatenate all DataFrames into a single DataFrame
combined_df = pd.concat(dataframes)

# Group by 'Email Address' and merge unique tags while keeping all other columns
combined_df = combined_df.groupby('Email Address', as_index=False).agg({
    col: 'first' if col != 'TAGS' else lambda x: clean_tags(', '.join(x))
    for col in combined_df.columns
})

