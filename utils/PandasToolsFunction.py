import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import locale
import calendar

import random

from typing import Union 

day_of_week_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday',
                        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday' }

#initial_categorisation = {}

def make_date_filter(df: pd.DataFrame, start_date: str, end_date: str = None, column: str = "date" ) -> filter : 
    """
    Create a date filter.
    
    Parameters:
    - df (DataFrame): Input DataFrame.
    - start_date (str): Start date in the format 'YYYY-MM-DD'.
    - end_date (str): End date in the format 'YYYY-MM-DD'.
    - column (str): Name of the column containing dates (default: 'date').

    Returns:
    - filter: Filter condition.
    To use this filter on your DataFrame df : 
    filtered_df = df[filter]
    """
    if end_date is not None and start_date is not None :
        filter = (df[column] >= start_date) & (df[column] <= end_date)
    elif end_date is None :
        filter = df[column] >= start_date
    else : 
        filter = df[column] <= end_date
    return filter

def year_filter(df: pd.DataFrame, years=[]):
    df_copy = df.copy()
    filter = df_copy['date'].dt.year.isin(years)
    return df_copy[filter]

def date_filter(df: pd.DataFrame, start_date: str, end_date: str = None, column: str = "date" ) -> pd.DataFrame : 
    df_copy = df.copy()
    filter = make_date_filter(df_copy, start_date, end_date, column)
    return df_copy[filter]
def make_station_filter(df: pd.DataFrame, stations: Union[list[str], int], column: str = "station", seed = None ) -> filter : 
    """
    Create a station filter.
    
    Parameters:
    - df (DataFrame): Input DataFrame.
    - stations (list[str] or int) : if int it will plot n random stations, where n equals your input int. Example ['1J7', 'O2O'] or 5.
    - column (str): Name of the column containing dates (default: 'date').

    Returns:
    - filter: Filter condition.
    To use this filter on your DataFrame df : 
    filtered_df = df[filter]
    - stations: stations (might be useful if randomly generated)
    """
    
    if type(stations) == int :
        if seed is not None : 
            random.seed(seed)
        stations = random.sample(df[column].tolist(), stations)
    
    match_pattern = '|'.join(stations)
    filter = df[column].str.contains(match_pattern)
    
    return filter, stations


def make_day_filter(  df: pd.DataFrame, day_to_match: list[str] = [], day_to_ban: list[str] = [],
                    
                        column: str = "LPTD", match_separator: str = '|', ban_separator: str = '|', case: bool = False) -> filter : 
    """
    Create a day filter.
    
    Parameters:
    - df (DataFrame): Input DataFrame.
    - words_to_match (list[str]) : List of words
    - column (str): Name of the column containing the words you want to filter (default: 'LPTD').
    - match_separator (str) : If you want the article having all the words ('&') or at least one of them ('|').
                        Default is '|'. 
    - ban_separator (str) : Same but for discarding words.
    - case (bool) : If you want the case to be respected (default : False).

    Returns:
    - filter: Filter condition.
    To use this filter on your DataFrame df : 
    filtered_df = df[filter]
    """
    filtered_df = df.copy()
    match_filter_df = pd.Series(True, index=filtered_df.index)
    ban_filter_df = pd.Series(True, index=filtered_df.index)

    """if day_to_match :
        for day in day_to_match :
            match_filter_df = filtered_df[column].str.contains(match_pattern, case=case)
    if words_to_ban :
        ban_pattern = ban_separator.join(words_to_ban)
        ban_filter_df = ~filtered_df[column].str.contains(ban_pattern, case=case)"""

    return match_filter_df & ban_filter_df

def sort_by_day_of_week(df: pd.DataFrame, day_name_col = 'day_name', date_col = 'date'):
    custom_day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Convert the 'day_name' column to a categorical type with the custom sorting order
    df[day_name_col] = pd.Categorical(df[day_name_col], categories=custom_day_order, ordered=True)

    # Sort the DataFrame by 'day_name' and then by 'date'
    df = df.sort_values(by=[day_name_col, date_col])

    # Reset the index if needed
    df = df.reset_index(drop=True)

    return df

def display_by_station(df: pd.DataFrame, stations: Union[list[str]], 
                    start_date: str = None, end_date: str = None,
                    date_column : str = 'date', day_name_col = 'day_name',
                    station_column = 'station', crowd_column: str = 'y',
                    seed = None, count_per_day_type = None, # change to ['job', 'ferie', 'vacances'],
                    plot: str = True, display_mode = 'per_day_of_week'
                    ) -> pd.DataFrame :    
   
    """
    Plot the evolution of the crowd. Stations and period of time can be specified.

    Parameters:
    - df (DataFrame): Input DataFrame.
    - stations (list[str] or int) : if int it will plot n random stations, where n equals your input int. Example ['1J7', 'O2O'] or 5.
    - start_date/end_date (str): Start/end date in the format 'YYYY-MM-DD'.
    - time_unity (list[str]): Don't change it for the moment please.
    - plot (bool) : If True, it plots the figure. (default : True)
    - display_mode (str) : 
        - 'per_day_of_week' : will plot boxplot of distribution along each day of the week.
        - 'dates' : will plot along dates, 
           if the time period is under than one month, it'll plot the day names of week.

    Returns:
    - The DataFrame filtered by the time period and stations.
    - The considered stations.
    """
    #We copy to avoid changing the original DataFrame.
    new_df = df.copy()


    if start_date is not None or end_date is not None :
        period_filter = make_date_filter(new_df, start_date, end_date, date_column)
        new_df = new_df[period_filter]
    
    if start_date is None : start_date = new_df['date'].iloc[0]
    if end_date is None : end_date = new_df['date'].iloc[-1]

    station_filter, stations = make_station_filter(df, stations, station_column, seed)
    
    final_df = new_df[station_filter]
    

    if plot :
        if display_mode == 'per_day_of_week' :
            x_data = 'day_name'
            final_df = sort_by_day_of_week(final_df)
        elif display_mode == 'dates':
            if len(pd.date_range(start_date, end_date)) <= 32 :
                final_df['dated_day_name'] = final_df[day_name_col].str.slice(0, 2) + '-' + final_df[date_column].dt.day.astype(str)
                x_data = 'dated_day_name'
            else :
                x_data = date_column

        plt.figure(figsize=(12, 6))
        sns.lineplot(x=x_data, y=crowd_column, hue=station_column, data=final_df)

        within = ''
        joined_words = ', '.join(stations[:10])
        containing_str = f'that have visited the following station(s) : "{joined_words}"'
        if len(stations) > 10 :
            containing_str += '...'
        if start_date and end_date:
            within = f'within the time period {start_date} - {end_date}, '

        plt.title(f'Number of people {containing_str},\n{within}daily')
        plt.xlabel('Years')
        plt.ylabel('Number of people')
        plt.grid(True)
        plt.tight_layout()

        plt.show()
    
    if count_per_day_type is not None :
        total=0
        print(f"Count per day type for the following stations {joined_words}")
        print(f"Time period : {start_date} - {end_date}")
        for col in count_per_day_type :
            value =  final_df[col].value_counts()[1]
            total+=value
            print(f"{col} : {value}")

        print(f"{total = }")

    return final_df, stations