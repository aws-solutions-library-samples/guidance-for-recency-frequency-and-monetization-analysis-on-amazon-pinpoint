from utils import *
from constants import *

class Read_Clean_Store:
    def __init__(self, data) -> None:
        self.data = data
        self.clean_cat()
        self.clean_date()
        self.clean_num()
        self.remove_na()
        self.data = self.data[FINAL_COLS]
    
    def clean_cat(self) -> None:
        for c in CAT_COLS:
            print(f'Working with {c}', end='\t')
            self.data[c] = self.data[c].apply(lambda x: cleaning_character_based_cat(x))
            print('Done')

    def clean_date(self) -> None:
        for c in DATE_COLS:
            print(f'Working with {c}', end='\t')
            self.data[c] = pd.to_datetime(self.data[c], errors='coerce')
            print('Done')

    def clean_num(self) -> None:
        for c in NUM_COLS:
            print(f'Working with {c}', end='\t')
            self.data[c] = self.data[c].apply(lambda x: cleaning_num(x))
            print('Done')

    def remove_na(self) -> None:
        print(f'Filtering the rows with NaN')
        missing_data = self.data[self.data.isnull().any(axis=1)]
        print(f'Storing the data with missing values for seperate analysis at {MISSING_DATA_FILE}')
        store_dataframe_to_s3_as_csv(missing_data, MISSING_DATA_FILE)
        print(f'Removing the rows with NaN')
        self.data = self.data[~self.data.isnull().any(axis=1)]
