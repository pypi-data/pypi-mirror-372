import pandas as pd
import numpy as np
from pulp import (LpMinimize,LpProblem,lpSum,LpVariable)


class FunctionsDistribution(object):
    """
    Class for calculating and adjusting suggested distributions.
    """
    
    def __init__(self):
        pass

    def set_priority(self, df_cost, df_priority):
        """
        Sets priorities based on a DataFrame of costs and priorities.
        """
        df_cost = df_cost.copy()
        df_priority = df_priority.copy()
        
        df_priority.columns = ["Origin", "priority"]
        list_origin = df_cost["Origin"].unique().tolist()

        df_cost = pd.merge(df_cost, df_priority, on=['Origin'], how='left').fillna(50)
        df_cost = df_cost.set_index('Origin') 
        
        for i in range(len(list_origin)):
            df_cost.iloc[i, 0:-1] = df_cost.iloc[i, 0:-1] * df_cost.iloc[i, -1]
        df_cost = df_cost.iloc[:, 0:-1]  

        return df_cost


    def adjust_demand(self, demand, prop, maxim, pdv_def):
        """
        Adjusts the demand to avoid exceeding the maximum allowed units in the warehouse.
        """
        for loc in pdv_def:
            bol = True
            while bol:
                if (demand.loc[loc].sum() > maxim.loc[loc].sum()) and (maxim.loc[loc].sum()>0):
                    demand.loc[loc] = demand.loc[loc] * prop
                else:
                    bol = False

        return demand


    def adjust_total_demand(self, demand, prop, maxim):
        """
        Adjusts the total demand to not exceed the maximum available units.
        """
        bol = True

        while bol:
            if (demand['Demand'].sum() >= maxim) and (maxim>0):
                demand['Demand'] = demand['Demand'] * prop
            else:
                bol = False

        return demand


    def solve_model(self, item, pdv_ex, pdv_def, cost, demand, offer, maxim):
        """
        Solves the transportation model for a specific item.
        """
        model = LpProblem(f'Transportation_Problem_{item}', LpMinimize)
        var = dict()

        # Define variables
        for i in pdv_def:
            for j in pdv_ex:
                var[(i, j)] = LpVariable(f'S{j}E{i}', 0)

        # Set objective function
        model += lpSum([cost[i][j] * var[(i, j)] for i in pdv_def for j in pdv_ex])

        # Define constraints
        for j in pdv_ex:
            model += lpSum([var[(i, j)] for i in pdv_def]) <= offer.loc[j]

        for i in pdv_def:
            model += lpSum(var[(i, j)] for j in pdv_ex) == demand.loc[i]
            model += lpSum(var[(i, j)] for j in pdv_ex) <= maxim.loc[i]

        # Solve the model
        solubility = model.solve()

        # Format and round decimal values to the nearest integer
        if solubility == 1:
            result = list()
            for j in pdv_ex:
                for i in pdv_def:
                    result.append([j, i, var[(i, j)].varValue])
            solution = pd.DataFrame(result)
            
            return solution


    def distribution(self, df_demand, df_offer, deficit_dict, excess_dict, df_cost, items, 
                    df_max_fcst, max_dict, item_adjust_factor_, total_adjust_factor_, expiration=True):
        """
        Calculates suggested distributions item by item using offer and demand. 
        Additionally, prioritizes locations based on the cost matrix and max values.

        Returns a DataFrame with TransferLotSize.       
            : param df_demanda: Dataframe with demand by item and location
            : param df_oferta: Dataframe with offer by item and location
            : param deficit_dict: Dictionary Item :  list of Locations with deficit            
            : param excesos_dict: Dictionary Item :  list of Locations with excess
            : param df_cost: Dataframe of Costs
            : param items: List of items to distribuition 
            : param df_max_fcst: Dataframe with max inventory by item-location using forecasts
            : param max_dict: Dictionary Item : max inventory. Max inventory by item. 
            : param item_adjust_factor_: float. Factor Value to ajust demand
            : param total_adjust_factor_: float. Factor Value to ajust demand
            : param expiration: Boolean to allow items with expiration.
        """
        try:
            df_demand = df_demand.copy()
            df_offer = df_offer.copy()
            excess_dict = excess_dict.copy()
            deficit_dict = deficit_dict.copy()
            df_cost = df_cost.copy()
            df_max_fcst = df_max_fcst.copy()
            max_dict = max_dict.copy()

            results = pd.DataFrame()
            state = {}

            if expiration:
                df_inv_exp = df_offer[['Item', 'Location', 'DaysExp']].copy()

            for it in items:
                pdv_ex = excess_dict[it]
                pdv_def = deficit_dict[it]

                offer_it = df_offer[(df_offer['Item'] == it) & (df_offer['Location'].isin(pdv_ex))][['Location', 'Offer']].set_index('Location')
                demand_it = df_demand[(df_demand['Item'] == it) & (df_demand['Location'].isin(pdv_def))][['Location', 'Demand']].set_index('Location')

                if expiration: 
                    cost = df_cost.loc[pdv_ex]
                    inv_exp =  df_inv_exp[(df_inv_exp['Item'] == it) & (df_inv_exp['Location'].isin(pdv_ex))][['Location', 'DaysExp']].set_index('Location')
                    inv_exp.loc[:, 'Score'] = inv_exp.apply(lambda x: 0 if (x['DaysExp']==inv_exp['DaysExp'].min()) else (10 if (x['DaysExp']==inv_exp['DaysExp'].max()) else 5), axis=1)
                    cost = cost.join(inv_exp)

                    for i in range(len(pdv_ex)):
                        cost.iloc[i, 0:-2] = ((cost.iloc[i, 0:-2] * cost.iloc[i, -1]) / 100) + cost.iloc[i, 0:-2]

                    cost = cost.iloc[:, 0:-2]

                else:
                    cost = df_cost.loc[pdv_ex][pdv_def]

                max_val = df_max_fcst.loc[pdv_def][[it]]
                demand_it = self.adjust_demand(demand_it, item_adjust_factor_, max_val, pdv_def)

                max_total = max_dict[it]
                demand_it = self.adjust_total_demand(demand_it, total_adjust_factor_, max_total)

                res = self.solve_model(it, pdv_ex, pdv_def, cost, demand_it, offer_it, max_val)

                res.columns = ['LocationOrigin', 'LocationDestination', 'TransferLotSize']
                res['Item'] = it

                if not res.empty:
                    res['TransferLotSize'] = res['TransferLotSize']
                    state[it] = 'success'

                    if results.empty:
                        if not res.empty:
                            results = res.copy()

                    elif not res.empty:
                        results = pd.concat([results, res])

                    results = results [['Item', 'LocationOrigin', 'LocationDestination', 'TransferLotSize']]
                else:
                    state[it] = 'failure'    

        except KeyError as err:
            self.logger.exception(f'Column not found. Please check column names: {err}')
            print(f'Column not found. Please check column names')
            raise   

        return results



    def adjust_delivery(self, df):
        """
        Returns a DataFrame with adjusted TransferLotSize.

        The function adjusts the suggested distribution by rounding the units,
        without exceeding the total units to be distributed per item calculated,
        complying with the rules of maximum units to be distributed.

        The rounding is done starting with the highest priority locations, rounding up,
        when the maximum calculated units are reached, those that have not been rounded are set to zero.
        """
        df = df.copy().reset_index(drop=True)

        list_origins = df["LocationOrigin"].unique().tolist()

        df_result = pd.DataFrame()

        for location in list_origins:

            df_new = df[df["LocationOrigin"]==location].copy()

            df_new["TransferLotSize_sum"] = df_new.groupby("Item")["TransferLotSize"].transform("sum")
            df_new["TransferLotSize_sum"] = np.ceil(df_new["TransferLotSize_sum"].round(2))
            list_items = df_new["Item"].unique()

            for i in list_items:

                indices = df_new[df_new["Item"]==i].index.tolist()
                df_filter = df_new.loc[indices].copy()
                df_filter.sort_values("priority", ascending=True, inplace=True)
                df_filter["TransferLotSizeRounded"] = df_filter["TransferLotSize"].apply(np.ceil)
                df_filter['cumulative'] = df_filter['TransferLotSizeRounded'].cumsum()

                df_filter['difference'] = df_filter['TransferLotSize_sum'] - df_filter['cumulative'].shift(1).fillna(0)

                df_filter['TransferLotSize'] = df_filter.apply(
                    lambda x: (
                        x['difference']
                        if x['difference'] >= 0 and x['cumulative'] > x['TransferLotSize_sum']
                        else (
                            0 if x['difference'] < 0
                            else x['TransferLotSizeRounded']
                        )
                    ),
                    axis=1
                )

                df_new.loc[indices, "TransferLotSize"] = df_filter.loc[indices, "TransferLotSize"]

            if df_result.empty:
                if not df_new.empty:
                    df_result = df_new.copy()

            elif not df_new.empty:
                df_result = pd.concat([df_result, df_new], ignore_index=True)

        df_result = df_result[df_result["TransferLotSize"]>0]

        return df_result
