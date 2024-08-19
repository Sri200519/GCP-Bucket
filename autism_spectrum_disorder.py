def scrape_and_upload_to_gcs_5():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # Fetch the webpage content
    url = 'https://www.connecticutchildrens.org/specialties-conditions/developmental-behavioral-pediatrics/autism-spectrum-disorder-asd'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract data
    data = []

    # Function to clean the text content
    def clean_text(text):
        return text.strip()  # Clean up the text content

    # Find and extract all <p> tags
    for tag in soup.find_all('p'):
        text_content = clean_text(tag.get_text(strip=True))
        data.append({
            'tag': tag.name,
            'content': text_content
        })

    # Convert data to JSON format
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_key = 'autism_spectrum_disorder.json'

    # Initialize Google Cloud Storage client
    storage_client = storage.Client()

    try:
        # Upload JSON data to GCS
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(gcs_key)
        blob.upload_from_string(json_data, content_type='application/json')
        print("Data successfully uploaded to GCS")
    except GoogleAPIError as e:
        print(f"Failed to upload to GCS: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scrape_and_upload_to_gcs_5()