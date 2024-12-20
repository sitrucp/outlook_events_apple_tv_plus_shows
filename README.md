# Apple TV+ Data Outlook Event Creation

This repository contains scripts to process Apple TV+ viewing history data and create Outlook calendar events using the Microsoft Graph API.

## Features
1. **Data Cleaning**: Preprocess viewing history data from Apple TV+.
2. **Event Creation**: Create Outlook calendar events for viewing entries.
3. **Logging**: Maintain logs for processed events and last event creation.

## Workflow Summary
1. Request and download your viewing history data from Apple TV+.
2. Preprocess the data using `process_raw_data.py`.
3. Use `create_events.py` to create Outlook events from the cleaned data.
4. Check logs for details and track processing.

## Prerequisites
- **Microsoft Graph API Credentials**: `client_id`, `tenant_id`, `client_secret`, `user_id`
- **Required Libraries**:  `pandas`, `numpy`, `requests`, `pytz`

## Usage

### Step 1: Obtain Your Apple TV+ Viewing History
1. Go to [Apple Data and Privacy](https://privacy.apple.com).
2. Log in with your Apple ID.
3. Request your data by selecting **"Request your data"**. It may take a few days to receive the data.
4. Once notified via email, download the data.
5. Extract the file `TV App Favorites and Activity.json` from the path:
   ```
   Apple_Media_Services\Stores Activity\Apple TV and Podcast Information\TV App Favorites and Activity.json
   ```

### Step 2: Clean the Data
Run the `process_raw_data.py` script to clean the downloaded data file `TV App Favorites and Activity.json`.

The script outputs a cleaned and preprocessed file (e.g., `TV App Favorites and Activity_clean.csv`).

### Step 3: Create Outlook Calendar Events
Run the `create_events.py` script to create calendar events using the cleaned data file generated in Step 2.

## Logs
Two logs are created for tracking progress:
1. **Create Events Log**: Tracks processing details and errors during event creation (`create_events_log.txt`).
2. **Last Event Log**: Tracks the most recent processed event to start from in future runs (`last_event_log.csv`).

## Example Directory Structure
```
repo/
|
├── process_raw_data.py
├── create_events.py
├── TV App Favorites and Activity.json
├── TV App Favorites and Activity_clean.csv
│── create_events_log.txt
│── last_event_log.csv
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.
