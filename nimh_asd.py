def scrape_and_upload_to_gcs_14():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # Fetch the web page
    url = 'https://www.nimh.nih.gov/health/topics/autism-spectrum-disorders-asd'
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the specific div by ID and class
    target_div = soup.find('div', id='main_content', class_='areanav-true sidebar-true')

    # Extract content from p, h2, h3, ul, and a tags within the specific div
    data = []
    if target_div:
        for tag in target_div.find_all(['p', 'h2', 'h3', 'ul', 'a']):
            tag_name = tag.name
            if tag_name == 'a':
                tag_content = tag.get_text(strip=True)
                href = tag.get('href', '')
                data.append({
                    'tag': tag_name,
                    'content': tag_content,
                    'href': href
                })
            else:
                tag_content = tag.get_text(strip=True)
                if tag_name == 'ul':
                    list_items = [li.get_text(strip=True) for li in tag.find_all('li')]
                    tag_content = '\n'.join(list_items)
                data.append({
                    'tag': tag_name,
                    'content': tag_content
                })
    else:
        print("Target div not found")

    # Debugging: Print the length and content of the data list
    print(f"Number of items extracted: {len(data)}")
    print("Data extracted:")
    for item in data:
        print(item)

    # Convert data to JSON format
    data_json = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'nimh_asd.json'

    # Initialize Google Cloud Storage client
    storage_client = storage.Client()

    try:
        # Upload JSON data to GCS
        bucket = storage_client.get_bucket(gcs_bucket_name)
        blob = bucket.blob(gcs_file_name)
        blob.upload_from_string(data_json, content_type='application/json')
        print("Data successfully uploaded to GCS")
    except GoogleAPIError as e:
        print(f"Failed to upload to GCS: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

scrape_and_upload_to_gcs_14()