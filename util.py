from os import environ

import pusher
from google.cloud import storage
from google.api_core.exceptions import PreconditionFailed
from google.cloud.exceptions import NotFound

BLOB = storage.Client().get_bucket(environ['BUCKET']).blob('lock')
IMAGES_DIR = 'wine-images/'
FACTSHEETS_DIR = 'factsheets/'

dry_run = False
PUSHER = pusher.Pusher(
    app_id=environ['PUSHER_APP_ID'],
    key=environ['PUSHER_KEY'],
    secret=environ['PUSHER_SECRET'],
    cluster=environ['PUSHER_CLUSTER'],
    ssl=True,
)

def info(message):
  return out('INFO', message)

def warning(message):
  return out('WARNING', message)

def error(message):
  return out('ERROR', message)

def out(event, message):
  print(f'{event}: {message}')
  PUSHER.trigger('my-channel', event, {'message': message})

def lock():
  print('Attempting to lock')
  try:
    BLOB.upload_from_string('start', if_generation_match=0)
  except PreconditionFailed:
    print('Another function has the lock')
    return False
  print('Locked')
  return True

def get_lock():
  print('Getting the lock value')
  try:
    return BLOB.download_as_string()
  except NotFound:
    print('Could not get the lock value')
    return ''

def unlock():
  print('Releasing the lock')
  BLOB.delete()
