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
from datupapi.inventory.src.ProcessForecast.extract_forecast import Extract


class DefinePeriods(Extract):

    def __init__(self,df_ ,df_current ,meta_cols, period, DayOfWeek, DaysOfWeek, DayOfMonth, DaysOfMonth,pmonth, df_Prep, df_inv, column_forecast,
                 location, frequency_, join_, columns_group, actual_date, num) -> None:
        self.df_ = df_
        self.df_current = df_current
        self.meta_cols = meta_cols
        self.period = period
        self.DayOfWeek = DayOfWeek
        self.DaysOfWeek = DaysOfWeek
        self.DayOfMonth = DayOfMonth
        self.DaysOfMonth = DaysOfMonth
        self.pmonth = pmonth
        self.df_Prep = df_Prep
        self.df_inv = df_inv
        self.column_forecast = column_forecast
        self.location = location
        self.frequency_ = frequency_
        self.join_ = join_
        self.columns_group = columns_group
        self.actual_date = actual_date  
        self.num = num       

    
    def period_zero(self,col):
        frequency_ = self.frequency_ 
        df_ = self.df_

        if frequency_ == 'M': 
            df_ = df_[(df_['Date']>self.df_Prep['timestamp'].max()) & (df_['Date']>=self.actual_date) &
                      (df_['Date']<= (self.actual_date + relativedelta(months=1) + MonthEnd(self.pmonth) + datetime.timedelta(days=-1)))]

            df_a = df_.drop_duplicates()
            df_extract_forecast = Extract().extract_forecast(df_a, self.df_inv, column_forecast=self.column_forecast, location=self.location, frequency_= self.frequency_,
                                                    date_cols = 'Date', months_= 1, weeks_= 4, join_=self.join_).fillna(0)  
            df_extract_forecast = df_extract_forecast.groupby(self.columns_group, as_index=False).agg({self.column_forecast:"sum"})

            cols_per = ['Coverage']
            lista_1 = self.meta_cols+cols_per
            lista_2 = self.columns_group + self.meta_cols[self.num :] + [self.column_forecast]
            df_b = df_[lista_1].drop_duplicates()                 
            df_final = pd.merge(df_extract_forecast, df_b,on=col, how='left')                                
            df_final[self.column_forecast] = df_final[self.column_forecast] * (1-((self.DaysOfMonth - df_final['Coverage'])/self.DaysOfMonth))
            df_final = df_final[lista_2]     

        if frequency_ == 'W':   
            df_ = df_[(df_['Date']>self.df_Prep['timestamp'].max()) & (df_['Date']>=self.actual_date) & (df_['Date']<= (self.actual_date + relativedelta(weeks=1)))].copy()
                                
            df_ = df_.drop_duplicates()
            df_extract_forecast = Extract().extract_forecast(df_, self.df_inv, column_forecast=self.column_forecast, location=self.location,frequency_= self.frequency_,
                                    date_cols = 'Date', months_= 1, weeks_= 1, join_=self.join_).fillna(0) 
            df_final = df_extract_forecast.groupby(self.columns_group, as_index=False).agg({self.column_forecast:"sum"})
            df_final[self.column_forecast] = df_final[self.column_forecast] * (1 - self.DayOfWeek/self.DaysOfWeek)      

        return df_final    


    def period_all(self,col):
        frequency_ = self.frequency_
        df_ = self.df_       

        if frequency_ == 'M': 
            df_ = df_[(df_['Date']>(self.actual_date + relativedelta(months=1) + MonthEnd(self.pmonth)+ datetime.timedelta(days=-1))) &
                        (df_['Date']<= (self.actual_date + relativedelta(months=(self.period+1)) + MonthEnd(self.pmonth) + datetime.timedelta(days=-1)))]                       
            df_a = df_.drop_duplicates()
            df_extract_forecast =  Extract().extract_forecast(df_a, self.df_inv, column_forecast=self.column_forecast, location=self.location, frequency_= self.frequency_,
                                                    date_cols = 'Date', months_= (self.period+1), weeks_= ((self.period+1)*4), join_=self.join_).fillna(0) 
            df_extract_forecast = df_extract_forecast.groupby(self.columns_group, as_index=False).agg({self.column_forecast:"sum"}) 
            df_extract_forecast = df_extract_forecast.rename(columns={self.column_forecast:'Next'})
        
            cols_per = ['Coverage','Periods']
            lista_1 = self.meta_cols + cols_per
            lista_2 = self.columns_group + self.meta_cols[self.num :] + [self.column_forecast]
            df_b = df_[lista_1].drop_duplicates() 
            df_final = pd.merge(df_extract_forecast, df_b, on=col, how='left')
            df_final = pd.merge(df_final, self.df_current, on=col, how='left')
            df_final[self.column_forecast] = df_final['Current'] + df_final['Next'] * ((df_final['Coverage'] - self.DaysOfMonth + self.DayOfMonth)/(df_final['Periods'] * self.DaysOfMonth))
            df_final = df_final[lista_2].copy()

        if frequency_ == 'W': 
            df_ = df_[(df_['Date']>(self.actual_date+relativedelta(weeks=1))) & (df_['Date']<= (self.actual_date + relativedelta(weeks=(self.period+1))))].copy()

            df_a=df_.drop_duplicates()
            df_extract_forecast = Extract().extract_forecast(df_a, self.df_inv, column_forecast= self.column_forecast, location= self.location, frequency_= self.frequency_,
                                                date_cols= 'Date', months_= (self.period+1) , weeks_= (self.period+1), join_=self.join_).fillna(0) 
            df_extract_forecast = df_extract_forecast.groupby(self.columns_group, as_index=False).agg({self.column_forecast:"sum"}) 
            df_extract_forecast = df_extract_forecast.rename(columns={self.column_forecast:'Next'})                  

            cols_per = ['Coverage','Periods']
            lista_1 = self.meta_cols + cols_per
            lista_2 = self.columns_group + self.meta_cols[self.num :] + [self.column_forecast]
            df_b = df_[lista_1].drop_duplicates()                 
            df_final = pd.merge(df_extract_forecast, df_b, on=col, how='left')
            df_final = pd.merge(df_final, self.df_current, on=col, how='left')
            df_final[self.column_forecast] = df_final['Current'] + df_final['Next'] * ((df_final['Coverage'] - self.DaysOfWeek + self.DayOfWeek)/(df_final['Periods'] * self.DaysOfWeek))
            df_final = df_final[lista_2]    

        return df_final    
              

    #DEFINE PERIODS-----------------------------------------------------------------------

    def define_periods(self,col):
        df_ = self.df_ 
        location = self.location 
        frequency_ = self.frequency_
        period = self.period 
        df_current = self.df_current

        try:                                     
            if location == False:  
                if frequency_ == 'M':                            
                    if not df_.empty:
                        itemslist_ = list(df_['Item'].unique())
                        df_current = df_current[df_current['Item'].isin(itemslist_)].copy()

                        # LESS THAN A PERIOD-----------------------------------------------------
                        if period == 0:
                            df_final = self.period_zero(col)

                        if period != 0:   
                            df_final = self.period_all(col)    

                    if df_.empty:
                        columns = list(self.df_inv.columns)
                        columns.append(self.column_forecast)
                        df_final = pd.DataFrame(columns = columns)


                if frequency_ == 'W':   
                    if not df_.empty:
                        itemslist_ = list(df_['Item'].unique())
                        df_current = df_current[df_current['Item'].isin(itemslist_)].copy()

                        # LESS THAN A PERIOD-----------------------------------------------------
                        if period == 0:
                            df_final = self.period_zero(col)

                        if period != 0:
                            df_final = self.period_all(col)      

                    if df_.empty:
                        columns = list(self.df_inv.columns)
                        columns.append(self.column_forecast)
                        df_final = pd.DataFrame(columns = columns)

            
            if location == True :   
                if frequency_ == 'M':
                    if not df_.empty:
                        itemslist_ = list(df_['Item'].unique())
                        df_current = df_current[df_current['Item'].isin(itemslist_)].copy()

                        # LESS THAN A PERIOD-----------------------------------------------------
                        if period == 0:
                            df_final = self.period_zero(col)
                            
                        if period != 0:                          
                            df_final = self.period_all(col)  

                    if df_.empty:                                
                        columns = list(self.df_inv.columns)
                        columns.append(self.column_forecast)
                        df_final = pd.DataFrame(columns = columns)


                if frequency_ == 'W':   
                    if not df_.empty:
                        itemslist_ = list(df_['Item'].unique())
                        df_current = df_current[df_current['Item'].isin(itemslist_)].copy()

                        # LESS THAN A PERIOD-----------------------------------------------------
                        if period == 0:
                              df_final = self.period_zero(col)

                        if period != 0:
                            df_final = self.period_all(col)     

                    if df_.empty:
                        columns = list(self.df_inv.columns)
                        columns.append(self.column_forecast)
                        df_final = pd.DataFrame(columns = columns)        

        except KeyError as err:
            #self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise

        return df_final