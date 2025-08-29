import boto3
import numpy as np
import os
import pandas as pd

from pyod.models.lof import LOF
from datetime import datetime
from datupapi.configure.config import Config
from datupapi.extract.io import IO


class Anomaly():

    def __init__(self):
        DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
        self.io = IO(config_file=DOCKER_CONFIG_PATH, logfile='data_prepare', log_path='output/logs')
    

    @staticmethod
    def detectar_anomalias_prep(df, location=False,
                            prob_lim_general=85,
                            prob_lim_item=95,
                            limite_cambio_demanda=10,
                            limite_nan = 5
                            ):
        """
        Función para detectar anomalías y generar alertas en la preparación de nuevos clientes

        Parámetros obligatorios:
        - df: Dataframe a analizar. Debe incluir mínimo las columnas 'timestamp', 'item_id' y 'demand'.

        Parámetros opcionales:
        - location: Indica si existe la columna de location.
        - prob_lim_general: Límite de probabilidad para LOF general(default = 85%).
        - prob_lim_item: Límite de probabilidad para LOF por item (default = 95%).
        - limite_cambio_demanda: Límite para la alerta de cambio en la demanda (default = 10%).
        """

        # Preparar dataframe por total y por item
        df['demand'] = df['demand'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        demand_total = df[['timestamp','demand']]
        demand_total = demand_total.groupby('timestamp', as_index=False)['demand'].sum()

        demand_item = df[['timestamp','item_id','demand']]
        demand_item = demand_item.groupby(['timestamp', 'item_id'], as_index=False).agg({'demand': 'sum'}).sort_values(by='timestamp', ascending=False).reset_index(drop=True)
        demand_item = demand_item.reset_index()
        unique_items = demand_item['item_id'].unique()
        print('Unique items:',demand_item['item_id'].nunique())

        if location:
            print("Sección de análsis por item-loc en desarrollo")

        #1. LOF general ------
        demand_reshaped  = demand_total['demand'].values.reshape(-1, 1)
        lof = LOF(n_neighbors = 20, metric ="manhattan", novelty=True)
        lof.fit(demand_reshaped)
        #me quedo sólo con los datos anómalos
        probs = lof.predict_proba(demand_reshaped)
        is_out = probs[:,1] > (prob_lim_general/100)
        out = demand_total[is_out]

        #alerta
        alert_anomalies_total = True if not out.empty else False
        alert_anomalies_total_txt = (f"Anomalias en el total de la demanda: {out.shape[0]}.\nDetalles: \n{out}"
                                     if alert_anomalies_total else "")

        #2. LOF por item ------
        out_if_item2 = pd.DataFrame()
        lof2 = LOF(n_neighbors = 20, metric ="manhattan", novelty=True)

        alerta_max = 0
        alerta_media = 0
        items_alerta_max = []
        items_alerta_media = []

        for item_id in unique_items:
            # Filtrar el DataFrame para el ítem actual
            item_tmp = demand_item[demand_item['item_id'] == item_id]

            # Verificar si hay suficientes datos para el modelo LOF
            if 24 < len(item_tmp) <= 48:
                alerta_media = alerta_media +1
                items_alerta_media.append(item_id)

            if len(item_tmp) > 24:  # Asegurar que haya suficientes puntos para aplicar LOF
                # Aplicar LOF
                lof2.fit(item_tmp[['demand']])
                probs = lof2.predict_proba(item_tmp[['demand']])
                is_out = probs[:, 1] > (prob_lim_item/100)
                out2 = item_tmp[is_out]

                # Concatenar los outliers del ítem actual al DataFrame de resultados
                out_if_item2 = pd.concat([out_if_item2, out2[['item_id', 'timestamp', 'demand']]], ignore_index=True)

            else:
                alerta_max = alerta_max + 1
                items_alerta_max.append(item_id)

        out_if_item2 = out_if_item2.drop_duplicates()
        #alerta por anomalias
        alert_anomalies_item = True if not out_if_item2.empty else False
        alert_anomalies_item_txt = (f"Items con probabilidad de anomalía: {out_if_item2['item_id'].nunique()}. \nDetalles: \n{out_if_item2}"
                                    if alert_anomalies_item else "")

        #3. Alerta por items con poco histórico -------------------
        alert_insufficient_history = True if alerta_max > 0 or alerta_media > 0 else False
        alert_insufficient_history_txt = f"Items con menos de 24 meses en el histórico: {alerta_max}. ({', '.join(map(str, items_alerta_max))}). " if alerta_max > 0 else ""
        alert_insufficient_history_txt += f"Items con menos de 48 meses en el histórico: {alerta_media}. ({', '.join(map(str, items_alerta_media))})." if alerta_media > 0 else ""

        #4. Cambio drástico en la demanda total en comparación con el mes anterior --OJO ESTO DEBE IR DESPUÉS DEL RESAMPLE
        demand_actual = demand_total['demand'].iloc[-1]
        demand_ant = demand_total['demand'].iloc[-2]
        percentage_change = ((demand_actual - demand_ant) / demand_ant) * 100

        alert_demand_var = True if abs(percentage_change) > limite_cambio_demanda else False
        alert_demand_var_txt = f"Variación en la demanda total: {percentage_change:.2f}%." if alert_demand_var else ""
        print(f"Demanda tuvo un cambio del {percentage_change:.2f}% respecto al mes anterior.")

        #5. Columnas con información incompleta
        incomplete_columns = []
        for col in df.columns:
            missing_ratio = df[col].isna().mean()
            print(f"Columna '{col}' tiene un {missing_ratio:.2%} de valores faltantes.")
            if missing_ratio >= limite_nan:
                incomplete_columns.append((col, missing_ratio))

        if incomplete_columns:
            alert_incomplete_col = True
            column_details = [f"{col} ({missing_ratio:.2%})" for col, missing_ratio in incomplete_columns]
            alert_incomplete_col_txt = f"Columnas con más del {limite_nan * 100:.2f}% de información vacía: {', '.join(column_details)}."
        else:
            alert_incomplete_col = False
            alert_incomplete_col_txt = ""

        ## --------------------- MATRIZ DE ALERTAS ------------------------------

        alert_messages = [alert_anomalies_total_txt,
                        alert_anomalies_item_txt,
                        alert_insufficient_history_txt,
                        alert_demand_var_txt,
                        alert_incomplete_col_txt
                        ]

        alert_summary = '\n'.join(filter(None, alert_messages)) if any(alert_messages) else "Sin alertas"
        print(alert_summary)

        alert_matrix = pd.DataFrame({
            'Anomalias_Total_Demand': [alert_anomalies_total],
            'Anomalias_Item': [alert_anomalies_item],
            'Historico': [alert_insufficient_history],
            'Var_Demanda_Total': [alert_demand_var],
            'Info_Vacia': [alert_incomplete_col],
            'Alertas': [alert_summary]
        })

        return alert_matrix


    def detectar_anomalias_estable(
            self,
            prob_lim_general = 85,
            prob_lim_item = 95,
            limite_cambio_items = 20,
            limite_cambio_demanda = 10,
            limite_nan = 0.5,
            limite_cambio_demanda_item = 90,
            prob_lim_general_frcst = 85,
            prob_lim_item_frcst = 95,
            limite_precision = 40,
            limite_cambio_loc = 5,
            append_matrix = True
            ):
        """
        Función para detectar anomalías y generar alertas en clientes estables

        Parámetros opcionales:
        - prob_lim_general: Límite de probabilidad de anomalía con LOF para el historico general (default = 85%).
        - prob_lim_item: Límite de probabilidad de anomalía con LOF para el historico por item (default = 95%).
        - limite_cambio_items: Límite para la alerta de cambio en número de items (default = 20%).
        - limite_cambio_demanda: Límite para la alerta de cambio en la demanda (default = 10%).
        - limite_nan = Límite en porcentaje para alerta de información vacia en las columnas del prep (default = 0.5%)
        - limite_cambio_demanda_item = Límite en porcentanje para alerta por cambio de la demanda de un item entre el mes pasado y el actual (default = 90%)
        - prob_lim_general_frcst = Límite de probabilidad de anomalía con LOF para los pronósticos generales (default = 85%)
        - prob_lim_item_frcst = Límite de probabilidad de anomalía con LOF para los pronósticos por item (default = 95%)
        - limite_precision = Límite en porcentaje de accuracy para generar alerta por precisión baja (default = 40%)
        - limite_cambio_loc = Límite en cambio porcentual para alerta por cambios en el número de ubicaciones (default = 5%)
        """
        datalake_path_prep = self.io.dataset_import_path[0]
        datalake_path_forecast = self.io.results_path + '/Qmfcst/Qmfcst.csv'
        datalake_path_eff = self.io.results_path + '/Qeff/Qeff.csv'
        location = self.io.use_location

        print('Ruta prep',datalake_path_prep)
        print('Ruta forecast',datalake_path_forecast)
        print('Ruta eff',datalake_path_eff)
        print('Location:', location)

        # Descargar los datasets
        df_demand = self.io.download_object_csv(datalake_path=datalake_path_prep)
        df_forecast = self.io.download_object_csv(datalake_path=datalake_path_forecast)
        df_eff = self.io.download_object_csv(datalake_path=datalake_path_eff)

        # Preparar Qprep por total y por item
        df_demand['demand'] = df_demand['demand'].astype(float)
        df_demand['timestamp'] = pd.to_datetime(df_demand['timestamp'])

        demand_total = df_demand[['timestamp', 'demand']].groupby('timestamp').sum()

        demand_item = df_demand.groupby(['timestamp','item_id']).sum()
        demand_item = demand_item.reset_index()
        unique_items = demand_item['item_id'].unique()

        #------------------------------------ ALERTAS DEL QPREP ---------------------------------
        # 1. LOF general ------
        demand_reshaped = demand_total['demand'].values.reshape(-1, 1)
        lof = LOF(n_neighbors=20, metric="manhattan", novelty=True)
        lof.fit(demand_reshaped)

        # Me quedo sólo con los datos anómalos
        probs = lof.predict_proba(demand_reshaped)
        demand_total["probabilidad"] = probs[:, 1]  #
        demand_total['probabilidad'] = demand_total['probabilidad'].apply(lambda x: f"{round(x * 100, 1)}%")
        is_out = probs[:, 1] > (prob_lim_general/100)
        out = demand_total[is_out]

        # Alerta
        alert_anomalies_total = not out.empty
        alert_anomalies_total_txt = (f"Anomalias en el total de la demanda: {out.shape[0]}.\nDetalles: \n{out}"
                                    if alert_anomalies_total else "")

        # 2. LOF por item ------
        out_if_item2 = pd.DataFrame()
        lof2 = LOF(n_neighbors=20, metric="manhattan", novelty=True)

        alerta_max = 0
        alerta_media = 0
        items_alerta_max = []
        items_alerta_media = []

        for item_id in unique_items:
            # Filtrar el DataFrame para el ítem actual
            item_tmp = demand_item[demand_item['item_id'] == item_id]

            # Verificar si hay suficientes datos para el modelo LOF
            if 24 < len(item_tmp) <= 48:
                alerta_media += 1
                items_alerta_media.append(item_id)

            if len(item_tmp) > 24:  # Asegurar que haya suficientes puntos para aplicar LOF
                # Aplicar LOF
                lof2.fit(item_tmp[['demand']])
                probs = lof2.predict_proba(item_tmp[['demand']])
                item_tmp = item_tmp.copy()
                item_tmp.loc[:, "probabilidad"] = probs[:, 1]
                is_out2 = probs[:, 1] > (prob_lim_item/100)
                out2 = item_tmp[is_out2]

                # Concatenar los outliers del ítem actual al DataFrame de resultados
                out_if_item2 = pd.concat([out_if_item2, out2[['item_id', 'timestamp', 'demand', 'probabilidad']]], ignore_index=True)

            else:
                alerta_max += 1
                items_alerta_max.append(item_id)

        out_if_item2 = out_if_item2.drop_duplicates()

        # Alerta por anomalías
        alert_anomalies_item = not out_if_item2.empty
        alert_anomalies_item_txt = (f"Items con probabilidad de anomalía: {out_if_item2['item_id'].nunique()}. \nDetalles: \n{out_if_item2}"
                                    if alert_anomalies_item else "")

        # 3. Alerta por items con poco histórico -------------------
        items_alerta_max = np.array(items_alerta_max).astype(str)
        items_alerta_media = np.array(items_alerta_media).astype(str)

        alert_insufficient_history = alerta_max > 0 or alerta_media > 0
        alert_insufficient_history_txt = (
            f"Items con menos de 24 meses en el histórico: {alerta_max}. ({', '.join(map(str, items_alerta_max))}). "
            if alerta_max > 0 else "")
        alert_insufficient_history_txt += (
            f"Items con menos de 48 meses en el histórico: {alerta_media}. ({', '.join(map(str, items_alerta_media))})."
            if alerta_media > 0 else "")

        # 4. Cambio drástico en la demanda total en comparación con el mes anterior --------------
        demand_actual = demand_total['demand'].iloc[-1]
        demand_ant = demand_total['demand'].iloc[-2]
        percentage_change = ((demand_actual - demand_ant) / demand_ant) * 100

        alert_demand_var = abs(percentage_change) > limite_cambio_demanda
        alert_demand_var_txt = f"Variación en la demanda total: {percentage_change:.2f}%." if alert_demand_var else ""
        print(f"Demanda tuvo un cambio del {percentage_change:.2f}% respecto al mes anterior.")

        ## 5. Cambio drástico en la demanda por items en comparación con el mes anterior -----------
        df_demand['timestamp'] = pd.to_datetime(df_demand['timestamp'])
        df_demand['item_id'] = df_demand['item_id'].astype(str)

        #Filtro sólo los últimos dos meses y los organizo por item y fecha para que quede cada item con sus dos fechas seguidas
        cambio_demand = df_demand[df_demand['timestamp'].isin([df_demand['timestamp'].max(), df_demand['timestamp'].max() - pd.DateOffset(months=1)])]
        cambio_demand = cambio_demand.groupby(['item_id', 'timestamp'])['demand'].sum().reset_index().sort_values(by=['item_id','timestamp'], ascending=True)
        cambio_demand['month_prev_demand'] = cambio_demand.groupby('item_id')['demand'].shift(1)
        cambio_demand['month_delta_demand'] = (cambio_demand['demand'] - cambio_demand['month_prev_demand'])/cambio_demand['month_prev_demand']*100
        cambio_demand = cambio_demand.replace([np.inf, -np.inf], 100)
        cambio_demand = cambio_demand.fillna(0)
        cambio_demand = cambio_demand[cambio_demand['timestamp'] == cambio_demand['timestamp'].max()]

        # #Alerta
        cambio_demand_alert = cambio_demand[abs(cambio_demand['month_delta_demand'])>limite_cambio_demanda_item]
        items_alerta = cambio_demand_alert['item_id'].nunique()
        alert_demand_item_var = True if cambio_demand_alert['month_delta_demand'].sum() > 0 else False
        alert_demand_item_var_txt = (f"Hay {items_alerta} items con una variación en su demanda mayor al {limite_cambio_demanda_item}%.\nDetalles: {cambio_demand_alert.item_id.unique()}"
                                      if alert_demand_item_var else "")
        print(f'{alert_demand_item_var_txt}')


        # 6. Columnas con información incompleta ---------
        incomplete_columns = []
        for col in df_demand.columns:
            missing_ratio = df_demand[col].isna().mean()
            print(f"Columna '{col}' tiene un {missing_ratio:.2%} de valores faltantes.")
            if missing_ratio >= limite_nan:
                incomplete_columns.append((col, missing_ratio))

        if incomplete_columns:
            alert_incomplete_col = True
            column_details = [f"{col} ({missing_ratio:.2%})" for col, missing_ratio in incomplete_columns]
            alert_incomplete_col_txt = (
                f"Columnas con más del {limite_nan * 100:.2f}% de información vacía: {', '.join(column_details)}."
            )
        else:
            alert_incomplete_col = False
            alert_incomplete_col_txt = ""


        #-------------------------------------- ALERTAS DE MULTIFORECAST --------------------------------------------
        df_forecast = df_forecast[['Date','Item','Target','SuggestedForecast', 'Ranking']]
        df_forecast['Date'] = pd.to_datetime(df_forecast['Date'])
        total_mfrcst = df_forecast.groupby('Date').sum()
        total_mfrcst = total_mfrcst.drop(columns=['Item'])

        item_mfrcst = df_forecast.groupby(['Date','Item']).sum()
        item_mfrcst = item_mfrcst.reset_index()
        unique_items = item_mfrcst['Item'].unique()

        print('Items únicos en multiforecast: ',item_mfrcst['Item'].nunique())
        FechaHorizonte = df_forecast['Date'].max()
        print('Fecha de Horizonte: ',FechaHorizonte)

        ## 7. LOF para multiforecast general ------------
        forecast_reshaped  = total_mfrcst['SuggestedForecast'].values.reshape(-1, 1)

        #novelty=True permite utilizar el método predict_proba para obtener las probabilidades de cada punto.
        lof_f = LOF(n_neighbors=20, metric="manhattan", novelty=True)
        lof_f.fit(forecast_reshaped)

        ##imprime los labels: 0 para normal, 1 para atípico
        print(lof_f.labels_)

        #me quedo sólo con los datos anómalos
        probs = lof_f.predict_proba(forecast_reshaped)
        total_mfrcst["probabilidad"] = probs[:, 1] ##Agrego la probabilidad de anomalía para cada periodo
        total_mfrcst["probabilidad"] = total_mfrcst['probabilidad'].apply(lambda x: f"{round(x * 100, 1)}%")
        is_out3 = probs[:,1] > (prob_lim_general_frcst/100)
        out3 = total_mfrcst[is_out3]
        out3 = out3.drop(columns=['Ranking'])

        # Alerta
        alert_anomalies_frcst_total = not out.empty
        alert_anomalies_frcst_total_txt = (f"Anomalias en los pronósticos totales: {out3.shape[0]}.\nDetalles: \n{out3}" if alert_anomalies_frcst_total else "")
        print(alert_anomalies_frcst_total_txt)

        ## 8. LOF para multiforecast POR ITEM ---------------
        out_if_item4 = pd.DataFrame()
        lof4 = LOF(n_neighbors = 20, metric ="manhattan")

        for item_id in unique_items:
            # Filtrar el DataFrame para el ítem actual
            item_tmp = item_mfrcst[item_mfrcst['Item'] == item_id]

            # Aplicar LOF
            lof4.fit(item_tmp[['SuggestedForecast', 'Target']])
            probs = lof4.predict_proba(item_tmp[['SuggestedForecast', 'Target']])
            # item_tmp["probabilidad"] = probs[:, 1]  #Agregando probabilidad de anomalía a los items
            item_tmp = item_tmp.copy()
            item_tmp.loc[:, "probabilidad"] = probs[:, 1]
            is_out4 = probs[:, 1] > (prob_lim_item_frcst/100)
            out4 = item_tmp[is_out4]

            # Concatenar los outliers del ítem actual al DataFrame de resultados
            out_if_item4 = pd.concat([out_if_item4, out4[['Date', 'Item', 'SuggestedForecast', 'Target', 'Ranking', 'probabilidad']]], ignore_index=True)

            #Filtrar solo las fechas en donde target = 0
            out_if_item4 = out_if_item4[out_if_item4['Target'] == 0]


        # Mostrar el DataFrame con todos los outliers encontrados
        out_if_item4 = out_if_item4.drop_duplicates()
        print(f'Número de items con probabilidad mayor a {prob_lim_item_frcst} de anomalía: {out_if_item4.Item.nunique()}')

        # Alerta por anomalías
        alert_anomalies_frcst_item = not out_if_item4.empty
        alert_anomalies_frcst_item_txt = (f"Items con probabilidad mayor a {prob_lim_item_frcst}% de anomalía en los pronósticos: {out_if_item4['Item'].nunique()}. \nDetalles: \n{out_if_item4}"
                                          if alert_anomalies_frcst_item else "")

        #-------------------------------------------------- ALERTAS DE EFFICIENCIA --------------------------------------
        df_eff['Item'] = df_eff['Item'].astype(str)
        print(df_eff['Item'].nunique())
        if location:
          df_eff =df_eff[['Date', 'Item', 'Location', 'Ranking', 'Target', 'SuggestedForecast', 'NextSuggestedForecast',
                'BackSuggestedForecast', 'AccuracySuggForecast', 'AccuracyNextForecast', 'AccuracyBackForecast',
                'ItemType', 'AccuracyBestFit', 'IntervalBestFit']]
          df_eff['itemloc'] = df_eff['Item'] + '-' + df_eff['Location']
        else:
          df_eff =df_eff[['Date', 'Item', 'Ranking', 'Target', 'SuggestedForecast', 'NextSuggestedForecast',
                'BackSuggestedForecast', 'AccuracySuggForecast', 'AccuracyNextForecast', 'AccuracyBackForecast',
                'ItemType', 'AccuracyBestFit', 'IntervalBestFit']]

        ##9. items con baja precisión
        items_baja_precision = df_eff[df_eff['Date']==df_eff['Date'].max()]
        items_baja_precision = items_baja_precision[items_baja_precision['AccuracyBestFit']<limite_precision]
        num_items_baja_precision = items_baja_precision['Item'].nunique()

        ##Conteo de baja precisión por tipo de impacto
        items_baja_precision_alto = items_baja_precision[(items_baja_precision['ItemType']=='Items Alto Impacto')]
        items_baja_precision_medio = items_baja_precision[(items_baja_precision['ItemType']=='Items Impacto Moderado')]
        items_baja_precision_bajo = items_baja_precision[(items_baja_precision['ItemType']=='Items Bajo Impacto')]

        #Alerta
        alert_precision = True if num_items_baja_precision > 0 else False

        if location:
          alert_precision_txt = (f"Hay {items_baja_precision.shape[0]} combinaciones con precisión menor al {limite_precision}% en el mes de corte.\n{items_baja_precision_alto.shape[0]} son combinaciones de alto impacto: {items_baja_precision_alto.itemloc.unique()}\n{items_baja_precision_medio.shape[0]} son combinaciones de impacto moderado: {items_baja_precision_medio.itemloc.unique()}\n{items_baja_precision_bajo.shape[0]} son combinaciones de bajo impacto: {items_baja_precision_bajo.itemloc.unique()}"
                                if alert_precision else "")
        else:
          alert_precision_txt = (f"Hay {items_baja_precision.shape[0]} items con precisión menor al {limite_precision}% en el mes de corte.\n{items_baja_precision_alto.shape[0]} son items de alto impacto: {items_baja_precision_alto.Item.unique()}\n{items_baja_precision_medio.shape[0]} son items de impacto moderado: {items_baja_precision_medio.Item.unique()}\n{items_baja_precision_bajo.shape[0]} son items de bajo impacto: {items_baja_precision_bajo.Item.unique()}"
                                if alert_precision else "")
        print(alert_precision_txt)

        #------------------------------------------------- ALERTAS DE LOGS ----------------------------------------------------
        sql = f"SELECT * FROM `datup-supplyai-dev.infodatupprocess.TblLogsForecasting` WHERE Project LIKE '{self.io.tenant_id}'"
        gcp_forecast = self.io.download_bigquery_table(project_id='datup-supplyai-dev' ,
                                                tenant_id='infodatupprocess',
                                                table_name='TblLogsForecasting',
                                                sqlQuery=sql,
                                                gcp_key='datup-supplyai-dev-gcp.json')

        gcp_forecast = gcp_forecast.sort_values(by=['Date', 'Time'], ascending=[True, True])
        gcp_forecast['Date'] = pd.to_datetime(gcp_forecast['Date'])

        log_forecast = gcp_forecast.groupby(gcp_forecast['Date'].dt.to_period('M')).tail(1).reset_index(drop=True)
        drop_columns = ['Time', 'Customer', 'Type', 'SeasonalType', 'TrendType', 'ResidualType', 'ForecastNaive', 'AvgResidual',
                        'ForecastLo95', 'ForecastLo80', 'ForecastLo60','ForecastPoint','ForecastUp60','ForecastUp80','ForecastUp95',
                        'MASE', 'SuggestedForecastSales','NextSuggestedForecastSales','BackSuggestedForecastSales']
        log_forecast = log_forecast.drop(columns=drop_columns)
        print(f'Logs descargados y recortados a {log_forecast.shape[0]} ejecuciones.')

        if log_forecast.shape[0] < 2:
          print('Logs insuficientes. Las alertas dependientes de logs pasarán a estado nulo')

        #10. Cambios en el número total de items ----------------------
        if log_forecast.shape[0] > 1:
          num_actual_items = demand_item['item_id'].nunique()
          num_ant_items = log_forecast['Items'].iloc[-2]
          cambio_num_items = ((num_actual_items - num_ant_items) / num_ant_items) * 100

          #Alerta
          alert_items_var = True if abs(cambio_num_items) > 10 else False
          alert_items_var_txt = f"Variación en items: {cambio_num_items:.2f}%." if alert_items_var else ""
          print(f"El número de ítems únicos ha cambiado en un {cambio_num_items:.2f}%.")

        else:
          alert_items_var = False
          alert_items_var_txt = 'Nulo'

        #11. Cambios en el número total de ubicaciones  -------------- DE UBICACIÓN
        if log_forecast.shape[0] > 1:
          if location:
              num_actual_loc = df_demand['location'].nunique()
              num_ant_loc = log_forecast['Locations'].iloc[-2]
              cambio_num_loc = ((num_actual_loc - num_ant_loc) / num_ant_loc) * 100
          else:
              cambio_num_loc = 0

          #Alerta
          alert_loc_var = True if abs(cambio_num_loc) > limite_cambio_loc else False
          alert_loc_var_txt = f"Variación en ubicaciones: {cambio_num_loc:.2f}%." if alert_loc_var else ""
          print(f"El número de ubicaciones únicos ha cambiado en un {cambio_num_loc:.2f}%.")

        else:
          alert_loc_var = False
          alert_loc_var_txt = 'Nulo'

        ##12. Aumento en el WMAPE
        if log_forecast.shape[0] > 1:
          wmape_actual = log_forecast['WMAPE'].iloc[-1]
          wmape_anterior = log_forecast['WMAPE'].iloc[-2]

          #Alerta
          alert_wmape_var = True if  wmape_anterior < wmape_actual else False
          alert_wmape_var_txt = ((f"El error promedio aumentó de {wmape_anterior:.2f}% a {wmape_actual:.2f}%") if alert_wmape_var
                                else (f"El error promedio disminuyó de {wmape_anterior:.2f}% a {wmape_actual:.2f}%"))
          print(f"El error pasó de {wmape_anterior:.2f}% a {wmape_actual:.2f}%")
          print(alert_wmape_var_txt)

        else:
          alert_wmape_var = False
          alert_wmape_var_txt = 'Nulo'

        ##13. Fecha de corte
        fecha_corte = log_forecast['DateDataPrep'].iloc[-1]
        fecha_ejecucion = pd.Timestamp.now().date()
        fecha_ejecucion_mod = fecha_ejecucion.strftime('%Y-%m') + '-01'
        fecha_ejecucion_mod = datetime.strptime(fecha_ejecucion_mod, '%Y-%m-%d').date()

        ##Confirmar que fecha_corte es un dia antes que la fecha de ejecucion
        alert_fecha = False if fecha_corte == fecha_ejecucion_mod - pd.Timedelta(days=1) else True
        alert_fecha_txt = (f'La fecha de corte {fecha_corte} es incorrecta') if alert_fecha else (f"{fecha_corte}")
        print(alert_fecha_txt)

        #####--------------------Creción tabla resumen


        if location:
          # Creo tabla para lo items con baja precisión
          tabla = items_baja_precision[['Item', 'Location','ItemType', 'Ranking', 'AccuracyBestFit']]

          # Agrego su variación respecto al mes pasado
          tabla = tabla.copy()
          tabla.loc[:, 'VariacionUltimoMes'] = tabla['Item'].map(cambio_demand.set_index('item_id')['month_delta_demand'])

          #Agrego el histórico
          tabla['Item'] = tabla['Item'].astype(str)
          df_demand['item_id'] = df_demand['item_id'].astype(str)
          tabla['Location'] = tabla['Location'].astype(str)
          df_demand['location'] = df_demand['location'].astype(str)

          historico_meses = df_demand.groupby(['item_id', 'location']).size().reset_index(name='Historico (Meses)')
          tabla = tabla.merge(historico_meses, left_on=['Item', 'Location'], right_on=['item_id', 'location'], how='left')
          tabla.drop(columns=['item_id', 'location'], inplace=True, errors='ignore')
          tabla['Historico (Meses)'] = tabla.set_index(['Item', 'Location']).index.map(df_demand.groupby(['item_id', 'location']).size())

        else:
          # Creo tabla para lo items con baja precisión
          tabla = items_baja_precision[['Item','ItemType', 'Ranking', 'AccuracyBestFit']]

          # Agrego su variación respecto al mes pasado
          tabla = tabla.copy()
          tabla.loc[:, 'VariacionUltimoMes'] = tabla['Item'].map(cambio_demand.set_index('item_id')['month_delta_demand'])

          #Agrego el histórico
          tabla['Item'] = tabla['Item'].astype(str)
          df_demand['item_id'] = df_demand['item_id'].astype(str)

          historico_meses = df_demand.groupby(['item_id']).size().reset_index(name='Historico (Meses)')
          tabla = tabla.merge(historico_meses, left_on=['Item'], right_on=['item_id'], how='left')
          tabla.drop(columns=['item_id'], inplace=True, errors='ignore')
          tabla['Historico (Meses)'] = tabla.set_index(['Item']).index.map(df_demand.groupby(['item_id']).size())


        #Añadir alertas LOF
        out_if_item2['item_id'] = out_if_item2['item_id'].astype(str)
        out_if_item4['Item'] = out_if_item4['Item'].astype(str)

        def obtener_alerta(item):

            item = str(item)

            # Filtrar por item
            alerta_prep = out_if_item2[out_if_item2['item_id'] == item][['timestamp', 'probabilidad']].copy()
            alerta_forecast = out_if_item4[out_if_item4['Item'] == item][['Date', 'probabilidad']].copy()

            # Unificar nombres de columnas
            alerta_prep = alerta_prep.rename(columns={'item_id': 'Item'})
            alerta_forecast = alerta_forecast.rename(columns={'Date': 'timestamp'})

            # Convertir 'Item' a string para evitar inconsistencias
            alerta_prep['Item'] = str(item)
            alerta_forecast['Item'] = str(item)

            # Concatenar
            alertas = pd.concat([alerta_prep, alerta_forecast], ignore_index=True)

            return alertas.to_dict(orient='records') if not alertas.empty else None

        tabla['AlertaAnomalia'] = tabla['Item'].apply(obtener_alerta)
        items_con_alerta = set(out_if_item2['item_id']).union(set(out_if_item4['Item']))
        print(f'Items con baja precisión con alertas de anomalías: {items_con_alerta}')

        #---------------------Cargando tabla resumen
        self.io.upload_csv(tabla, q_name='ResumenAlertas', datalake_path='output')
        print('Tabla resumen de alertas creada y cargada en S3')

        ## --------------------- MATRIZ DE ALERTAS ------------------------------

        alert_matrix = pd.DataFrame({
            'FechaEjecucion': [pd.Timestamp.now().date()],
            'FechaCorte': [alert_fecha_txt],
            'FechaHorizonte': [FechaHorizonte],
            'AnomaliasPrepTotal': [alert_anomalies_total_txt],
            'AnomaliasPrepItem': [alert_anomalies_item_txt],
            'HistoricoCorto': [alert_insufficient_history_txt],
            'VarDemandaTotal': [alert_demand_var_txt],
            'VarDemanda_Item': [alert_demand_item_var_txt],
            'ColumnasVacias': [alert_incomplete_col_txt],
            'AnomaliasForecastTotal': [alert_anomalies_frcst_total_txt],
            'AnomaliasForecastItem': [alert_anomalies_frcst_item_txt],
            'PrecisionBaja': [alert_precision_txt],
            'Var_Items': [alert_items_var_txt],
            'Var_Loc': [alert_loc_var_txt],
            'WMAPE': [alert_wmape_var_txt],
        })

        print('Matriz de la ejecuón creada. Calculando número total de alertas....')

        ####-------------------------CONCATENACIÓN Y CARGA DE LA MATRIZ

        if append_matrix:
            self.io.populate_bigquery_table(alert_matrix, project_id='datup-supplyai-dev', tenant_id=self.io.tenant_id, table_name='TblAlerts', write_mode='append')
            old_matrix = self.io.download_object_csv(datalake_path='output/Alertas/Alertas.csv')
            old_matrix = pd.DataFrame(columns=alert_matrix.columns)
            new_matrix = pd.concat([old_matrix, alert_matrix])
            self.io.upload_csv(new_matrix, q_name='Alertas', datalake_path='output')
            print('Matriz de alertas anexada y cargada en BigQuery y S3')
            return new_matrix

        else:
            self.io.populate_bigquery_table(alert_matrix, project_id='datup-supplyai-dev', tenant_id=self.io.tenant_id, table_name='TblAlerts', write_mode='overwrite')
            self.io.upload_csv(alert_matrix, q_name='Alertas', datalake_path='output')
            print('Matriz de alertas creada y cargada en BigQuery y S3')
            return alert_matrix

anomalia = Anomaly() 