import pandas as pd
import numpy as np

def load_train(x_train_path, y_train_path):
    x_train_data = pd.read_csv(x_train_path)
    y_train_data = pd.read_csv(y_train_path)
    return x_train_data, y_train_data

def load_train_integers(x_train_path, y_train_path):
    x_train_data, y_train_data = load_train(x_train_path, y_train_path)

    # format x
    x_train_data['date'] = pd.to_datetime(x_train_data['date']) # Convert the dates to datetime objects
    reference_date = x_train_data['date'][0] # Define a reference date
    x_train_data['date'] = (x_train_data['date'] - reference_date).dt.days # Calculate the number of days since the reference date for each date
    x_train_data['station'], unique_ids = pd.factorize(x_train_data['station']) # Station names to integers

    # format y
    y_train_data.drop('index', axis=1, inplace=True)

    return x_train_data, y_train_data


def mape(actual, forecast, ignore=False):
    """
    Compute the Mean Absolute Percentage Error (MAPE)
    
    Parameters:
    actual (numpy array): Array of actual values
    forecast (numpy array): Array of forecasted values
    
    Returns:
    float: MAPE value
    """
    if ignore:
        nonzero_actual = (actual != 0)
        nonzero_forecast = (forecast != 0)
        nonzero = np.logical_and(nonzero_actual, nonzero_forecast)
        actual = actual[nonzero] # delete elements of actual for which either actual=0 or forecast=0
        forecast = forecast[nonzero] # delete elements of forecasr for which either actual=0 or forecast=0
        # hence actual and forecast are both the same size
    else:
        eps = 1
        zero_actual = (actual == 0)
        zero_forecast = (forecast == 0)
        actual[zero_actual] = actual[zero_actual] + eps
        forecast[zero_forecast] = forecast[zero_forecast] + eps
    return np.mean(np.abs(actual - forecast)/actual)

