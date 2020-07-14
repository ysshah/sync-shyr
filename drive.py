from io import FileIO
from os import environ

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from auth import credentials

# https://developers.google.com/drive/api/v3/search-files#query_string_examples
QUERY = "'{}' in parents and mimeType = '{}'"
FACTSHEETS_QUERY = QUERY.format(environ['FACT_SHEETS_FOLDER_ID'], 'application/pdf')
IMAGES_QUERY = QUERY.format(environ['IMAGES_FOLDER_ID'], 'image/jpeg')

service = build('drive', 'v3', credentials=credentials)

def list_images():
  print('Retrieving image list from Drive')
  return list_files(IMAGES_QUERY)

def list_factsheets():
  print('Retrieving factsheet list from Drive')
  return list_files(FACTSHEETS_QUERY)

def list_files(query):
  # TODO: Handle more than 1000 items
  return service.files().list(q=query, fields='files(id, name, modifiedTime)',
                              pageSize=1000).execute()['files']

def download(file_id, destination):
  print(f'Downloading {file_id} to {destination}')
  downloader = MediaIoBaseDownload(FileIO(destination, mode='w'),
                                   service.files().get_media(fileId=file_id))
  while not downloader.next_chunk()[1]:
    pass
