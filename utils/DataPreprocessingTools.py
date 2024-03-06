import pandas as pd
from scipy.stats import norm
import numpy as np

def IC(X, alpha = 1e-4):
        """
        Computes the confidence interval for a new datapoint drawn from the same random variable for which
        X has been created, to belong to it.
        The probability for the new datapoint to belong in the confidence interval is 1-alpha.
        """
        mu, sigma = X.mean(), X.std()
        q_alpha = norm.ppf(1-alpha)
        return [ mu - sigma*q_alpha, mu + sigma*q_alpha] 

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