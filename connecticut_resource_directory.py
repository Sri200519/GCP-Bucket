def scrape_and_upload_to_gcs_10():
    import json
    from bs4 import BeautifulSoup
    import requests
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # Fetch the webpage content
    url = 'https://portal.ct.gov/oca/miscellaneous/miscellaneous/resources/resource-list'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize data list
    data = []

    # Function to parse items and descriptions from the siblings
    def parse_items_and_descriptions(start_ul):
        items = []
        descriptions = []
        ul = start_ul

        while ul:
            for li in ul.find_all('li'):
                link = li.find('a')
                link_text = link.get_text(strip=True) if link else ''
                link_href = link['href'] if link else ''
                items.append({
                    'text': link_text,
                    'href': link_href
                })
            
            # Find the next description <p> tag
            next_p = ul.find_next_sibling('p', style='text-align: justify;')
            if next_p:
                descriptions.append(next_p.get_text(strip=True))
            
            # Move to the next <ul> if it exists
            ul = next_p.find_next_sibling('ul', style='list-style-type: disc;') if next_p else None

        return items, descriptions

    # Extract data
    heading = None
    for tag in soup.find_all(['p', 'ul']):
        if tag.name == 'p' and 'margin-bottom: 0in;' in tag.get('style', ''):
            if heading:
                # Save previous heading's data before starting a new one
                data.append({
                    'title': heading['title'],
                    'items': heading['items'],
                    'descriptions': heading['descriptions']
                })

            # Start a new heading
            heading = {
                'title': tag.get_text(strip=True),
                'items': [],
                'descriptions': []
            }

            # Parse items and descriptions starting from the next sibling <ul>
            next_ul = tag.find_next_sibling('ul', style='list-style-type: disc;')
            if next_ul:
                heading['items'], heading['descriptions'] = parse_items_and_descriptions(next_ul)
        
    # Append the last heading
    if heading:
        data.append({
            'title': heading['title'],
            'items': heading['items'],
            'descriptions': heading['descriptions']
        })

    # Convert data to JSON format
    json_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_file_name = 'connecticut_resource_directory.json'

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

scrape_and_upload_to_gcs_10()