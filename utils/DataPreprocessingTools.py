import pandas as pd
from scipy.stats import norm
import numpy as np

from tqdm import tqdm

from PandasToolsFunction import make_date_filter

def IC(X, alpha = 1e-4):
        """
        Computes the confidence interval for a new datapoint drawn from the same random variable for which
        X has been created, to belong to it.
        The probability for the new datapoint to belong in the confidence interval is 1-alpha.
        """
        mu, sigma = X.mean(), X.std()
        q_alpha = norm.ppf(1-alpha)
        return [ mu - sigma*q_alpha, mu + sigma*q_alpha] 

def covid_remover(data: pd.DataFrame):
    
    covid_removed_data = data.copy()

    covid_time = make_date_filter(covid_removed_data, start_date='2020-02-01', end_date='2021-11-01')
    covid_removed_data = covid_removed_data[~covid_time]
    return covid_removed_data

def data_day_typer(data_init: pd.DataFrame):

    data = data_init.copy()

    for index, row in data.iterrows():
        if row['ferie'] == 1:
            data.at[index, 'day_type'] = 'ferie'
        elif row['vacances'] == 1: 
            data.at[index, 'day_type'] = 'vacances'
        elif row['job'] == 1:
            data.at[index, 'day_type'] = 'job'
        else:
            data.at[index, 'day_type'] = 'job'

    for day_type_col in ['job', 'ferie', 'vacances']:
        data.pop(day_type_col)

    return data


def data_anomaly_elimination(data_init: pd.DataFrame, alpha=1e-4):
    data = data_init.copy()

    elimination_counts = {}
    elimination_percentages = {}
    for station in tqdm(data['station'].unique()):
        station_count = 0

        for day_type in ['job', 'ferie', 'vacances']: # Our day types will form a partition.
            mask = (data['station'] == station) & (data[day_type] == 1)
            station_day_type_data = data[mask]

            lower_bound, upper_bound = IC(station_day_type_data['y'], alpha)

            # Keep only the data points within the confidence interval
            previous_size = len(data)
            data = data[~((mask) & ((data['y'] < lower_bound) | (data['y'] > upper_bound)))]
            
            station_count += previous_size - len(data)
        elimination_counts[station] = station_count
        elimination_percentages[station] = station_count/sum(data_init['station'] == station)

    return data, elimination_counts, elimination_percentages