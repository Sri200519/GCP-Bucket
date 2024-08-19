def scrape_and_upload_to_gcs_16():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # URL of the webpage to scrape
    url = 'https://ctserc.org/services'

    # Make an HTTP GET request to the webpage
    response = requests.get(url)

    # Parse the HTML content of the webpage
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the div with the id 'serc-services'
    services_div = soup.find('div', id='serc-services')

    # Extract text from the div
    services_text = services_div.get_text(strip=True) if services_div else 'Div with id "serc-services" not found.'

    # Prepare the data
    data = {
        'source_url': url,
        'content': services_text
    }

    # Convert data to JSON format
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'state_education_resource_center.json'

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

scrape_and_upload_to_gcs_16()