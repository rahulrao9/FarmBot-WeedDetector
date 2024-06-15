from __future__ import print_function
import os
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import json

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "drive_credentials.json"
PARENT_FOLDER_ID = "166bz8k9oRIuqhiGIz8a3HA48qlMRW8Jf"

# Configure logging
logging.basicConfig(filename='drive.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        creds = authenticate()
        service = build('drive', 'v3', credentials=creds)

        items_to_upload = ['app.log', 'downloaded_images', 'farmbot_run.log']

        for item in items_to_upload:
            upload_or_update(service, item, PARENT_FOLDER_ID)

    except Exception as e:
        logging.error(f"An error occurred in main: {e}", exc_info=True)

def authenticate():
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        service_account_info = json.load(f)
    creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return creds

def upload_or_update(service, item, parent_folder_id):
    try:
        if os.path.isfile(item):
            upload_file(service, item, parent_folder_id)
        elif os.path.isdir(item):
            upload_folder(service, item, parent_folder_id)
        else:
            logging.warning(f"Item not found: {item}")
    except Exception as e:
        logging.error(f"An error occurred while processing {item}: {e}", exc_info=True)
        

def upload_file(service, filepath, parent_folder_id):
    filename = os.path.basename(filepath)
    print(f'Uploading file: {filename} to folder: {parent_folder_id}')
    
    results = service.files().list(
        q=f"name='{filename}' and '{parent_folder_id}' in parents and trashed=false",
        spaces='drive',
        fields='files(id, name)').execute()
    items = results.get('files', [])

    media = MediaFileUpload(filepath, resumable=True)

    try:
        if items:
            file_id = items[0]['id']
            file = service.files().update(fileId=file_id, media_body=media).execute()
            print(f'Updated file: {filename}')
        else:
            file_metadata = {'name': filename, 'parents': [parent_folder_id]}
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f'Uploaded file: {filename}')
    except Exception as e:
        print(f"Error uploading {filename}: {e}")
        logging.error(f"Error uploading {filename}: {e}", exc_info=True)


def upload_folder(service, folder_path, parent_folder_id):
    folder_name = os.path.basename(folder_path)
    
    # Check if folder already exists
    results = service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_folder_id}' in parents and trashed=false",
        spaces='drive',
        fields='files(id, name)').execute()
    items = results.get('files', [])

    if items:
        folder_id = items[0]['id']
        print(f'Folder already exists: {folder_name} (ID: {folder_id})')
    else:
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f'Created folder: {folder_name} (ID: {folder_id})')

    # Upload all files in the folder
    print(f'Attempting to upload files from: {folder_path}')
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            print(f'Attempting to upload file: {item}')
            upload_file(service, item_path, folder_id)
        else:
            print(f'Unknown item type: {item}')

if __name__ == '__main__':
    main()