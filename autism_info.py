def scrape_and_upload_to_gcs_3():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # Step 1: Fetch the web page
    url = 'https://autism.org/what-is-autism/'
    response = requests.get(url)
    html_content = response.text

    # Step 2: Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all div elements with the specified classes
    data = []
    divs1 = soup.find_all('div', class_='fusion-text fusion-text-1')
    divs2 = soup.find_all('div', class_='fusion-text fusion-text-2')

    # Extract content from the first class
    for div in divs1:
        div_content = div.get_text(strip=True)
        data.append({
            'class': 'fusion-text-1',
            'content': div_content
        })

    # Extract content from the second class
    for div in divs2:
        div_content = div.get_text(strip=True)
        data.append({
            'class': 'fusion-text-2',
            'content': div_content
        })

    # Convert data to JSON format
    data_json = json.dumps(data, ensure_ascii=False)

    # Step 3: Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_key = 'autism_info.json'

    # Initialize Google Cloud Storage client
    storage_client = storage.Client()

    try:
        # Upload JSON data to GCS
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(gcs_key)
        blob.upload_from_string(data_json, content_type='application/json')
        print("Data successfully uploaded to GCS")
    except GoogleAPIError as e:
        print(f"Failed to upload to GCS: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scrape_and_upload_to_gcs_3()