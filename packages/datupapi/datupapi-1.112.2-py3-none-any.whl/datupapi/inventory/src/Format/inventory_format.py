import json
import pandas as pd
import numpy as np
import os.path as path

'''with open('conf/formatBase.json') as file:
    base = json.load(file)'''


class InventoryFormat():
    def __init__(self, df) ->None:
        self.df = df

    def format_and_type(self,  FormatType:int=None, use_decimal:bool=False):
        #formatType : 1 - Format_and_clean Function format (sort the values at the end of the function and do not fill the nans with 0 at the beginning)
        #formatType : 2 - format_tblinv Function format (fill the nans with 0 at the beginning and do not sort the df at the end)
        #formatType : 3 - Tbl indicators
        #formatType : 4 - Aditional clean format to export results 
        
        columns_des = ["Item","ItemDescription","Location","LocationDescription","Ranking","Provider","ProviderDescription","UM"]

        columns_inv = ["Inventory","Transit", "Transfer","Committed", "InventoryTransit","StockoutDays","InvTransStockoutDays"]

        columns_avg_max = ["AvgDailyUsage","MaxDailyUsage","AvgLeadTime","MaxLeadTime"]

        columns_exh = ["Exhibitions","ExhibitionsStatus"]

        columns_ss = ["SecurityStock","SecurityStockDays","SecurityStockDaysRef"]

        columns_cov = ["ReorderFreq","MinCoverage","MaxCoverage"]

        columns_sug = ["DemandHistory","SuggestedForecast","MinSuggestedForecast"]

        columns_reord = ["MinReorderPoint","ReorderPoint","ReorderPointDays","ReorderQtyBase","PurchaseFactor","ReorderQty",
                         "ReorderQtyDays","InvTransReorderDays","NextOrderReorderQtyBase","NextOrderReorderQty","ReorderStatus"]
        
        columns_cost = ["UnitCost","TotalCost","LastCost","UnitPrice","UnitCostAvg"]

        columns_others = ["Stability"]

        colmuns_meta = ["Customer","Country","ProductType","Weight","Dimension","Color","Origen","Gama","Marca","MateriaPrima",
                        "JefeProducto","JefeProductoDescription","GrupoCompra","Familia","Seccion","Categoria","SubCategoria","Linea",
                        "SubLinea","Canal","InventoryUnit","Comments","DeliveryFactor","PurchaseOrderUnit","PalletFactor","MOQ","Metadata"]
        
        columns_advance = ["BackSuggestedForecast","NextSuggestedForecast","BackReorderQtyBase","BackReorderQty","NextReorderQtyBase",
                           "NextReorderQty","MinOrderQty","MaxOrderQty","OtifOrder","TotalOrder","DelayDays","ShortFall"]

        columns_delete = ["InventoryTransitForecast","ForecastStockoutDays","LeadTimeDemand","ReorderQtyFactor"]

        cleanAndFormatIndicators = [*columns_des, *columns_inv, *columns_avg_max, *columns_exh, *columns_ss, 
                                    *columns_cov, *columns_sug, *columns_reord, *columns_cost, *columns_others,
                                    *colmuns_meta, *columns_advance, *columns_delete]

        cleanAndFormatCols = [*columns_inv, *columns_exh, *columns_ss, *columns_cov, *columns_sug, *columns_reord, 
                              *columns_advance, *columns_delete]
                              
        columns_drop = ["ExhibitionsStatus","SecurityStockDaysRef","PurchaseFactor",
                        "ReorderStatus","MinOrderQty","MaxOrderQty", "LeadTimeDemand"]

        cleanAndFormatCols = [i for i in cleanAndFormatCols if i not in columns_drop]


        
        tblInvIndicators = ["Item","ItemDescription", "Location", "Country", "Inventory", 
                            "Transit", "TransitDate", "TransitAdditional", "Committed",
                            "UM", "InventoryTransit", "StockoutDays", "InvTransStockoutDays",
                            "Ranking", "Provider", "ProductType",  "Customer", "JefeProducto",
                            "GrupoCompra", "Seccion", "Origen", "Color", "Marca", "MateriaPrima", "Gama"]
        
        tblInventory = ["Item","ItemDescription", "Location", "Inventory", "StockoutDays", "Transit",
                        "Committed", "InventoryTransit", "InvTransStockoutDays", "UM", "Provider"]

        tblInvCols = ["Inventory","Transit", "Committed","InventoryTransit","StockoutDays","InvTransStockoutDays"]

        df = self.df
        if FormatType == 1:
            indicators= cleanAndFormatIndicators
            cols = cleanAndFormatCols

        elif FormatType == 2:
            df=df.fillna(0)
            indicators = tblInvIndicators
            cols = tblInvCols

        elif FormatType == 3:
            df=df.fillna(0)
            indicators = tblInventory
            cols = tblInvCols

        elif FormatType == 4:
            indicators = [i for i in cleanAndFormatIndicators if i not in columns_delete]
            cols =  [i for i in cleanAndFormatCols if i not in columns_delete]

        
        try:

            for name in indicators:
                if name not in df.columns:
                    df[name] = "N/A"
            
            for a in cols:
                df[a] = df[a].astype(str).replace("N/A",'0')
                df[a] = df[a].astype(float) 
                
                if not use_decimal:  
                    df[a] = df[a].apply(np.ceil)
                    df[a] = df[a].astype(int)
                else:  
                    df[a] = df[a].round(2)

            if FormatType == 4:
                columns = columns_ss + colmuns_meta
                columns_drop = ["OtifOrder","TotalOrder","DelayDays","ShortFall"]

                for i in columns:
                    if df[i].nunique() == 1:
                        if df[i].iloc[0] == "N/A":
                            columns_drop.append(i)

                df.drop(columns=columns_drop, inplace=True)
                columns = df.columns
                indicators = [i for i in indicators if i in columns]


            cols =  df.select_dtypes(['float']).columns
            df[cols] =  df[cols].apply(lambda x: round(x, 3))
            
            df = df[indicators].copy()
            df = df.drop_duplicates().reset_index(drop=True) 
            if FormatType == 1:
                df = df.sort_values(by=['Ranking','Item']).drop_duplicates().reset_index(drop=True) 

        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise
        return df

    def general_indicators_format(self,Column:str=None):
        try:
            df=self.df               
            
            df.loc[:,Column] = df.loc[:,Column].fillna(0)
            df.loc[:,Column] = df.loc[:,Column].map(lambda x: 0 if x < 0 else x)
            df.loc[:, Column] = (
                df.loc[:, Column]
                .astype(str)
                .str.replace('-inf', '0')
                .str.replace('inf', '0')
                .str.replace('nan', '0')
                .astype(float)
                )

        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise         
        return df  

