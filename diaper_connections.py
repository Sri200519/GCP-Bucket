def scrape_and_upload_to_gcs_11():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # URL of the website to scrape
    URL = 'https://www.thediaperbank.org/diaper-connections/'

    # Send a GET request to the website
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Define blocks to scrape
    blocks = [
        {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_1 et_pb_css_mix_blend_mode_passthrough et-last-child'},
        {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_2 et_pb_css_mix_blend_mode_passthrough'},
        {'class': 'et_pb_column et_pb_column_2_3 et_pb_column_5 et_pb_css_mix_blend_mode_passthrough et-last-child'}
    ]

    documents = []

    for block in blocks:
        for div in soup.find_all('div', class_=block['class']):
            # Extracting text from the div
            text = div.get_text(strip=True)
            # Adding text to the documents list
            documents.append({'text': text})

    # Convert documents to JSON format
    json_data = json.dumps(documents, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'diaper_connections.json'

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

scrape_and_upload_to_gcs_11()