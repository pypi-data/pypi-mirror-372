import pandas as pd
import calendar
from dateutil.relativedelta import relativedelta


class DailyUsageFuture():

    def __init__(self, location, column_forecast, date, df_fcst):
        self.location = location
        self.column_forecast = column_forecast
        self.date = date
        self.df_fcst = df_fcst

    def get_columns(self):

        """Return two lists: columns_filter and columns_group"""
        columns_data = ["Date", "Item", "Location", "Target"]
        if self.location:
            columns_filter = columns_data
            columns_filter.append(self.column_forecast)
            columns_group = ["Item", "Location"]
        else:
            columns_filter = columns_data
            columns_filter.remove("Location")
            columns_filter.append(self.column_forecast)
            columns_group = ["Item"]

        return columns_group, columns_filter


    def get_date(self):

        actual_date = self.date[0:8]
        actual_date = pd.to_datetime(str(int(float(actual_date))), format='%Y%m%d')

        year = actual_date.year
        month = actual_date.month
        total_days = calendar.monthrange(year, month)[1]

        return actual_date, total_days


    def calculate_daily(self, df: pd.DataFrame, type_daily: str):

        """Calculate the daily usage depending on type of daily usage. Return a DataFrame"""
        _, total_days = self.get_date()
        columns_group, _ = self.get_columns()

        if type_daily == "AvgDailyUsage":
            df_avg = df.groupby(columns_group, as_index=False).agg({type_daily: "mean"}).reset_index(drop=True)
            df_avg[type_daily] = df_avg[type_daily] / total_days

        elif type_daily == "MaxDailyUsage":
            df_avg = df.groupby(columns_group, as_index=False).agg({type_daily: "max"}).reset_index(drop=True)
            df_avg[type_daily] = df_avg[type_daily] / total_days

        return df_avg


    def processing(self, df_avg, df_inv_suggested, type_daily: str):

        columns_group, columns_filter = self.get_columns()
        # Create explicit copy to avoid SettingWithCopyWarning
        df_avg = df_avg[columns_filter].copy()
        df_avg[type_daily] = df_avg.apply(lambda x: x[self.column_forecast] if (x["Target"]==0) else x["Target"], axis=1)
        df_avg = self.calculate_daily(df_avg, type_daily)
        df_avg.loc[:, columns_group] = df_avg.loc[:, columns_group].astype(str)
        df_inv_suggested.loc[:, columns_group] = df_inv_suggested.loc[:, columns_group].astype(str)
        columns_merge = columns_group + [type_daily]
        df_daily_usage = pd.merge(df_inv_suggested, df_avg[columns_merge], on=columns_group, how="left")

        return df_daily_usage


    def daily_usage(self, df_inv_suggested, type_daily: str):

        actual_date, _ = self.get_date()

        if type_daily in ["AvgDailyUsage", "MaxDailyUsage"]:

            min_date = (actual_date + relativedelta(day=31))
            max_date = (min_date + relativedelta(months=3)).replace(day=1) + relativedelta(day=31)
            date_min = min_date.strftime("%Y-%m-%d")
            date_max = max_date.strftime("%Y-%m-%d")

            df_avg = self.df_fcst[(self.df_fcst["Date"] >= date_min) & (self.df_fcst["Date"] <= date_max)]
            df_daily = self.processing(df_avg, df_inv_suggested, type_daily)
        else:
            print('No column found')

        df_daily[type_daily] = round(df_daily[type_daily], 3)

        return df_daily