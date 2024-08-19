def scrape_and_upload_to_gcs_4():
    import json
    from bs4 import BeautifulSoup
    import requests
    import pdfplumber
    from gcloud import storage
    from google.api_core.exceptions import GoogleAPIError

    # Step 1: Download the PDF
    url = "https://portal.ct.gov/-/media/dph/cyshcn/ct-collaborative-autism-services-resource-directory.pdf"
    response = requests.get(url)
    
    # Save to /tmp directory in Lambda
    pdf_path = "/tmp/resource_directory.pdf"
    with open(pdf_path, "wb") as file:
        file.write(response.content)

    # Step 2: Extract Data from the PDF
    def extract_text_from_pdf(pdf_path):
        text_data = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_data.extend(page.extract_text().split('\n'))
        return text_data

    pdf_text_lines = extract_text_from_pdf(pdf_path)

    # Step 3: Parse Data
    def parse_text(lines):
        parsed_data = []
        entry = {}
        for line in lines:
            if line.strip() == '':  # Assuming a blank line indicates a new entry
                if entry:
                    parsed_data.append(entry)
                    entry = {}
            else:
                if "Organization:" in line:
                    if entry:  # Save the previous entry if it exists
                        parsed_data.append(entry)
                    entry = {"organization": line.replace("Organization:", "").strip()}
                elif "Contact:" in line:
                    entry["contact_info"] = line.replace("Contact:", "").strip()
                elif "Services:" in line:
                    entry["services"] = line.replace("Services:", "").strip()
                else:
                    # Handle additional lines or append to existing entry fields
                    if "additional_info" in entry:
                        entry["additional_info"] += " " + line.strip()
                    else:
                        entry["additional_info"] = line.strip()
        if entry:
            parsed_data.append(entry)
        return parsed_data

    structured_data = parse_text(pdf_text_lines)

    # Convert structured data to JSON
    json_data = json.dumps(structured_data, ensure_ascii=False, indent=4)

    # Step 4: Google Cloud Storage (GCS) Configuration
    gcs_bucket_name = 'beacon-database'
    gcs_key = 'autism_services_resource_directory.json'

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

scrape_and_upload_to_gcs_4()