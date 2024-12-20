import json
import pandas as pd
from datetime import datetime, timedelta


input_file = 'TV App Favorites and Activity.json'
output_file = 'TV App Favorites and Activity.csv'

# Function to convert milliseconds to HH:MM format
def ms_to_hhmm(ms):
    seconds = int(ms / 1000)
    return f"{seconds // 3600:02d}:{(seconds % 3600) // 60:02d}"

def extract_details(description, media_type):
    # Split the description at the first occurrence of " ("
    parts = description.split(" (", 1)
    details = {}
    
    # The first part is the show name
    details['Show Name'] = parts[0]

    # Add media_type to details directly
    details['Type'] = media_type
    
    # Process the rest of the description for episode details
    episode_details = parts[1].split(', ') if len(parts) > 1 else []

    for part in episode_details:
        if 'Episode Title' in part:
            details['Episode Title'] = part.split('[', 1)[1].split(']', 1)[0]
        elif 'Episode Number' in part:
            # Directly use the string without converting to int
            details['Episode Number'] = part.split('[', 1)[1].split(']', 1)[0]
        elif 'Season Number' in part:
            # Directly use the string without converting to int
            details['Season Number'] = part.split('[', 1)[1].split(']', 1)[0]

    return details

# Load the JSON data
with open(input_file, 'r') as file:
    data = json.load(file)

extracted_data = []  # List to accumulate the extracted details

# Process each event
for event in data['events']:
    interpretation = event['event_interpretation']
    stored_event = event['stored_event']

    # Correctly extract media_type from the event data
    media_type = stored_event['media_type']  # Assuming 'media_type' is the correct key

    # Pass media_type to the extract_details function
    details = extract_details(interpretation['human_readable_media_description'], media_type)

    # Convert timestamp and play_cursor_in_milliseconds
    end_date = datetime.fromtimestamp(stored_event['timestamp'] / 1000.0)
    duration = ms_to_hhmm(stored_event['play_cursor_in_milliseconds'])
    start_date = end_date - timedelta(milliseconds=stored_event['play_cursor_in_milliseconds'])

    details.update({
        'End Datetime': end_date.strftime('%Y-%m-%d %H:%M:%S'),
        'Duration': duration,
        'Start Datetime': start_date.strftime('%Y-%m-%d %H:%M:%S')
    })

    extracted_data.append(details)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(extracted_data)

# After the DataFrame is created and before it's saved to CSV
df['Season Number'] = df['Season Number'].astype(str)
df['Episode Number'] = df['Episode Number'].astype(str)

# Use .apply() with a lambda function to strip trailing '.0' for any numeric-like strings, if still necessary
df['Season Number'] = df['Season Number'].apply(lambda x: x.rstrip('.0') if '.' in x else x)
df['Episode Number'] = df['Episode Number'].apply(lambda x: x.rstrip('.0') if '.' in x else x)

# Define the desired column order
column_order = ['Show Name', 'Episode Title', 'Season Number', 'Episode Number', 'Start Datetime', 'End Datetime', 'Duration', 'Type']

# Convert the list of dictionaries to a DataFrame with a specific column order
df = pd.DataFrame(extracted_data, columns=column_order)

# Reorder the DataFrame columns before saving
df = df[column_order]

# Create a temporary column for sorting
df['Sort Datetime'] = pd.to_datetime(df['Start Datetime'])

# Sort the DataFrame by the temporary column (descending order)
df = df.sort_values(by='Sort Datetime', ascending=False)

# Drop the temporary sorting column
df = df.drop(columns=['Sort Datetime'])

# Now save the DataFrame to a CSV file with the columns in the desired order
df.to_csv(output_file, index=False)

print("Data saved to", output_file)
