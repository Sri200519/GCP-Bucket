def scrape_and_upload_to_gcs_19():
    import requests
    from google.cloud import storage
    import json
    # Step 1: Fetch Data
    url = 'https://www.211childcare.org/providers.json'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")
    
    # Step 2: Upload to Google Cloud Storage
    client = storage.Client()
    bucket_name = 'beacon-database'  # Your bucket name
    destination_blob_name = 'providers.json'
    
    bucket = client.get_bucket(bucket_name)
    json_data = json.dumps(data)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(json_data, content_type='application/json')
    
    print(f"Data successfully uploaded to {bucket_name}/{destination_blob_name}")