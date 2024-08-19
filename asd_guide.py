def scrape_and_upload_to_gcs1():
    from gcloud import storage
    import json
    from bs4 import BeautifulSoup
    import requests

    # URL of the page to scrape
    url = 'https://childmind.org/guide/autism-spectrum-disorder-quick-guide/'
    
    # GCS Configuration
    gcs_bucket_name = 'beacon-database'  # Replace with your GCS bucket name
    gcs_blob_name = 'asd_guide.json'  # Replace with the desired blob name

    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Fetch the web page using requests with headers
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the specific div by class
        target_div = soup.find('div', class_='w-full mt-16 md:px-3 md:row-span-2 xl:row-span-1')

        # Extract content from p, h2, h3, and ul tags within the specific div
        data = []
        if target_div:
            for tag in target_div.find_all(['p', 'h2', 'h3', 'ul']):
                tag_name = tag.name
                tag_content = tag.get_text(strip=True)
                
                # Handle lists separately
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
        data_json = json.dumps(data, ensure_ascii=False)

        # Google Cloud Storage Configuration
        storage_client = storage.Client()
        bucket = storage_client.bucket(gcs_bucket_name)
        blob = bucket.blob(gcs_blob_name)

        # Upload data to GCS
        try:
            blob.upload_from_string(data_json, content_type='application/json')
            print("Data successfully uploaded to GCS")
        except Exception as e:
            print(f"Error uploading data to GCS: {e}")

    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

scrape_and_upload_to_gcs1()