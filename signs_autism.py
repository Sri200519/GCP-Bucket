def scrape_and_upload_to_gcs_15():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # Fetch the web page
    url = 'https://www.autismspeaks.org/signs-autism'
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the specific div by class
    target_divs = soup.find_all('div', class_='basic-block')

    # Extract content from p, h2, h3, ul, and a tags within the specific divs
    data = []
    for target_div in target_divs:
        section_data = []
        for tag in target_div.find_all(['p', 'h2', 'h3', 'ul', 'a']):
            tag_name = tag.name
            if tag_name == 'a':
                tag_content = tag.get_text(strip=True)
                href = tag.get('href', '')
                section_data.append({
                    'tag': tag_name,
                    'content': tag_content,
                    'href': href
                })
            else:
                tag_content = tag.get_text(strip=True)
                if tag_name == 'ul':
                    list_items = [li.get_text(strip=True) for li in tag.find_all('li')]
                    tag_content = '\n'.join(list_items)
                section_data.append({
                    'tag': tag_name,
                    'content': tag_content
                })
        if section_data:
            data.append(section_data)

    # Debugging: Print the length and content of the data list
    print(f"Number of sections extracted: {len(data)}")
    print("Data extracted:")
    for section in data:
        print(section)

    # Convert data to JSON format
    data_json = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'signs_autism.json'

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

scrape_and_upload_to_gcs_15()