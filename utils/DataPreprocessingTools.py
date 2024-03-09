import pandas as pd
from scipy.stats import norm
import numpy as np

from tqdm import tqdm

from PandasToolsFunction import make_date_filter
from PandasToolsFunction import date_filter

# Labelling data

def covid_remover(data: pd.DataFrame):
    
    covid_removed_data = data.copy()

    start_covid = pd.to_datetime('2019-12-01') # includes the scnf strike of december
    end_covid = pd.to_datetime('2021-11-01')
    covid_time = make_date_filter(covid_removed_data, start_date=start_covid, end_date=end_covid)
    covid_removed_data = covid_removed_data[~covid_time]
    return covid_removed_data

def covid_replace(data: pd.DataFrame):
    covid_replaced_data = data.copy()
    
    start_date = pd.to_datetime('2019-12-01')
    end_date = pd.to_datetime('2021-11-01')

    covid_time_plus_strike = make_date_filter(data, start_date, end_date)
    covid_time_plus_strike = data[covid_time_plus_strike]

    length = (end_date - start_date).days  # Calculate the number of days in the time period

    replacing_time_period = make_date_filter(data, start_date=end_date, end_date=start_date + pd.DateOffset(days=length))
    replacing_time_period = data[replacing_time_period]

    covid_replaced_data.loc[covid_time_plus_strike.index] = replacing_time_period.values

    return covid_replaced_data

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


def add_day_type_column(df_init: pd.DataFrame, holy_dict: dict, pub_holy_dict: dict):
    """ 
    Here are the labels
    day_type_map = {0: 'job', 1: 'mid_holy', 2: 'start_holy', 3: 'end_holy',
                 4: 'Noel_eve', 5: 'Noel', 6: 'New_year_eve', 7: 'New_year',
                 8: 'other ferie'}

    Other day types : Mardi gras ? 
    """
    df = df_init.copy()

    df['day_type'] = 0  # Default value = JOB

    for holiday, period in holy_dict.items():
        start_date, end_date = period
        holiday_filter = make_date_filter(df, start_date, end_date)
        df.loc[holiday_filter, 'day_type'] = 1
        df.loc[holiday_filter & (df['date'] == start_date), 'day_type'] = 2  # First day
        df.loc[holiday_filter & (df['date'] == end_date), 'day_type'] = 3    # Last day
    
    # Static public holydays
    for year in range(2015, 2024):
        df.loc[df['date'] == str(year) + '-12-24', 'day_type'] = 4 # Noel_eve 
        df.loc[df['date'] == str(year) + '-12-25', 'day_type'] = 5 # Noel
        df.loc[df['date'] == str(year) + '-12-31', 'day_type'] = 6 # New_year_eve
        df.loc[df['date'] == str(year) + '-01-01', 'day_type'] = 7 # New_year
        df.loc[df['date'] == str(year) + '-05-01', 'day_type'] = 8 # Labour Day
        df.loc[df['date'] == str(year) + '-05-08', 'day_type'] = 9 # 8 mai 1945
        df.loc[df['date'] == str(year) + '-07-14', 'day_type'] = 10 # 14 Juillet
        df.loc[df['date'] == str(year) + '-08-15', 'day_type'] = 11 # Assomption
        df.loc[df['date'] == str(year) + '-11-01', 'day_type'] = 12 # Toussaint
        df.loc[df['date'] == str(year) + '-11-11', 'day_type'] = 13 # 11 Novembre

    Public_holyday_map = {'Paques': 14, 'Ascension': 15, 'Pentecote': 16}

    # Dynamic public holydays
    for public_holyday, day in pub_holy_dict.items(): # Paques, Ascension, Pencôte
        df.loc[df['date'] == day, 'day_type'] = Public_holyday_map[public_holyday[:-5]] # -5 to elimiate the date. public_holyday looks like 'Ascension_2022'.

    return df


def add_month_type_column(df_init: pd.DataFrame, date_col:str = 'date'):
    
    df = df_init.copy()

    # Add a column 'month' that has 0 for january and 11 for december 
    df['month'] = (df[date_col].dt.month)# - 1) % 12

    return df


def replicate_one_year(data: pd.DataFrame, year_to_replicate='2022'):
    """ 
    Replicate year (2022 by default) to 2020-2021.
    Be careful to do that after the labelling part of days, so that the replication also replicates labels.

    """
    # Filter data for the specified year
    data_to_replicate = date_filter(data, start_date=f"{year_to_replicate}-01-01", end_date=f'{year_to_replicate}-12-31')
    # Update the 'date' column to the new year (2023)
    data_to_replicate['date'] = pd.to_datetime(data_to_replicate['date']) - pd.DateOffset(years=2)

    # Concatenate the original data with the duplicated data
    duplicated_data = pd.concat([data, data_to_replicate], ignore_index=True)

    return duplicated_data


# Data anomaly detection

def IC(X, alpha = 1e-4):
        """
        Computes the confidence interval for a new datapoint drawn from the same random variable for which
        X has been created, to belong to it.
        The probability for the new datapoint to belong in the confidence interval is 1-alpha.
        """
        mu, sigma = X.mean(), X.std()
        q_alpha = norm.ppf(1-alpha)
        return [ mu - sigma*q_alpha, mu + sigma*q_alpha] 

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