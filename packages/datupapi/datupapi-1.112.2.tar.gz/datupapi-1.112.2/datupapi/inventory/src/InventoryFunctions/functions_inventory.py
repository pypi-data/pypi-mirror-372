import os
import re
import pandas as pd
import numpy as np
from datupapi.configure.config import Config
from datetime import datetime
from datupapi.inventory.src.Format.inventory_format import InventoryFormat


class FunctionsInventory(InventoryFormat):
    """
        Class for return a dataframe with all the indicators         
        : param df_inv: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, Transit, DemandHistory  SuggestedForecast AvgDailyUsage MaxDailyUsage
        : param committed: Boolean to enable InventoryTransit computation including Committed
        : param min_inv: Boolean to allow the minimum amount of inventory in location
        : param div_purfac: Boolean to allow data divided by purchase days 
        : param ref_secstock: Boolean to allow Security Stock Ref 
        : param exhibitions: Boolean to allow Exhibitions
        : param order_date (str): date of the next order %Y-%m-%d 

        >>> df_inv = FunctionsInventory(df_inv,committed=True, min_inv=False, div_purfac=False, ref_secstock=False, exhibitions=False).functions_inventory()
    """

    def __init__(self, df_inv, committed, min_inv, ref_secstock, exhibitions, order_date=None, seasonality=False, reorder_new=False) -> None:      
        self.df_inv = df_inv
        self.committed = committed
        self.min_inv = min_inv        
        self.ref_secstock = ref_secstock
        self.order_date = order_date
        self.exhibitions = exhibitions
        self.seasonality = seasonality
        self.reorder_new = reorder_new

    def inventory(self,df):
        if (self.committed==True):
            df['InventoryTransit'] = df['Inventory'] + df['Transit'] - df['Committed']
        else:
            df['InventoryTransit'] = df['Inventory'] + df['Transit']
        
        df['InventoryTransitForecast'] = df['InventoryTransit'] - df['SuggestedForecast']
        df['LeadTimeDemand'] = df['SuggestedForecast']

        if self.reorder_new is False:
            df["NextOrderLeadTimeDemand"] = "N/A"
        
        else:
            df["NextOrderLeadTimeDemand"] = df["NextOrderSuggestedForecast"]

        return df


    def stock(self , df):

        if ((self.ref_secstock==False) & (self.exhibitions==False) & (self.seasonality==False)):
            df['SecurityStock'] = ((df['MaxDailyUsage']*df['MaxLeadTime']) - (df['AvgDailyUsage']*df['AvgLeadTime']))
        
        elif ((self.ref_secstock==True) & (self.exhibitions==False) & (self.seasonality==False)):
            df['SecurityStock'] = df['SecurityStockDaysRef'] * df['AvgDailyUsage']
        
        elif ((self.ref_secstock==False) & (self.exhibitions==True) & (self.seasonality==False)):
            df['SecurityStock'] = (((df['MaxDailyUsage']*df['MaxLeadTime']) - (df['AvgDailyUsage']*df['AvgLeadTime']))) + df['Exhibitions']
        
        elif ((self.ref_secstock==True) & (self.exhibitions==True) & (self.seasonality==False)):
            df['SecurityStock'] = (df['SecurityStockDaysRef'] * df['AvgDailyUsage']) + df['Exhibitions']                  
        

        elif ((self.ref_secstock==False) & (self.exhibitions==False) & (self.seasonality==True)):
            df['SecurityStock'] = ((df['MaxDailyUsageSeasonality']*df['MaxLeadTime']) - (df['AvgDailyUsageSeasonality']*df['AvgLeadTime']))
        
        elif ((self.ref_secstock==True) & (self.exhibitions==False) & (self.seasonality==True)):
            df['SecurityStock'] = df['SecurityStockDaysRef'] * df['AvgDailyUsageSeasonality']
        
        elif ((self.ref_secstock==False) & (self.exhibitions==True) & (self.seasonality==True)):
            df['SecurityStock'] = (((df['MaxDailyUsageSeasonality']*df['MaxLeadTime']) - (df['AvgDailyUsageSeasonality']*df['AvgLeadTime']))) + df['Exhibitions']
        
        elif ((self.ref_secstock==True) & (self.exhibitions==True) & (self.seasonality==True)):
            df['SecurityStock'] = (df['SecurityStockDaysRef'] * df['AvgDailyUsageSeasonality']) + df['Exhibitions']      


        df['SecurityStock'] = df['SecurityStock'].fillna(0)
        df['SecurityStock'] = df['SecurityStock'].map(lambda x: 0 if x < 1 else x)
        
        df['SecurityStockDays'] = (df['SecurityStock']) / (df['AvgDailyUsage'])
        InventoryFormat(df).general_indicators_format('SecurityStockDays')

        df['StockoutDays'] = (df['Inventory']-df['SecurityStock'])/df['AvgDailyUsage']
        InventoryFormat(df).general_indicators_format('StockoutDays')

        df['InvTransStockoutDays'] = (df['InventoryTransit']-df['SecurityStock'])/df['AvgDailyUsage']
        InventoryFormat(df).general_indicators_format('InvTransStockoutDays')
        
        df['ForecastStockoutDays'] = (df['InventoryTransitForecast']-df['SecurityStock'])/df['AvgDailyUsage']
        InventoryFormat(df).general_indicators_format('ForecastStockoutDays')
        return df



    def order_days(self, df:pd.DataFrame):
  
        """
        Function to get number of days until the next order

        : param df_f: Inventory's Dataframe
        """

        if self.reorder_new is False: 
            
            df["OrderDays"] = "N/A"
        
        else: 

            order_date = self.order_date

            actual_date = datetime.today().date()
            order_date = datetime.strptime(order_date, "%Y-%m-%d").date()
            difference = order_date - actual_date
            order_days = int(difference.days)

            df['OrderDays'] = order_days

        return df 



    def reorder(self, df):


        df['ReorderPoint'] = (df['LeadTimeDemand'] + df['SecurityStock']).map(lambda x: max(0, x))
        df['MinReorderPoint'] = (df['MinSuggestedForecast'] + df['SecurityStock']).map(lambda x: max(0, x))
        df['ReorderPointDays'] = df['ReorderPoint'] / df['AvgDailyUsage']
        df['RQty'] = (df['ReorderPoint'] - df['InventoryTransit']).map(lambda x: max(0, x))


        InventoryFormat(df).general_indicators_format('ReorderPointDays')


        if self.reorder_new is False: 

            df['ReorderStatus'] = df.apply(
                lambda x: 'Order' if (
                    x['InventoryTransit'] < x['MinReorderPoint'] or 
                    x['InventoryTransit'] < x['SecurityStock']
                ) else 'Hold', axis=1
            )

            df['ReorderStatus'] = df.apply(
                lambda x: 'Hold' if (
                    (0 < x['MinReorderPoint'] - x['InventoryTransit'] < 1) and 
                    x['ReorderStatus'] == 'Order'
                ) else x['ReorderStatus'], axis=1
            )

        else:

            df['ReorderStatus'] = df.apply(
                lambda x: 'Order' if (
                    x['InventoryTransit'] < x['ReorderPoint'] or 
                    x['InventoryTransit'] < x['SecurityStock']
                ) else 'Hold', axis=1
            )

            df['ReorderStatus'] = df.apply(
                lambda x: 'Hold' if (
                    (0 < x['ReorderPoint'] - x['InventoryTransit'] < 1) and 
                    x['ReorderStatus'] == 'Order'
                ) else x['ReorderStatus'], axis=1
            )

            df['ReorderStatus'] = df.apply(
                lambda x: 'Order' if (
                    x['ReorderStatus'] == 'Order' and 
                    (x['InvTransStockoutDays'] <= x['AvgLeadTime'] or x['OrderDays'] == 0)
                ) else 'Hold', axis=1
            )


        if self.min_inv == False:

            df['ReorderQty'] = df.apply(
                lambda x: x['RQty'] if x['ReorderStatus'] == 'Order' else 0, axis=1
            )

            df['ReorderQty'] = df.apply(
                lambda x: 0 if x['ReorderQty'] < 1 else x['ReorderQty'], axis=1
            )

        else:
            
            df['ReorderQty'] = df.apply(
                lambda x: x['RQty'] if x['ReorderStatus'] == 'Order' else x['DemandHistory'], axis=1
            )

            df['ReorderQty'] = df.apply(
                lambda x: 0 if x['ReorderQty'] < 1 else x['ReorderQty'], axis=1
            )

        return df




    def next_order_reorder(self, df):


        if self.reorder_new is False:

            df["NextOrderReorderPoint"] = "N/A"
            df["NextOrderRQty"] = "N/A"
            df["NextOrderReorderQty"] = "N/A"
                
        else:

            df['NextOrderReorderPoint'] = (df['NextOrderLeadTimeDemand'] + df['SecurityStock']).map(lambda x: max(0, x))
            df['NextOrderRQty'] = (df['NextOrderReorderPoint'] - df['InventoryTransit']).map(lambda x: max(0, x))


            if self.min_inv == False:

                df['NextOrderReorderQty'] = df.apply(
                    lambda x: x['NextOrderRQty'] if x['ReorderStatus'] == 'Order' else 0, axis=1
                )

                df['NextOrderReorderQty'] = df.apply(
                    lambda x: 0 if x['NextOrderReorderQty'] < 1 else x['NextOrderReorderQty'], axis=1
                )

            else:
                
                df['NextOrderReorderQty'] = df.apply(
                    lambda x: x['NextOrderRQty'] if x['ReorderStatus'] == 'Order' else x['DemandHistory'], axis=1
                )

                df['NextOrderReorderQty'] = df.apply(
                    lambda x: 0 if x['NextOrderReorderQty'] < 1 else x['NextOrderReorderQty'], axis=1
                )

        return df




    def minmax(self, df): 
                           
        df['MinQty'] = (df['BackSuggestedForecast'] + df['SecurityStock']- df['InventoryTransit']).map(lambda x: 0 if x < 1 else x)   
        df['MaxQty'] = (df['NextSuggestedForecast'] + df['SecurityStock']- df['InventoryTransit'] ).map(lambda x: 0 if x < 1 else x)        
        
        df['MinReorderQty'] = df.apply(lambda x: (x['MinQty'] if (x['MinQty']<x['MaxQty']) else x['MaxQty']) if (x['ReorderStatus']=='Order') else 0 , axis=1 )
        df['MinReorderQty'] = df.apply(lambda x: (0 if (x['MinReorderQty'] < 1) else x['MinReorderQty']) if(x['ReorderStatus']=='Order') else x['MinReorderQty'], axis=1)
        
        df['MaxReorderQty'] = df.apply(lambda x: (x['MinQty'] if (x['MinQty']>x['MaxQty']) else x['MaxQty']) if (x['ReorderStatus']=='Order') else 0 , axis=1 )
        df['MaxReorderQty'] = df.apply(lambda x: (0 if (x['MaxReorderQty'] < 1 ) else x['MaxReorderQty']) if(x['ReorderStatus']=='Order') else x['MaxReorderQty'], axis=1)        

        return df


    def purchase_factor(self,df):

        df['ReorderQtyBase'] = df['ReorderQty']
        df['BackReorderQtyBase'] = df['MinReorderQty']
        df['NextReorderQtyBase'] = df['MaxReorderQty']        
        df['ReorderQty'] = ((df['ReorderQty']/df['PurchaseFactor']).apply(np.ceil))*df['PurchaseFactor']
        df['BackReorderQty'] = ((df['MinReorderQty']/df['PurchaseFactor']).apply(np.ceil))*df['PurchaseFactor']
        df['NextReorderQty'] = ((df['MaxReorderQty']/df['PurchaseFactor']).apply(np.ceil))*df['PurchaseFactor']

        df['ReorderQtyFactor'] = round(df['ReorderQty']/df['PurchaseFactor'])


        if self.reorder_new is False:

            df["NextOrderReorderQtyBase"] = "N/A"

        else:

            df['NextOrderReorderQtyBase'] = df['NextOrderReorderQty']   
            df['NextOrderReorderQty'] = ((df['NextOrderReorderQty']/df['PurchaseFactor']).apply(np.ceil))*df['PurchaseFactor']


        return df


    def reorder_days(self , df):

        df['ReorderQtyDays'] = (df['ReorderQty'])/df['AvgDailyUsage']
        InventoryFormat(df).general_indicators_format('ReorderQtyDays')

        df['InvTransReorderDays'] = df['ReorderQtyDays'] + df['InvTransStockoutDays']

        return df

             
    def functions_inventory(self):
        """
            Return a dataframe with all the indicators         
            : param df_inv: Inventory's Dataframe with the columns Item, Location(Optional), Inventory, Transit, DemandHistory  SuggestedForecast AvgDailyUsage MaxDailyUsage
            : param committed: Boolean to enable InventoryTransit computation including Committed
            : param min_inv: Boolean to allow the minimum amount of inventory in location            
            : param ref_secstock: Boolean to allow Security Stock Ref 
            : param exhibitions: Boolean to allow Exhibitions

            >>> df_inv = functions_inventory(df_inv,min_inv=False,div_purfac=False,ref_secstock=False,exhibitions=False)  
        """
        try:            
            df = self.df_inv         
            df = self.inventory(df)
            df = self.stock(df)
            df = self.order_days(df)
            df = self.reorder(df)
            df = self.next_order_reorder(df)
            df = self.minmax(df)                                   
            df = self.purchase_factor(df)
            df = self.reorder_days(df)  
            df.drop(columns=['RQty','NextOrderRQty','MinQty','MaxQty'], inplace=True) 

            if 'UnitCost' not in df.columns:
                df.loc[:,'UnitCost'] = 0           

            if 'TotalCost' not in df.columns:        
                df.loc[:,'TotalCost'] = df['UnitCost'] * df['ReorderQty']
            
        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise         
        return df 