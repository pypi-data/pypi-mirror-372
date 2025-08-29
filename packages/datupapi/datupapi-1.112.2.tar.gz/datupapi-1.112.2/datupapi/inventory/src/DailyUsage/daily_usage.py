import pandas as pd
import os
import sys
import numpy as np
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from datupapi.configure.config import Config
from datupapi.extract.io import IO
from datupapi.utils.utils import Utils
from pandas.tseries.offsets import MonthEnd
from functools import reduce

class DailyUsage():
    """
    Class for processing inventory and forecasts.
    This class provides methods for get average daily usage and, generating forecasts, and defining periods.

    Args:
        df_prep (pandas.DataFrame): Qprep Dataframe prepared for Forecast.
        df_fcst (pandas.DataFrame): Qmfcst Dataframe prepared for Forecast.
        df_inv_suggested (pandas.DataFrame): Dataframe of Iventory Opt whit Suggested Forecasts
        forecast_rule (Boolean): Boolean to allow the use of the Suggested Forecast to calculate the average 
        location (Boolean): to enable the use of Location
        monhts_ (int): Target Number months
        weeks_ (int): Target Number weeks
        frequency_ (string): to switch the calculation between week or month.
        column_forecast (string): name of the column where the desired forecast is located 
    """

    def __init__(self, df_prep, df_fcst, forecast_rule, location, frequency_, df_leadtimes=None, column_forecast="SuggestedForecast", months_=4, weeks_=16, coverage=False) -> None:
        self.df_prep = df_prep
        self.df_fcst = df_fcst
        self.df_leadtimes = df_leadtimes
        self.forecast_rule = forecast_rule
        self.location = location
        self.months_ = months_
        self.weeks_ = weeks_
        self.frequency_ = frequency_
        self.column_forecast = column_forecast
        self.coverage = coverage

    def get_columns(self):
        """Return two lists: columns_filter and columns_group"""

        columns_data = ["Date", "Item","Location", "Target"]
        if self.location is True:
            columns_filter = columns_data            
            columns_filter.append(self.column_forecast)
            columns_group = ["Item","Location"]

        else:
            columns_filter = columns_data
            columns_filter.remove("Location")
            columns_filter.append(self.column_forecast)
            columns_group = ["Item"]

        return columns_group, columns_filter
    

    def get_period(self):        
        period_dict = {"M":(30*self.months_), "W":(7*self.weeks_)}
        period = period_dict.get(self.frequency_,0)

        return period


    def calculate_daily(self,df:pd.DataFrame,df_suggested:pd.DataFrame,type_daily:str):
        """Calculate the daily usage depending on type of daily usage. Return a DataFrame"""
        period = self.get_period()
        columns_group,_ = self.get_columns()
        coverage = self.coverage
        
        if coverage:
            df_leatimes = self.df_leadtimes
            columns_lead = columns_group + ["Coverage"]
            df_leatimes = df_leatimes[columns_lead].copy()
            df = pd.merge(df,df_leatimes, on=columns_group,how="left")

            columns_sugg = columns_group + ["SuggestedForecast"]
            df_suggested = df_suggested[columns_sugg].copy()
            df_suggested = df_suggested.rename(columns={"SuggestedForecast":"SuggestedForecastCov"})
            df = pd.merge(df, df_suggested, on=columns_group,how="left")

        if type_daily == "AvgDailyUsage" and not coverage:
            df_avg = df.groupby(columns_group, as_index=False).agg({type_daily:"sum"}).reset_index(drop=True)
            df_avg[type_daily] = df_avg[type_daily]/period

        elif type_daily == "MaxDailyUsage" and not coverage:
            df_avg = df.groupby(columns_group, as_index=False).agg({type_daily:"std"}).reset_index(drop=True)
            df_avg[type_daily] = (2*df_avg[type_daily])/period


        elif type_daily == "AvgDailyUsage" and coverage:
            df_avg = df.groupby(columns_group, as_index=False).agg({"SuggestedForecastCov":"max","Coverage":"max"}).reset_index(drop=True)
            df_avg[type_daily] = df_avg["SuggestedForecastCov"]/df_avg["Coverage"]

        elif type_daily == "MaxDailyUsage" and coverage:
            df_avg = df.groupby(columns_group, as_index=False).agg({type_daily:lambda x: np.std(x) if len(x) > 1 else 0.1*x,"Coverage":"max"}).reset_index(drop=True)
            df_avg[type_daily] = (2*df_avg[type_daily])/df_avg["Coverage"]

        elif type_daily == "AvgDailyUsageSeasonality" and not coverage:
            df_avg = df.groupby(columns_group, as_index=False).agg({type_daily:"mean"}).reset_index(drop=True)
        
        elif type_daily == "MaxDailyUsageSeasonality" and not coverage:
            df_avg = df.groupby(columns_group, as_index=False).agg({type_daily:"max"}).reset_index(drop=True)


        return df_avg        


    def processing(self, df_avg, df_inv_suggested, type_daily:str):
        """Return Dataframe (df_daily_usage) cleaned"""

        columns_group, columns_filter = self.get_columns()
        df_avg = df_avg[columns_filter].copy()

        if self.forecast_rule is True:
          df_avg[type_daily] = df_avg.apply(lambda x: x[self.column_forecast] if (x["Target"]==0) else x["Target"], axis=1)

        else:
          df_avg.loc[:,type_daily] = df_avg.loc[:,"Target"].copy()
        
        df_avg = self.calculate_daily(df_avg, df_inv_suggested, type_daily)
        df_avg.loc[:,columns_group] = df_avg.loc[:,columns_group].astype(str)
        df_inv_suggested.loc[:,columns_group] = df_inv_suggested.loc[:,columns_group].astype(str)
        columns_merge = columns_group + [type_daily]
        df_daily_usage = pd.merge(df_inv_suggested, df_avg[columns_merge],on=columns_group, how="left") 

        return df_daily_usage
    

    def daily_usage(self, df_inv_suggested, type_daily:str): 
        """
        Returns a data frame that incorporates the Daily Usage column into the inventory data frame.
        
        Args:
        df_inv_suggested (pandas.DataFrame): Result of Suggested forecast together Inventory for avg_daily, 
        while for max_daily to use df_avg_daily.
        type_daily (str): AvgDailyUsage or MaxDailyUsage.
        """
        
        coverage = self.coverage
        columns_group, _ = self.get_columns()

        if coverage:
            df_leatimes = self.df_leadtimes
            columns_lead = columns_group + ["Coverage"]
            df_leatimes = df_leatimes[columns_lead].copy()


        try:
            if type_daily == "AvgDailyUsageSeasonality" or type_daily=="MaxDailyUsageSeasonality":

                date_max = self.df_prep['timestamp'].max() - relativedelta(months=10) + MonthEnd(0)
                date_min = date_max - relativedelta(months=1) + MonthEnd(0)

                df_avg = self.df_fcst[(self.df_fcst["Date"] >= date_min) & (self.df_fcst["Date"] <= date_max)]

                df_daily = self.processing(df_avg, df_inv_suggested, type_daily)

            elif self.forecast_rule and not coverage:                  
                    if self.frequency_ == 'M':                      
                        df_avg = self.df_fcst[(self.df_fcst['Date'] > self.df_prep['timestamp'].max()) &
                                            (self.df_fcst['Date'] < (self.df_prep['timestamp'].max() + relativedelta(months=self.months_ + 1) + MonthEnd(0)))]
                        
                        df_daily = self.processing(df_avg, df_inv_suggested, type_daily)
                    
                    elif self.frequency_ == 'W':                      
                        df_avg = self.df_fcst[(self.df_fcst['Date'] > self.df_prep['timestamp'].max()) &
                                            (self.df_fcst['Date'] < (self.df_prep['timestamp'].max() + relativedelta(weeks=self.weeks_ + 1)))] #cambia weeks o mes
                        
                        df_daily = self.processing(df_avg, df_inv_suggested, type_daily)
                            

            elif self.forecast_rule and coverage:
                    
                    df_fcst = self.df_fcst
                    df_fcst = pd.merge(df_fcst, df_leatimes, on=columns_group, how="inner")

                    if type_daily=="MaxDailyUsage":
                        period = self.get_period()
                        df_fcst["Coverage"] = df_fcst["Coverage"].apply(lambda x:period if x<period else x)

                    df_fcst['Coverage_delta'] = df_fcst['Coverage'].apply(lambda x: relativedelta(days=x))


                    if self.frequency_ == 'M':                      
                        df_avg = df_fcst[(df_fcst['Date'] > self.df_prep['timestamp'].max()) &
                                            (df_fcst['Date'] <= (self.df_prep['timestamp'].max() + df_fcst['Coverage_delta'] + MonthEnd(0)))]
                        
                        df_daily = self.processing(df_avg, df_inv_suggested, type_daily)
                    
                    elif self.frequency_ == 'W':                      
                        df_avg = df_fcst[(df_fcst['Date'] > self.df_prep['timestamp'].max()) &
                                            (df_fcst['Date'] <= (self.df_prep['timestamp'].max() + df_fcst['Coverage_delta']))] #cambia weeks o mes
                        
                        df_daily = self.processing(df_avg, df_inv_suggested, type_daily)


            elif self.forecast_rule is False:                  
                    if self.frequency_ == 'M':                      
                        df_avg = self.df_fcst[(self.df_fcst['Date'] <= self.df_prep['timestamp'].max()) & 
                                            (self.df_fcst['Date'] > (self.df_prep['timestamp'].max() - relativedelta(months=self.months_) + MonthEnd(0)))] #cambia esta regla respecto a true
                        
                        df_daily = self.processing(df_avg, df_inv_suggested, type_daily)
                    
                    elif self.frequency_ == 'W':                      
                        df_avg = self.df_fcst[(self.df_fcst['Date'] <= self.df_prep['timestamp'].max()) & 
                                            (self.df_fcst['Date'] > (self.df_prep['timestamp'].max() - relativedelta(weeks=self.weeks_)))]
                        
                        df_daily = self.processing(df_avg, df_inv_suggested, type_daily)
                    

            df_daily[type_daily] = round(df_daily[type_daily],3)

            if type_daily == "MaxDailyUsage":
              df_daily.loc[:,type_daily] = df_daily.loc[:,'AvgDailyUsage'] + df_daily.loc[:,type_daily]

            df_daily.loc[(df_daily[type_daily]<0),type_daily] = 0
        
        except KeyError as err:
            #self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise
        return df_daily