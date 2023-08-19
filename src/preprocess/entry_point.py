from cleaning import Read_Clean_Store
from feature_engineering import Feature_Engineering
from utils import read_file_with_encoding_from_s3, store_object_to_s3_as_pickle
from constants import SOURCE_DATA_FILE, CLEANED_DATA_FILE, FEATURE_ENGINEERED_DATA_FILE

def main():
    raw_data = read_file_with_encoding_from_s3(SOURCE_DATA_FILE)
    print(f'Cleaning the Raw Data...')
    data_cleaner = Read_Clean_Store(raw_data)
    print(f'Done')
    print(f'Storing the cleaned data at {CLEANED_DATA_FILE}')
    store_object_to_s3_as_pickle(data_cleaner.data, CLEANED_DATA_FILE)
    print(f'Applying Feature Engineering...')
    fe_obj = Feature_Engineering(data_cleaner.data)
    print(f'Storing the Feature Engineered Data at {FEATURE_ENGINEERED_DATA_FILE}')
    store_object_to_s3_as_pickle(fe_obj.rfm, FEATURE_ENGINEERED_DATA_FILE)

if __name__ == '__main__':
    main()
