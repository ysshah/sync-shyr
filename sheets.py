from os import environ

from googleapiclient.discovery import build
import pandas as pd

from auth import credentials

COLUMNS = [
    'Name', 'Count', 'Price', 'SKU', 'Vintage', 'Winery', 'Country', 'Region', 'Appellation',
    'Varietal', 'Type', 'Description', 'JH', 'JS', 'RP', 'ST', 'AG', 'D', 'WA', 'WE', 'WS', 'W&S',
    'WW', 'No-Adv'
]

service = build('sheets', 'v4', credentials=credentials)

def read():
  print('Reading spreadsheet')
  result = service.spreadsheets().values().get(spreadsheetId=environ['SPREADSHEET_ID'],
                                               range='Sheet1').execute()
  df = get_columns(pd.DataFrame(result['values'][1:], columns=result['values'][0]))
  df.set_index(df.index + 2, inplace=True)  # Set index to match row numbers
  df['Name'] = df['Name'].str.strip()  # Strip whitespace around name
  check_duplicates(df)
  # Strip dollar sign, remove decimal point, and convert to integer
  df['Price'] = df['Price'].apply(lambda p: int(p[1:].replace('.', '')))
  df['Description'].fillna('', inplace=True)  # Replace None descriptions with empty string
  return df

def get_columns(df):
  if missing_columns := set(COLUMNS) - set(df):
    raise RuntimeError(f'Sheet missing columns: {missing_columns}')
  return df[COLUMNS]

def check_duplicates(df):
  for c in ['Name', 'SKU']:
    column = df[c]
    for index, value in column[column.duplicated()].iteritems():
      rows = column[column == value].index.tolist()
      raise RuntimeError(f'Duplicate {c} detected: "{value}" (present in rows {rows})')
