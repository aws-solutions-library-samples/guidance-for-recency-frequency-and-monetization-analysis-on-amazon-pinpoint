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
        print(f'Merging Recency, Frequency and Monetary Features...', end='\t')
        rfm = self.recency_df.merge(self.frequency_df, on='CustomerID', how='left').merge(self.monetary_df, on='CustomerID', how='left')
        rfm.monetary.fillna(0, inplace=True)
        print(f'Done')
        return rfm

    ###Benchmark to give score for recency indicator
    def r_score(self, v, quantiles):
        dictionary = quantiles['recency']
        if v <= dictionary[.25]:
            return 4
        elif dictionary[.25] < v <= dictionary[.5]:
            return 3
        elif dictionary[.5] < v <= dictionary[.75]:
            return 2
        else:
            return 1


    ###Benchmark to give score for frequency indicator.   
    def f_score(self, v, quantiles): 
        dictionary = quantiles['frequency']
        if v <= dictionary[.25]:
            return 1
        elif dictionary[.25] < v <= dictionary[.5]:
            return 2
        elif dictionary[.5] < v <= dictionary[.75]:
            return 3
        else:
            return 4
        
    ###Benchmark to give score for frequency indicator.   
    def m_score(self, v, quantiles): 
        dictionary = quantiles['monetary']
        if v <= dictionary[.25]:
            return 1
        elif dictionary[.25] < v <= dictionary[.5]:
            return 2
        elif dictionary[.5] < v <= dictionary[.75]:
            return 3
        else:
            return 4

    def bucketing_rfm(self) -> None:
        print(f'Bucketing RFM values...', end='\t')
        ###Calculating quantile values
        quantiles = self.rfm[['recency', 'frequency', 'monetary']].quantile([.25, .5, .75]).to_dict()
        self.rfm['r_score'] = self.rfm.recency.apply(lambda x: self.r_score(x, quantiles))
        self.rfm['f_score'] = self.rfm.frequency.apply(lambda x: self.f_score(x, quantiles))
        self.rfm['m_score'] = self.rfm.monetary.apply(lambda x: self.m_score(x, quantiles))
        print('Done')
        