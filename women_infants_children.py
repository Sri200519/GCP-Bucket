def scrape_and_upload_to_gcs_18():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # URL of the webpage to scrape
    url = 'https://portal.ct.gov/dph/wic/wic'

    # Send a GET request to the website
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract data
    data = []

    # Define the styles to target
    target_styles = [
        'margin: 0in 0in 0pt;',
        'text-align: left;'
    ]

    # Find and extract <p> and <div> tags with the specified styles
    for style in target_styles:
        for tag in soup.find_all(['p', 'div'], style=style):
            text_content = tag.get_text(strip=True)
            data.append({
                'tag': tag.name,
                'style': style,
                'content': text_content
            })

    # Convert data to JSON format
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'women_infants_children.json'

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

scrape_and_upload_to_gcs_18()