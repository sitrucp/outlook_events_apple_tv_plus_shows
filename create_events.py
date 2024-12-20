import pandas as pd
import requests
#from datetime import datetime, timedelta
#import pytz
#from dateutil import parser
import sys
import os
import logging


#--- Get msgraph config variables ---#
config_msgraph_path = os.getenv("ENV_VARS_PATH")  # Get path to directory contaiining config_msgraph.py
if not config_msgraph_path:
    raise ValueError("ENV_VARS_PATH environment variable not set")
sys.path.insert(0, config_msgraph_path)

from config_msgraph import config_msgraph

client_id=config_msgraph["client_id"]
tenant_id=config_msgraph["tenant_id"]
client_secret=config_msgraph["client_secret"]
user_id=config_msgraph["user_id"]

#--- Define files ---#
input_file = "TV App Favorites and Activity.csv"
last_event_log = "last_event_log.csv"
create_event_log = "create_event_log.txt"

#--- Setup logging ---#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(create_event_log),
        logging.StreamHandler(sys.stdout)
    ]
)

#--- Function to obtain an access token ---#
def get_access_token(client_id, tenant_id, client_secret):
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_id': client_id,
        'scope': 'https://graph.microsoft.com/.default',
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Raises an exception for HTTP error codes
    return response.json().get('access_token')

#--- Function to create a calendar event using Microsoft Graph API ---#
def create_calendar_event(access_token, row):
    # Title format changed to include show, name, season, and episode
    if row['Type'] == 'TV':
        title = f"Apple TV+: {row['Show Name']} {row['Episode Title']} S:{row['Season Number']} E:{row['Episode Number']}"
    else:
        title = f"Apple TV+: {row['Show Name']}"

    description_html = (
        f"Title: {title}<br>"
        f"Start: {row['Start Datetime']}<br>"
        f"End: {row['End Datetime']}<br>"
        f"Duration: {row['Duration']}"
    )

    event_payload = {
        "subject": title,
        "start": {"dateTime": row['Start Datetime'], "timeZone": "Eastern Standard Time"},
        "end": {"dateTime": row['End Datetime'], "timeZone": "Eastern Standard Time"},
        "body": {"contentType": "HTML", "content": description_html},
        "categories": ["Apple TV+"]
    }

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    response = requests.post(f"https://graph.microsoft.com/v1.0/users/{user_id}/events", headers=headers, json=event_payload)
    response.raise_for_status()

#--- Main script to process the CSV data and create events ---#
def main():
    access_token = get_access_token(client_id, tenant_id, client_secret)

    # Read the last event date from last_event_log.csv
    log_df = pd.read_csv(last_event_log)
    last_event_date = pd.to_datetime(log_df['last_event_date'].iloc[0])
    
    # Read the apple data file
    df = pd.read_csv(input_file)

    # Convert 'Start Datetime' to datetime objects
    df['Start Datetime'] = pd.to_datetime(df['Start Datetime'])

    # Filter out events on or before the last event date
    df = df[df['Start Datetime'] > last_event_date]

    # Convert 'Start Datetime' and 'End Datetime' columns to datetime objects and then to ISO format without 'Z'
    #df['Start Datetime'] = pd.to_datetime(df['Start Datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')
    #df['End Datetime'] = pd.to_datetime(df['End Datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Convert 'Start Datetime' and 'End Datetime' columns to ISO format without 'Z'
    df['Start Datetime'] = df['Start Datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    df['End Datetime'] = pd.to_datetime(df['End Datetime']).dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Explicitly convert Season Number and Episode Number to strings
    df['Season Number'] = df['Season Number'].astype(str)
    df['Episode Number'] = df['Episode Number'].astype(str)

    # Now iterate with the updated DataFrame including duration
    for index, row in df.iterrows():
        try:
            create_calendar_event(access_token, row)  # Ensure this function uses updated DataFrame columns
            # Success message adjustment to include the title from the DataFrame
            if row['Type'] == 'TV':
                print(f"Event created for {row['Show Name']} {row['Episode Title']} S:{row['Season Number']} E:{row['Episode Number']}")
            else:
                print(f"Event created for {row['Show Name']}")
            #break # this is used to stop after one event creation to test if it is working as desired
        except Exception as e:
            if row['Type'] == 'TV':
                print(f"Event created for {row['Show Name']} {row['Episode Title']} S:{row['Season Number']} E:{row['Episode Number']}")
            else:
                print(f"Error creating event for {row['Show Name']}: {e}")

if __name__ == "__main__":
    main()

