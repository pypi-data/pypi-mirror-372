import json
import pandas as pd
import numpy as np
import os.path as path
from datupapi.inventory.src.Format.inventory_format import InventoryFormat

class InventoryTransformation(InventoryFormat):
    def __init__(self, df) ->None:
        self.df = df


    def functions_tblinv(self):    
        """
            Return a dataframe with all the indicators             
            :     
            >>> df_inv = functions_tblinv(df_inv)  
        """
        try:
            df=self.df               
            df.loc[:,'InventoryTransit'] = df['Inventory'] + df['Transit']
            df.loc[:,'StockoutDays']=( df['Inventory']- df['SecurityStock'])/ df['AvgDailyUsage']
            InventoryFormat(df).general_indicators_format("StockoutDays")
            

            df.loc[:,'InvTransStockoutDays'] = ( df['Inventory'] + df['Transit']- df['SecurityStock'])/ df['AvgDailyUsage']
            InventoryFormat(df).general_indicators_format("InvTransStockoutDays")
            
        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise         
        return df  