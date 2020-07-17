import traceback
import time

import util

def main():
  if not util.lock():
    return util.get_lock()
  time.sleep(10)

  # sheet = sheets.read()
  # squareup.sync(sheet)
  # firebase.sync(util.IMAGES_DIR, drive.list_images())

  # factsheets = drive.list_factsheets()
  # firebase.sync(util.FACTSHEETS_DIR, factsheets)
  # firebase.upload_wines(sheet, factsheets)
  # util.info('Sync complete.')
  # util.info('================================')

  util.unlock()

def shyr():
  try:
    main()
  except Exception as e:
    util.unlock()
    util.error(str(e))
    print(traceback.format_exc())

if __name__ == '__main__':
  shyr()
