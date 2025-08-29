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
from datupapi.prepare.format import Format
from pandas.tseries.offsets import MonthEnd
from functools import reduce

class Extract():
    """
    Class for processing inventory and forecasts.
    This class provides methods for extracting sales history, generating forecasts, and defining periods.

    Args:
        df_prep (pandas.DataFrame): Qprep Dataframe prepared for Forecast.
        df_invopt (pandas.DataFrame): Inventory's Dataframe with the columns Item Cleaned.
        param location: Boolean to enable the use of Location in the Inventory's dataframe
    """

    # SALES HISTORY-----------------------------------------------------------------------
    def extract_sales_history (self,df_prep, df_invopt,date_cols,location=True):  
        """
        Returns a data frame that incorporates the DemandHistory column into the inventory data frame.

        : param df_prep: Dataframe prepared for Forecast
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional)
        : param date_cols: Column name of date from df_prep
        : param location: Boolean to enable the use of Location in the Inventory's dataframe
        : return df_extract: Dataframe with addition the column Sales History in the Inventory's Dataframe

        >>> df_extract = extract_sales_history (df_prep,df_invopt,date_cols='timestamp', location=self.use_location)
        >>> df_extract =
                                            Item    Location  DemandHistory
                                idx0          85      905        200
                                idx1          102     487        100
        """      
        try:
            df_prep_history = df_prep[df_prep[date_cols]== df_prep[date_cols].max()].copy()
            if location:
                dict_names = {'item_id':'Item',
                                'location':'Location',
                                'demand':'DemandHistory'}
                df_prep_history = df_prep_history.rename(columns=dict_names)

                df_prep_history['Item'] = df_prep_history['Item'].astype(str)
                df_prep_history['Location'] = df_prep_history['Location'].astype(str)
                df_invopt['Item'] = df_invopt['Item'].astype(str)
                df_invopt['Location'] = df_invopt['Location'].astype(str)

                df_extract = pd.merge(df_invopt,df_prep_history[['Item','Location','DemandHistory']],on=['Item','Location'],how='left')
            else:
                dict_names =  {'item_id':'Item',
                                'demand':'DemandHistory'}
                df_prep_history = df_prep_history.rename(columns=dict_names)

                df_prep_history['Item'] = df_prep_history['Item'].astype(str)
                df_invopt['Item'] = df_invopt['Item'].astype(str)

                df_extract = pd.merge(df_invopt,df_prep_history[['Item','DemandHistory']],on=['Item'],how='left')

        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise
        return df_extract


    #FORECAST-----------------------------------------------------------------------
    def extract_forecast(self,df_fcst,df_invopt,date_cols,frequency_,months_,location,column_forecast='ForecastCollab',weeks_=4,join_='left'):      
        """
        Returns a data frame that incorporates the SuggestedForecast column into the inventory data frame.

        : param df_fcst: Forecast's Dataframe 
        : param df_invopt: Inventory's Dataframe with the columns Item, Location(Optional), DemandHistory
        : param date_cols: Column name of date from df_fcst
        : param frequency_: Target frequency to the dataset
        : param months_: Number of months
        : param location: Boolean to enable the use of Location in the Inventory's dataframe
        : param column_forecast: name of the column where the desired forecast is located 
        : param join_: type of join with forecast 

        >>> df_extract = extract_forecast (df_prep,df_fcst,df_invopt,date_cols='Date', location=self.use_location, frequency_= self.dataset_frequency,join_='left')
        >>> df_extract =
                                            Item    Location  DemandHistory   SuggestedForecast
                                idx0          85      905         23              200
                                idx1          102     487         95              100
        """ 
        try:
            if frequency_ == 'M':
                df_fcst_sug = df_fcst[df_fcst[date_cols]>= (df_fcst[date_cols].max() - relativedelta(months=months_))].copy()
                if location:
                    cols=['Item','Location']
                    df_fcst_sug = df_fcst_sug.groupby(cols, as_index=False)\
                                                                    .agg({column_forecast: "sum"})\
                                                                    .reset_index(drop=True)
                    df_invopt[cols] = df_invopt[cols].astype(str)                    
                    df_fcst_sug[cols] = df_fcst_sug[cols].astype(str)                    
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item','Location', column_forecast]], on=cols, how=join_)
                else:
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item', column_forecast]],on=['Item'],how=join_)
            
            elif frequency_ == 'W':
                df_fcst_sug = df_fcst[df_fcst[date_cols]>= (df_fcst[date_cols].max() - relativedelta(weeks=weeks_))].copy()
                if location:
                    cols=['Item','Location']
                    df_fcst_sug = df_fcst_sug.groupby(cols, as_index=False)\
                                                                    .agg({column_forecast: "sum"})\
                                                                    .reset_index(drop=True)
                    df_invopt[cols] = df_invopt[cols].astype(str)                    
                    df_fcst_sug[cols] = df_fcst_sug[cols].astype(str) 
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item','Location', column_forecast]], on=cols, how=join_)
                else:
                    df_fcst_sug = df_fcst_sug.groupby(['Item'], as_index=False)\
                                          .agg({column_forecast: "sum"})\
                                          .reset_index(drop=True)
                    df_invopt['Item'] = df_invopt['Item'].astype(str)
                    df_fcst_sug['Item'] = df_fcst_sug['Item'].astype(str)
                    df_extract = pd.merge(df_invopt,df_fcst_sug[['Item', column_forecast]],on=['Item'],how=join_)

        except KeyError as err:
            #self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise
        return df_extract