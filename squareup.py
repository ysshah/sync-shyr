import os
import json
import pickle
import uuid

from square.client import Client

import util

ITEMS_FILE = '/tmp/items.pickle'
TAX_ID = 'L2DWED7RBTKZGG5UHXVGUPWP'

client = Client(access_token=os.environ['SQUARE_ACCESS_TOKEN'])

def sync(sheet):
  items = load_items()
  objects = []
  for sheet_wine in sheet.itertuples():
    if sheet_wine.SKU in items:
      square_wine = items[sheet_wine.SKU]
      if compare(sheet_wine, square_wine):
        objects.append(create_catalog_object(sheet_wine, square_wine))
    else:
      util.info(f'New wine: {sheet_wine.Name}')
      objects.append(create_catalog_object(sheet_wine))

  if objects:
    print('Updating Square...')
    if not util.dry_run:
      result = client.catalog.batch_upsert_catalog_objects({
        'batches': [{ 'objects': objects }],
        'idempotency_key': str(uuid.uuid4())
      })
      if result.is_error():
        raise RuntimeError(f'Error updating Square: {result.errors}')
      download_items()
    print('Done.')
  else:
    util.info('Square wines already synced.')

def create_catalog_object(sheet_wine, square_wine={}):
  return {
    'id': square_wine.get('item_id', f'#{sheet_wine.SKU}'),
    'version': square_wine.get('item_version'),
    'type': 'ITEM',
    'present_at_all_locations': True,
    'item_data': {
      'name': sheet_wine.Name,
      'description': sheet_wine.Description,
      'tax_ids': [TAX_ID],
      'variations': [{
        'id': square_wine.get('variation_id', f'#{sheet_wine.SKU}Variation'),
        'version': square_wine.get('variation_version'),
        'type': 'ITEM_VARIATION',
        'present_at_all_locations': True,
        'item_variation_data': {
          'sku': sheet_wine.SKU,
          'price_money': { 'amount': sheet_wine.Price, 'currency': 'USD' },
          'pricing_type': 'FIXED_PRICING'
        }
      }]
    }
  }

def compare(sheet_wine, square_wine):
  different = False
  for attribute in ['Name', 'Description', 'Price']:
    if (old := square_wine[attribute]) != (new := getattr(sheet_wine, attribute)):
      util.info(f'[{sheet_wine.Name}] Update {attribute}: {old} to {new}')
      different = True
  return different

def load_items():
  if os.path.exists(ITEMS_FILE):
    with open(ITEMS_FILE, 'rb') as f:
      return pickle.load(f)
  return download_items()

def download_items():
  items = get_items()
  with open(ITEMS_FILE, 'wb') as f:
    pickle.dump(items, f)
  return items

def get_items():
  # TODO: Find out why there are 493 wines and not 492
  util.info('Downloading wines from Square...')
  items = {}
  c = None
  while (r := client.catalog.list_catalog(types='ITEM', cursor=c)) and (c := r.body.get('cursor')):
    print(f'Downloaded {len(r.body["objects"])} items...')
    if r.is_error():
      raise RuntimeError(f'Error retrieving wines from Square: {r.errors}')
    for item in r.body['objects']:
      if 'price_money' in data(item):  # Exclude Shipping & Handling, which has no price
        if sku(item) in items:
          print(f'WARNING: Duplicate wine "{name(item)}"')
        items[sku(item)] = {
          'Name': name(item),
          'Description': item['item_data'].get('description', ''),
          'Price': price(item),
          'item_id': item['id'],
          'item_version': item['version'],
          'variation_id': variation(item)['id'],
          'variation_version': variation(item)['version'],
        }
  return items
  # client.catalog.search_catalog_objects({'object_types': ['ITEM','IMAGE']})

def sku(item):
  if 'sku' not in data(item):
    raise RuntimeError(
      f'Could not find SKU for Square item: "{name(item)}"\n\n{json.dumps(item, indent=2)}')
  return data(item)['sku']

def name(item): return item['item_data']['name']
def price(item): return data(item)['price_money']['amount']
def data(item): return variation(item)['item_variation_data']
def variation(item): return item['item_data']['variations'][0]
