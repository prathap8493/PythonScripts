import firebase_admin
from firebase_admin import credentials, firestore
import requests
import time
from google.api_core.exceptions import DeadlineExceeded

cred = credentials.Certificate('./config.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_location_data(ip_address):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        if response.status_code == 200:
            data = response.json()
            return data.get('country'), data.get('regionName')
    except requests.RequestException as e:
        print(f"Error fetching location data for IP {ip_address}: {e}")
    return None, None

def update_document_with_retry(doc_id, data, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            db.collection('user_responses').document(doc_id).update(data)
            print(f"Successfully updated document {doc_id}")
            return
        except DeadlineExceeded:
            print(f"Deadline exceeded when updating document {doc_id}, retrying ({retries + 1}/{max_retries})...")
            time.sleep(2 ** retries) 
            retries += 1
    print(f"Failed to update document {doc_id} after {max_retries} retries.")

def process_documents(start_after_doc=None, batch_size=10):
    query = db.collection('user_responses').order_by(u'__name__').limit(batch_size)
    if start_after_doc:
        query = query.start_after(start_after_doc)

    docs = query.stream()
    last_doc = None
    for doc in docs:
        last_doc = doc
        doc_dict = doc.to_dict()
        if 'country' not in doc_dict:
            ip_address = doc_dict.get('user_ip')
            if ip_address:
                country, region = fetch_location_data(ip_address)
                if country:
                    print(f"IP: {ip_address}, Country: {country}, Region: {region}")
                    update_document_with_retry(doc.id, {'country': country, 'region': region})
    return last_doc

# Process all documents in batches
last_doc = None
while True:
    last_doc = process_documents(start_after_doc=last_doc, batch_size=10)
    if not last_doc:
        break
