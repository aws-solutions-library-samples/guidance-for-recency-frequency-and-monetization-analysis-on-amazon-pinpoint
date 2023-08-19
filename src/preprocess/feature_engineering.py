from utils import *
from constants import *

class Feature_Engineering:
    def __init__(self, data) -> None:
        self.data = data
        self.recency_df = self.calculate_recency()
        self.frequency_df = self.calculate_frequency()
        self.monetary_df = self.calculate_monetary_value()
        self.rfm = self.merge_features()
        self.bucketing_rfm()


    def calculate_recency(self) -> pd.DataFrame:
        print(f'Calculating recency...', end='\t')
        df = self.data[self.data.EventName.isin(['processed', 'viewed', 'purchased'])].copy()
        reference_date = df.Date.max() + datetime.timedelta(days = 1)
        df['days_from_last_purchase'] = (reference_date - df.Date).astype('timedelta64[D]')
        recency_df = df[['CustomerID', 'days_from_last_purchase']].groupby('CustomerID').min().reset_index()
        recency_df.rename(columns={'days_from_last_purchase': 'recency'}, inplace=True)
        recency_df['recency'] = recency_df['recency'].round(decimals=3)
        print(f'Done')
        return recency_df

    def calculate_frequency(self) -> None:
        print(f'Calculating frequency...', end='\t')
        df = self.data[self.data.EventName.isin(['processed', 'viewed', 'purchased'])].copy()
        frequency_df = df[['CustomerID', 'EventName']].groupby(['CustomerID']).count().reset_index()
        frequency_df.rename(columns = {'EventName':'frequency'}, inplace = True)
        frequency_df['frequency'] = frequency_df['frequency'].round(decimals=3)
        print(f'Done')
        return frequency_df
    
    def calculate_monetary_value(self) -> None:
        print(f'Calculating monetary_value...', end='\t')
        df = self.data[self.data.EventName.isin(['purchased'])].copy()
        df['amount'] = df.UnitPrice * df.Quantity
        monetary_df = df[['CustomerID','amount']].groupby('CustomerID').sum().reset_index()
        monetary_df.rename(columns = {'amount':'monetary'}, inplace = True)
        monetary_df['monetary'] = monetary_df['monetary'].round(decimals=3)
        print(f'Done')
        return monetary_df

    def merge_features(self) -> pd.DataFrame:
#         assert (self.monetary_df.shape[0] == self.recency_df.shape[0]) & (self.recency_df.shape[0] == self.frequency_df.shape[0]), 'The number of rows are not matching post feature engineering, hence aborting.'
        print(f'Merging Recency, Frequency and Monetary Features...', end='\t')
        rfm = self.recency_df.merge(self.frequency_df, on='CustomerID', how='left').merge(self.monetary_df, on='CustomerID', how='left')
        rfm.monetary.fillna(0, inplace=True)
        print(f'Done')
        return rfm

    ###Benchmark to give score for recency indicator
    def r_score(self, v, quantiles):
        dictionary = quantiles['recency']
        if v <= dictionary[.1]:
            return 10
        elif dictionary[.1] < v <= dictionary[.2]:
            return 9
        elif dictionary[.2] < v <= dictionary[.3]:
            return 8
        elif dictionary[.3] < v <= dictionary[.4]:
            return 7
        elif dictionary[.4] < v <= dictionary[.5]:
            return 6
        elif dictionary[.5] < v <= dictionary[.6]:
            return 5
        elif dictionary[.6] < v <= dictionary[.7]:
            return 4
        elif dictionary[.7] < v <= dictionary[.8]:
            return 3
        elif dictionary[.8] < v <= dictionary[.9]:
            return 2
        else:
            return 1


    ###Benchmark to give score for frequency indicator.   
    def f_score(self, v, quantiles): 
        dictionary = quantiles['frequency']
        if v <= dictionary[.1]:
            return 1
        elif dictionary[.1] < v <= dictionary[.2]:
            return 2
        elif dictionary[.2] < v <= dictionary[.3]:
            return 3
        elif dictionary[.3] < v <= dictionary[.4]:
            return 4
        elif dictionary[.4] < v <= dictionary[.5]:
            return 5
        elif dictionary[.5] < v <= dictionary[.6]:
            return 6
        elif dictionary[.6] < v <= dictionary[.7]:
            return 7
        elif dictionary[.7] < v <= dictionary[.8]:
            return 8
        elif dictionary[.8] < v <= dictionary[.9]:
            return 9
        else:
            return 10
        
    ###Benchmark to give score for frequency indicator.   
    def m_score(self, v, quantiles): 
        dictionary = quantiles['monetary']
        if v <= dictionary[.1]:
            return 1
        elif dictionary[.1] < v <= dictionary[.2]:
            return 2
        elif dictionary[.2] < v <= dictionary[.3]:
            return 3
        elif dictionary[.3] < v <= dictionary[.4]:
            return 4
        elif dictionary[.4] < v <= dictionary[.5]:
            return 5
        elif dictionary[.5] < v <= dictionary[.6]:
            return 6
        elif dictionary[.6] < v <= dictionary[.7]:
            return 7
        elif dictionary[.7] < v <= dictionary[.8]:
            return 8
        elif dictionary[.8] < v <= dictionary[.9]:
            return 9
        else:
            return 10

    def bucketing_rfm(self) -> None:
        print(f'Bucketing RFM values...', end='\t')
        ###Calculating quantile values
        quantiles = self.rfm[['recency', 'frequency', 'monetary']].quantile([.1, .2, .3, .4, .5, .6, .7, .8, .9]).to_dict()
        self.rfm['r_score'] = self.rfm.recency.apply(lambda x: self.r_score(x, quantiles))
        self.rfm['f_score'] = self.rfm.frequency.apply(lambda x: self.f_score(x, quantiles))
        self.rfm['m_score'] = self.rfm.monetary.apply(lambda x: self.m_score(x, quantiles))
        print('Done')
        
