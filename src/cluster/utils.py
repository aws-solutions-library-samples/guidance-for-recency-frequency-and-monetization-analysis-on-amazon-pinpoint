import os
os.system('pip install -U pickle5')

import pandas as pd
import numpy as np
import string
import pickle5 as pickle
import pickle
import boto3
import tempfile
import io
import random
import datetime


seed_value = 18
os.environ['PYTHONHASHSEED'] = str(seed_value)
random.seed(seed_value)
np.random.seed(seed_value)
# https://stackoverflow.com/questions/5836335/consistently-create-same-random-numpy-array/5837352#5837352
random_state = np.random.RandomState(seed=seed_value)


s3 = boto3.client('s3')


def read_from_s3(file_path):
    bucket_name = file_path.split('/')[2]
    key = '/'.join(file_path.split('/')[3:])
    response = s3.get_object(Bucket=bucket_name, Key=key)
    body = response['Body'].read()
    return body

def read_pickle_from_s3(file_path):
    data = pickle.loads(read_from_s3(file_path))
    return data

def read_csv_from_s3(file_path):
    # data = pd.read_csv(file_path, low_memory=False)
    data_in_bytes = read_from_s3(file_path=file_path)
    data = pd.read_csv(io.BytesIO(data_in_bytes), low_memory=False)
    return data

def read_file_with_encoding_from_s3(file_path, encoding='cp437'):
    # data = pd.read_csv(file_path, low_memory=False)
    data_in_bytes = read_from_s3(file_path=file_path)
    data = pd.read_csv(io.BytesIO(data_in_bytes), low_memory=False, encoding=encoding)
    return data

def store_dataframe_to_s3_as_csv(data, file_path, index=False, header=True):
    bucket_name = file_path.split('/')[2]
    key = '/'.join(file_path.split('/')[3:])
    fd, path = tempfile.mkstemp()
    try:
        data.to_csv(path, index=index, header=header)
        with open(path, "rb") as pointer:
            s3.upload_fileobj(pointer, bucket_name, key)
    finally:
        os.remove(path)

def store_object_to_s3_as_pickle(data, file_path):
    bucket_name = file_path.split('/')[2]
    key = '/'.join(file_path.split('/')[3:])
    fd, path = tempfile.mkstemp()
    try:
        with open(path, 'wb') as pointer:
            pickle.dump(data, pointer)
        with open(path, "rb") as pointer:
            s3.upload_fileobj(pointer, bucket_name, key)
    finally:
        os.remove(path)

table = str.maketrans({key: None for key in string.punctuation})
def cleaning_character_based_cat(string):
    if not pd.isnull(string):
        string = str(string)
        string_1 = string.lower().translate(table).strip()
        string_2 = ' '.join([x.strip() for x in string_1.split()]).strip()
        return string_2
    else:
        return np.nan
    
def cleaning_num(value):
    try:
        if not pd.isnull(value):
            if type(value) == float or type(value) == int:
                return float(value)
            else:
                return float(value.replace(',', ''))
        else:
            return np.nan
    except:
        return np.nan