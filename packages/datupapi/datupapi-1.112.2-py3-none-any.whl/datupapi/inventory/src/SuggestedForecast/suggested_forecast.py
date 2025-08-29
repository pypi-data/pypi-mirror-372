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
from datupapi.inventory.src.ProcessForecast.define_periods import DefinePeriods
from datupapi.inventory.src.ProcessForecast.extract_forecast import Extract

class SuggestedForecast(DefinePeriods):

    def __init__(self,df_LeadTimes, df_Forecast, df_Prep, df_inv, column_forecast,
                  columns_metadata, frequency_, location, actualdate, default_coverage_=30, join_='left') -> None:
        self.df_LeadTimes = df_LeadTimes
        self.df_Forecast = df_Forecast
        self.df_Prep = df_Prep
        self.df_inv = df_inv
        self.columns_metadata = columns_metadata
        self.column_forecast = column_forecast
        self.frequency_ = frequency_
        self.location = location
        self.actualdate = actualdate
        self.default_coverage_ = default_coverage_  
        self.join_ = join_

    # FORMAT -----------------------------------------------------------------------------------------------------------------------------
    def format_date(self):      

        d1 = pd.Period(pd.to_datetime(str('28'+'-02-' + self.actualdate[0:4]), format="%d-%m-%Y"), freq='M').end_time.date()
        d2 = str(self.actualdate[0:4] + '-02-'+'29')

        if (self.df_Prep['timestamp'].max()).date() == d1:
            pmonth = 0
            finfebrero='28'
        elif str((self.df_Prep['timestamp'].max()).date()) == d2:
            pmonth = 1
            finfebrero='29'
        else:
            pmonth = 0
            finfebrero='28'

        lastdayDict = {'1':'31', '2': finfebrero, '3':'31', '4':'30', '5':'31', '6':'30', '7':'31', '8':'31', '9':'30', '10':'31', '11':'30', '12':'31'}
        DayOfMonth = int(self.actualdate[6:8])
        Month = str(int(self.actualdate[4:6]))
        DaysOfMonth = int(lastdayDict[Month])
        DayOfWeek = int(datetime.datetime.today().weekday()) + 1 
        DaysOfWeek = 7 
        actual_date = self.actualdate[0:8]
        actual_date = pd.to_datetime(str(int(float(actual_date))), format='%Y%m%d')

        return pmonth, DayOfMonth, DaysOfMonth, DayOfWeek, DaysOfWeek, actual_date
    
    
    # FORECAST CURRENT MONTH -------------------------------------------------------------------------------------------------------------------
    def forecast_current(self, col):
        frequency_ = self.frequency_ 
     
        pmonth, DayOfMonth, DaysOfMonth, DayOfWeek, DaysOfWeek, actual_date = self.format_date()
        
        df_lead_cruce = self.df_LeadTimes        
        df_lead_cruce = df_lead_cruce.groupby(self.columns_metadata, as_index=False).agg({'Coverage':'mean','AvgLeadTime':'mean'}).reset_index(drop=True)
        df_lead_cruce['Coverage'] = df_lead_cruce[['Coverage','AvgLeadTime']].apply(lambda x : x['Coverage'] if (x['Coverage']>=x['AvgLeadTime']) else x['AvgLeadTime'], axis=1)            
        df_lead_cruce = df_lead_cruce.drop(['AvgLeadTime'], axis=1) 
        df_lead_cruce = df_lead_cruce.drop_duplicates() 

        df_fcst_cruce = self.df_Forecast    
        df_final_fcst = pd.merge(df_fcst_cruce, df_lead_cruce, on=col, how='left')  
        df_final_fcst.loc[df_final_fcst['Coverage'].isnull(),'Coverage'] = self.default_coverage_

        if frequency_ == 'M':        
            df_final_fcst['Periods'] = (df_final_fcst['Coverage'] + DayOfMonth-1)//DaysOfMonth
            df_final_fcst = df_final_fcst.fillna(0)
                    
            df_fcst_current = df_final_fcst[(df_final_fcst['Date']>self.df_Prep['timestamp'].max()) & (df_final_fcst['Date']>=actual_date) &
                                            (df_final_fcst['Date']<= (actual_date + relativedelta(months=1) + MonthEnd(pmonth) + datetime.timedelta(days=-1)))] 
            df_fcst_current = df_fcst_current.drop_duplicates()

        if frequency_ == 'W':        
            df_final_fcst['Periods'] = (df_final_fcst['Coverage'] + DayOfWeek)//DaysOfWeek
            df_final_fcst = df_final_fcst.fillna(0)
            
            df_fcst_current = df_final_fcst[(df_final_fcst['Date']>self.df_Prep['timestamp'].max())&
                                            (df_final_fcst['Date']>=actual_date) & (df_final_fcst['Date']<= (actual_date + relativedelta(weeks=1)))]
            df_fcst_current = df_fcst_current.drop_duplicates()

        return df_fcst_current, df_final_fcst
    

    # SUGGESTED FORECAST FUNCTION -----------------------------------------------------------------------------------------------------------------------------
    def suggested_forecast(self):       
        location = self.location
        frequency_ = self.frequency_ 

        try:                 
            pmonth, DayOfMonth, DaysOfMonth, DayOfWeek, DaysOfWeek, actual_date = self.format_date()
            columns_group = list(self.df_inv.columns)
            #---------------------------------------------------------------------------------------------------------------------------------------------
            if location == False: 
                col = ['Item']
                if frequency_ == 'M':
                    df_fcst_current, df_final_fcst = self.forecast_current(col)
                    
                    df_extract_fcst_current =  Extract().extract_forecast(df_fcst_current, self.df_inv, column_forecast=self.column_forecast, location=self.location, frequency_= self.frequency_ ,
                                                        date_cols = 'Date', months_= 1, weeks_= 4, join_=self.join_).fillna(0) 
                    df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({self.column_forecast:"sum"})           
                    df_extract_fcst_current[self.column_forecast] = df_extract_fcst_current[self.column_forecast]*(1-DayOfMonth/DaysOfMonth)
                    df_extract_fcst_current = df_extract_fcst_current.rename(columns={self.column_forecast:'Current'})
                    df_extract_fcst_current = df_extract_fcst_current[['Item','Current']].copy()

                    columns = list(self.df_inv.columns)
                    columns.append(self.column_forecast)
                    df_fcst_final = pd.DataFrame(columns = columns)

                    df_fcst_={}
                    df_final_={}
                    lista = columns_group + self.columns_metadata[1:]

                    for period in range((int(df_final_fcst['Periods'].max()))+1):
                        df_fcst_[period] = df_final_fcst[df_final_fcst["Periods"] == period]
                        df_final_[period] = DefinePeriods(df_fcst_[period], df_extract_fcst_current, self.columns_metadata, period, DayOfWeek, DaysOfWeek, DayOfMonth, DaysOfMonth, pmonth, 
                                                               self.df_Prep, self.df_inv, self.column_forecast, self.location, self.frequency_ , self.join_, columns_group, actual_date, num=1).define_periods(col)
                        if df_fcst_final.empty:
                            if not df_final_[period].empty:
                                df_fcst_final = df_final_[period].copy()

                        elif not df_final_[period].empty:
                            df_fcst_final = pd.concat([df_fcst_final, df_final_[period]], ignore_index=True)

                if frequency_ == 'W':
                    df_fcst_current, df_final_fcst = self.forecast_current(col)

                    df_extract_fcst_current = Extract().extract_forecast(df_fcst_current, self.df_inv, column_forecast=self.column_forecast, location=self.location,frequency_= self.frequency_ ,
                                                        date_cols = 'Date',months_= 1,weeks_= 1,join_= self.join_).fillna(0) 
                    df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({self.column_forecast:"sum"})
                    df_extract_fcst_current[self.column_forecast] = df_extract_fcst_current[self.column_forecast] *(1-DayOfWeek/DaysOfWeek)
                    df_extract_fcst_current = df_extract_fcst_current.rename(columns={self.column_forecast:'Current'})
                    df_extract_fcst_current = df_extract_fcst_current[['Item','Current']].copy()

                    columns = list(self.df_inv.columns)
                    columns.append(self.column_forecast)
                    df_fcst_final = pd.DataFrame(columns = columns)
                    
                    df_fcst_={}
                    df_final_={}
                    lista = columns_group + self.columns_metadata[1:]

                    for period in range((int(df_final_fcst['Periods'].max()))+1):
                        df_fcst_[period] = df_final_fcst[df_final_fcst["Periods"] == period]
                        df_final_[period] = DefinePeriods(df_fcst_[period], df_extract_fcst_current, self.columns_metadata, period, DayOfWeek, DaysOfWeek, DayOfMonth, DaysOfMonth, pmonth, 
                                                                self.df_Prep, self.df_inv, self.column_forecast, self.location, self.frequency_, self.join_, columns_group, actual_date, num=1).define_periods(col)


                        if df_fcst_final.empty:
                            if not df_final_[period].empty:
                                df_fcst_final = df_final_[period].copy()

                        elif not df_final_[period].empty:
                            df_fcst_final = pd.concat([df_fcst_final, df_final_[period]], ignore_index=True)

                    
                # Forecast -----------------------------------------------------------------  
                df_fcst_final = df_fcst_final.groupby(lista, as_index=False).agg({self.column_forecast:"max"}) 

            #---------------------------------------------------------------------------------------------------------------------------------------------
            if location == True:
                col=['Item','Location']

                if frequency_ == 'M':
                    df_fcst_current, df_final_fcst = self.forecast_current(col)

                    df_extract_fcst_current = Extract().extract_forecast(df_fcst_current, self.df_inv, column_forecast=self.column_forecast, location=self.location,frequency_= self.frequency_ ,
                                                        date_cols = 'Date',months_= 1, weeks_= 4, join_= self.join_).fillna(0) 
                    df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({self.column_forecast:"sum"})           
                    df_extract_fcst_current[self.column_forecast] = df_extract_fcst_current[self.column_forecast]*(1-DayOfMonth/DaysOfMonth)
                    df_extract_fcst_current = df_extract_fcst_current.rename(columns={self.column_forecast:'Current'})
                    df_extract_fcst_current = df_extract_fcst_current[['Item','Location','Current']].copy()

                    columns = list(self.df_inv.columns)
                    columns.append(self.column_forecast)
                    df_fcst_final = pd.DataFrame(columns = columns)

                    df_fcst_={}
                    df_final_={}
                    lista = columns_group + self.columns_metadata[2:]

                    for period in range((int(df_final_fcst['Periods'].max()))+1):
                        df_fcst_[period] = df_final_fcst[df_final_fcst["Periods"] == period]
                        df_final_[period] =  DefinePeriods(df_fcst_[period], df_extract_fcst_current, self.columns_metadata, period, DayOfWeek, DaysOfWeek, DayOfMonth, DaysOfMonth, pmonth, 
                                                                 self.df_Prep, self.df_inv, self.column_forecast, self.location, self.frequency_, self.join_, columns_group, actual_date, num=2).define_periods(col)

                        if df_fcst_final.empty:
                            if not df_final_[period].empty:
                                df_fcst_final = df_final_[period].copy()

                        elif not df_final_[period].empty:
                            df_fcst_final = pd.concat([df_fcst_final, df_final_[period]], ignore_index=True)

            
                if frequency_ == 'W':
                    df_fcst_current, df_final_fcst = self.forecast_current(col)

                    df_extract_fcst_current = Extract().extract_forecast(df_fcst_current, self.df_inv, column_forecast=self.column_forecast, location=self.location,frequency_= self.frequency_ ,
                                                        date_cols = 'Date', months_= 1, weeks_= 1, join_= self.join_).fillna(0) 
                    df_extract_fcst_current = df_extract_fcst_current.groupby(columns_group, as_index=False).agg({self.column_forecast:"sum"})
                    df_extract_fcst_current[self.column_forecast] = df_extract_fcst_current[self.column_forecast] * (1-DayOfWeek/DaysOfWeek)
                    df_extract_fcst_current = df_extract_fcst_current.rename(columns={self.column_forecast:'Current'})
                    df_extract_fcst_current = df_extract_fcst_current[['Item','Location','Current']].copy()

                    columns = list(self.df_inv.columns)
                    columns.append(self.column_forecast)
                    df_fcst_final = pd.DataFrame(columns = columns)

                    df_fcst_={}
                    df_final_={}
                    lista = columns_group + self.columns_metadata[2:]

                    for period in range((int(df_final_fcst['Periods'].max()))+1):
                        df_fcst_[period] = df_final_fcst[df_final_fcst["Periods"] == period]
                        df_final_[period] = DefinePeriods(df_fcst_[period], df_extract_fcst_current, self.columns_metadata, period, DayOfWeek, DaysOfWeek, DayOfMonth, DaysOfMonth, pmonth,
                                                                 self.df_Prep, self.df_inv, self.column_forecast, self.location, self.frequency_, self.join_, columns_group, actual_date, num=2).define_periods(col)
                        
                        if df_fcst_final.empty:
                            if not df_final_[period].empty:
                                df_fcst_final = df_final_[period].copy()

                        elif not df_final_[period].empty:
                            df_fcst_final = pd.concat([df_fcst_final, df_final_[period]], ignore_index=True)


                # Forecast -----------------------------------------------------------------  
                df_fcst_final = df_fcst_final.groupby(lista, as_index=False).agg({self.column_forecast:"max"}) 

        except KeyError as err:
            #self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise
        return df_fcst_final   