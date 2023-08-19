from __future__ import print_function

import argparse
import os

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from utils import read_pickle_from_s3, store_dataframe_to_s3_as_csv, seed_value
from constants import FEATURE_ENGINEERED_DATA_FILE, OUTPUT_DATA_FILE

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # Hyperparameters are described here. In this simple example we are just including one hyperparameter.
    parser.add_argument("--nclusters", type=int, default=7)


    # Sagemaker specific arguments. Defaults are set in the environment variables.
    parser.add_argument("--output-data-dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"])
    parser.add_argument("--model-dir", type=str, default=os.environ["SM_MODEL_DIR"])

    args = parser.parse_args()
    print("OS ENVIRONS:")
    print(os.environ)

    # Here we support a single hyperparameter, 'number_of_clusters'
    n_clusters = args.nclusters

    # Train data path
    train_data_path = FEATURE_ENGINEERED_DATA_FILE
    print("TRAIN DATA PATH:")
    print(train_data_path)

    train_data = read_pickle_from_s3(train_data_path)

    train_X = train_data[['r_score', 'f_score', 'm_score']].to_numpy()

    # Now use scikit-learn's decision tree classifier to train the model.
    clusterer = KMeans(n_clusters=n_clusters, random_state=seed_value)
    cluster_labels = clusterer.fit_predict(train_X)

    output_data = train_data.copy()
    output_data['Cluster_Labels'] = cluster_labels
    _df = output_data.groupby('Cluster_Labels').agg({'r_score': [('r_score_mean', 'mean')], 'f_score': [('f_score_mean', 'mean')], 'm_score': [('m_score_mean', 'mean')],})
    _df.columns = _df.columns.droplevel()
    _df2 = _df.mean(axis=1).reset_index()
    _df2.columns = ['Cluster_Labels', 'RFM_MEAN']
    _df2['Rank'] = _df2['RFM_MEAN'].rank(method='dense')
    _df2.set_index('Cluster_Labels', inplace=True)
    mapping_dict = _df2['Rank'].to_dict()
    output_data['Cluster_Labels'] = output_data['Cluster_Labels'].apply(lambda x: mapping_dict[x])
    store_dataframe_to_s3_as_csv(output_data, OUTPUT_DATA_FILE)


    # Print the coefficients of the trained classifier, and save the coefficients
    joblib.dump(clusterer, os.path.join(args.model_dir, "model.joblib"))


def model_fn(model_dir):
    """Deserialized and return fitted model
    Note that this should have the same name as the serialized model in the main method
    """
    clusterer = joblib.load(os.path.join(model_dir, "model.joblib"))
    return clusterer
