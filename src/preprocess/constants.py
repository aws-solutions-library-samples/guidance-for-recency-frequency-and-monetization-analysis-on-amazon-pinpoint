import os

SOURCE_S3 = f's3://{os.environ["S3_BUCKET"]}'
SOURCE_DATA_FILE = os.environ['DATA_SOURCE']
PREFIX = f'runs/{os.environ["PARTITION"]}'

MISSING_DATA_FILE = f'{SOURCE_S3}/{PREFIX}/missing_values.csv'
CLEANED_DATA_FILE = f'{SOURCE_S3}/{PREFIX}/data_cleaned.pkl'
FEATURE_ENGINEERED_DATA_FILE = f'{SOURCE_S3}/{PREFIX}/data_feature_engineered.pkl'
OUTPUT_DATA_FILE = f'{SOURCE_S3}/{PREFIX}/data_clusters.csv'

CAT_COLS = ['EventName', 'CustomerID']
DATE_COLS = ['Date']
NUM_COLS = ['UnitPrice', 'Quantity']
FINAL_COLS = CAT_COLS + DATE_COLS + NUM_COLS
