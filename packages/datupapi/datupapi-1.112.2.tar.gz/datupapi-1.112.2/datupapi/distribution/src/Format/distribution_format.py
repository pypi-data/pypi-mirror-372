import json
import pandas as pd
import numpy as np
import os.path as path

'''with open('conf/formatBase.json') as file:
    base = json.load(file)'''



class DistributionFormat():
    def __init__(self, df) ->None:
        self.df = df

    def format_and_type(self,  FormatType:int=None):
        #formatType : 1 - Format_and_clean Function format (sort the values at the end of the function and do not fill the nans with 0 at the beginning)

        columns_des = ["Item","ItemDescription","LocationOrigin", "LocationOriginDescription","LocationDestination",
                       "LocationDestinationDescription","Ranking","UM"]

        columns_inv = ["InventoryOrigin","InventoryDestination","TransitOrigin","TransitDestination", 
                       "TransferOrigin","TransferDestination", "InventoryTransitOrigin","InventoryTransitDestination"]

        columns_ss = ["SecurityStock"]

        columns_cov = ["MaxCoverage"]

        columns_sug = ["SuggestedForecast"]

        columns_dist = ["Offer","DeliveryQty","MaxInventory","LocationPriority","TransferLotSizePallet","PalletFactor",
                        "TransferLotSize","DeliveryFactor","TransferLotSizeUnit","PendingLotSize"]
        
        columns_cost = ["UnitCost","TotalCost"]

        colmuns_meta = ["DistributionID","StorageCapacity","MaxPallet","TotalInventoryPallets","Customer","Country",
                        "Vehiculo","TotalWeight","TotalWeightDistributed","TotalWeightUM","InventoryExp","DaysExp",
                        "ExpirationDate","TotalTransferLotSize","ProductType","Weight","WeightUM","WeightPallet","WeightPalletUM",
                        "WeightUnit","WeightUnitUM","CombinedWeight","CombinedWeightUM","Dimension","Color","Origen","Gama","Marca","MateriaPrima",
                        "Familia","Seccion","Categoria","SubCategoria","Linea","SubLinea","Canal"]
        
        columns_advance = ["NextTransit","DaysTransit","TransitDate","NextPickingDate","NextDeliveryDate","MinPickingDate"]


        cleanAndFormatIndicators = [*columns_des, *columns_inv,*columns_ss, *columns_cov, *columns_sug, 
                                    *columns_dist, *columns_cost,*columns_advance,*colmuns_meta]

        cleanAndFormatCols = [*columns_inv, *columns_ss, *columns_cov, *columns_sug, *columns_dist]
                              
        columns_drop = ["MaxInventory","LocationPriority","TransferLotSizePallet","PalletFactor"]

        cleanAndFormatCols = [i for i in cleanAndFormatCols if i not in columns_drop]


        df = self.df
        if FormatType == 1:
            indicators= cleanAndFormatIndicators
            cols = cleanAndFormatCols
        
        try:

            for name in indicators:
                if name not in df.columns:
                    df[name] = "N/A"
            
            for a in cols:
                df[a] = df[a].astype(str).replace("N/A",'0')
                df[a] = df[a].astype(float) 
                df[a] = df[a].apply(np.ceil)
                df[a] = df[a].astype(int) 

            if FormatType == 1:
                columns = columns_ss + colmuns_meta
                columns_drop = []

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

        except KeyError as err:
            self.logger.exception(f'No column found. Please check columns names: {err}')
            print(f'No column found. Please check columns names')
            raise
        return df


