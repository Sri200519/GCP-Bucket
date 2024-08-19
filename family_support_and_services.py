def scrape_and_upload_to_gcs_12():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # Fetch the webpage content
    url = "https://portal.ct.gov/dds/supports-and-services/family-support-and-services?language=en_US"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract data
    data = []

    # Find all divs with the specified class
    for div in soup.find_all('div', class_='cg-c-lead-story__body col'):
        block_content = div.get_text(strip=True, separator=' ')
        list_items = [li.get_text(strip=True) for li in div.find_all('li')]
        
        # Combine the block content with list items
        combined_content = {
            'block_content': block_content,
            'list_items': list_items
        }
        data.append(combined_content)

    # Convert data to JSON format
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'family_support_and_services.json'

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

scrape_and_upload_to_gcs_12()