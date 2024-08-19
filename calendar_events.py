def scrape_and_upload_to_gcs_8():
    import json
    from googleapiclient.discovery import build
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError
    from datetime import datetime

    # Configuration
    API_KEY = '***'  # Replace with your Google API Key
    CALENDAR_ID = 'ctfoodbank.events@gmail.com'  # Replace with your public calendar ID

    # Create the Google Calendar service object
    service = build('calendar', 'v3', developerKey=API_KEY)

    # Fetch events from the public calendar
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                        singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    # Prepare data for JSON
    data = []

    for event in events:
        # Extract event details
        event_data = {
            'id': event.get('id'),
            'summary': event.get('summary', ''),
            'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date', '')),
            'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date', '')),
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'creator': event.get('creator', {}).get('email', '')
        }
        data.append(event_data)

    # Convert data to JSON format
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'calendar_events.json'

    # Initialize Google Cloud Storage client
    storage_client = storage.Client()

    try:
        # Upload JSON data to GCS
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(gcs_file_name)
        blob.upload_from_string(json_data, content_type='application/json')
        print("Data successfully uploaded to GCS")
    except GoogleAPIError as e:
        print(f"Failed to upload to GCS: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scrape_and_upload_to_gcs_8()