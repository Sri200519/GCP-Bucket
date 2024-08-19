def scrape_and_upload_to_gcs_17():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # URL of the website to scrape
    URL = 'https://portal.ct.gov/dss/archived-folder/temporary-family-assistance---tfa'

    # Send a GET request to the website
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Define block to scrape
    block_class = 'content'

    # Extract the content from the specified block
    content_div = soup.find('div', class_=block_class)
    if content_div:
        text = content_div.get_text(strip=True)
    else:
        text = 'Content not found.'

    # Convert data to JSON format
    data = {
        'content': text
    }
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'temporary_family_assistance.json'

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

scrape_and_upload_to_gcs_17()