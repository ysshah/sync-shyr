import traceback

import drive, sheets, squareup, util

def shyr():
  try:
    util.info('Starting sync...')
    sheet = sheets.read()
    squareup.sync(sheet)
    firebase.sync(util.IMAGES_DIR, drive.list_images())

    factsheets = drive.list_factsheets()
    firebase.sync(util.FACTSHEETS_DIR, factsheets)
    firebase.upload_wines(sheet, factsheets)
    util.info('Sync complete.')
    util.info('================================')
  except Exception as e:
    util.error(str(e))
    print(traceback.format_exc())

if __name__ == '__main__':
  shyr()
