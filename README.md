# Challenge Data ENS, SNCF-Transilien 2024 :train:

# Preprocessing Data
See DataPreprocessing.ipynb and its correspondig utils file : DataPreprocessingTools.py

This is the code that creates the data in 'data/preprocessed_data'.

* **Adds the following features** :
    * day_numeric : day number of week (0 to 6)
    * week :        week number of the year (1 to 52)
    * months :      month number of the year (1 to 12)
    * days :        day number of the month (1 to 31)
    * day_type :    See day_type_map

* **Removes covid time** (including SNCF strike of December 2019) 2019-12-01 to 2021-11-01 :

* **Replicates year 2022** so that it gives more importance to it. 
We made the hypothesis that customer's habits are probably more related to last year than before covid, as remote working has became more usual.

See the three figures in data/figures/data_recrafting to view how this data changements modify the data.

day_type_map = {0: 'job', 1: 'mid_holy', 2: 'start_holy', 3: 'end_holy',
                 4: 'Noel_eve', 5: 'Noel', 6: 'New_year_eve', 7: 'New_year',
                 8: 'Labour Day', 9: 'May 8 1945', 10: 'July 14', 11: 'Assomption', 
                 12: 'Toussaint', 13: 'November 11', 14: 'Easter', 15: 'Ascension' , 16: 'Pentecost'}

                 
# Data Analysis 
See DataAnalysis.ipynb and its corresponding utils file AnalysisTools.py

Allows to display data, compute relative std per feature.

# Data Anomaly Detection

On the plots of station-wise MAPE on our Regressor Models (cf RegressionModels.ipynb), see figure in models/RandomForest/Hard_Stations/est_300_md20_Classic_features.png, we can see and report the stations that had bad test scores, see report in models/RandomForest/Hard_Stations/Classic_model_300.txt

Then we can plot those stations that seem hard to learn for the model (see figs in figures/anomaly_elimination/algo1 Before data)

So now we can see clearly what the problems are, we identified two types of anomalies.
* Type 1 : some quite long time periods record 0 validation. That seem clearly unsual and is probably dued to renovations.
* Type 2 : Another problem is that some station shows many isolated days with 0 validation whereas the average is around thousands of people. This kind of data does not seem easy to explain, but we still think that it is not usual data and so we shall remove it as well.

The next step was to implement an algo that removes such anomalies of the dataset. 
The algo is available in DataPreprocessingTools.py as the function 'data_anomaly_elimination'.

We used a confidence interval based method, applied for each day of week and then for each month. More precisely, the algorithm looks one station by one, computes the average number of visit on Mondays (for one station only), the corresponding standard deviation and computes a confidence interval of level alpha as the number of visit followed a normal law and removes from data the points that are outside this interval. Then it repeats for Tuesdays, ... until Sundays, and then it does the same for each of the twelve month of the year. And finally repeats for the next station.

We can see the results in figures/anomaly_elimination/algo1 After data.

Unfortunately, the final scores we obtained did not seem to really improve if not worsen.
So we thought that the anomalies of Type 2 were might not such unusual and should be taken into account, so we soften the anomaly elimination algorithm so that it removes Type 1 anomalies and keeps Type 2 anoalies. We managed doing so by computing confidence interval only by day of week and not anymore by month, also by changing the parameter alpha, moving from 5e-2 to 8e-3.

See figures in figures/anomaly_elimination/algo2, Before/After data, to see results.

# Models

## AverageModel

Feed a categorization to the model, i.e. features, for which it will average along each of them. This is a station-wise model in the sense that there is one model per station.

The model is essentially a dictionnary with format "{station}_{day_type} : average".

## RegressorModels

Select the regressor you want with regressor_type: 'RandomForest' or 'LinearRegression' or 'DecisionTreeClassifier'.

The one that reached the best score is RandomForest --> 170 on public test set.

## AutoRegressiveModel

Still a station-wise approach, testing two different algorithms : 

* ARIMA : Autoregressive integrated moving average, that takes essentially two elements : dates and one value column (here the number of validation per day).
* SARIMAX : Seasonal Autoregressive Integrated Moving-Average with Exogenous Regressors, that can take exogenous features, here we tried with the day type feature for instance.

As we were running out of time and as those methods were not very familiar to us, we haven't really delved into them. We only computed the projection on three stations and it was really bad results and quite cost effective in term of computation (+ 1min per station).
See fig in models/ARIMA/SARIMAX_Test.png, the prediction is not labeled but is at the end and clearly distinguishable.
