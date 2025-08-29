import base64
from typing import Dict, List
import boto3
import json
import os
import pandas as pd
import requests
#import snowflake.connector
import time
from boto3.dynamodb.conditions import Key, Attr
from boto3.session import Session
from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import datetime
from datupapi.configure.config import Config
from google.cloud import bigquery
from google.oauth2 import service_account
import google
from hashlib import md5
#from snowflake.connector.pandas_tools import write_pandas, pd_writer
#from snowflake.sqlalchemy import URL
from hdbcli import dbapi
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy import Integer, Float, String, DECIMAL
from sqlalchemy import insert, delete, exists, schema, text
from concurrent.futures import ThreadPoolExecutor #para cargar en paralelo a GCP
from threading import current_thread


class IO(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path

    def get_secret(self, secret_name=None):
        """
        Return the credentials mapped to the entered secret name

        :param secret_name: Name identifying the credentials in AWS.
        :return response: Credential to authenticate against AWS resource

        >>> creds = get_secret()
        >>> creds = ...
        """
        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager',
                                region_name=self.region,
                                aws_access_key_id=self.access_key,
                                aws_secret_access_key=self.secret_key)
        try:
            if secret_name is not None:
                get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            else:
                get_secret_value_response = client.get_secret_value(SecretId=self.sql_database + 'secret')
        except ClientError as e:
            if e.response['Error']['Code'] == 'DecryptionFailureException':
                # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                # An error occurred on the server side.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                # You provided an invalid value for a parameter.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                # You provided a parameter value that is not valid for the current state of the resource.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
            elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                # We can't find the resource that you asked for.
                # Deal with the exception here, and/or rethrow at your discretion.
                raise e
        else:
            # Decrypts secret using the associated KMS CMK.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
        return json.loads(get_secret_value_response['SecretString'])

    def populate_snowflake_table(self,
                                 df,
                                 dwh_account=None,
                                 dwh_name=None,
                                 dwh_user=None,
                                 dwh_passwd=None,
                                 dwh_dbname=None,
                                 dwh_schema=None,
                                 table_name=None,
                                 replace=True):
        """
         Create a table in Snowflake DWH and insert the records from a dataframe

        :param df: Dataframe storing the records to insert into the database table
        :param dwh_account: Snowflake account identifier
        :param dwh_name: Snowflake datawarehouse name
        :param dwh_user: Snowflake account username
        :param dwh_passwd: Snowflake account password
        :param db_name: Snowflake database name
        :param dwh_schema: Snowflake database schema
        :param table_name: Snowflake table name
        :param replace: If True replace table records whether exists. Otherwise append records. Default True.
        :return inserted_records: Number of records inserted

        >>> records = populate_snowflake_table(df, dwh_account='xx12345.us-east-1', dwh_name='myDwh', dwh_user='myuser', dwh_passwd='12345', dwh_dbname='mydbname', dwh_schema='myschema', table_name='mytable')
        >>> records = 1000
        """
        if self.tenant_id != '':
            tenant_table_name = (self.tenant_id + table_name)
        else:
            tenant_table_name = table_name

        url = URL(account=dwh_account, user=dwh_user, password=dwh_passwd, warehouse=dwh_name, database=dwh_dbname, schema=dwh_schema)
        try:
            engine = create_engine(url)
            conn = engine.connect()
            if replace:
                df.to_sql(tenant_table_name, con=engine, if_exists='replace', index=False, chunksize=16000)
            else:
                df.to_sql(tenant_table_name, con=engine, if_exists='append', index=False, chunksize=16000)
            inserted_records = conn.execute('select count(*) from ' + '"' + tenant_table_name + '"').fetchone()[0]
        finally:
            conn.close()
            engine.dispose()
        return inserted_records

    def populate_bigquery_table(self, df, project_id=None, tenant_id=None, table_name=None, write_mode='overwrite', gcp_key='datup-supplyai-dev-gcp.json'):
        """
        Create a table in BigQuery DWH and insert the records from a dataframe
        :param df: Dataframe storing the records to insert into the database table
        :param projectId: Project identifier in GCP
        :param tenantId: Tenant or customer identifier
        :param table_name: BigQuery table name
        :param write_mode: BigQuery table update method. Either overwrite or append
        :param gcp_key: BigQuery credential key
        :return: Number of records inserted

        >>> records = populate_bigquery_table(df, project_id='myproject', tenant_id='acme', table_name='mytable')
        >>> records = 1000
        """
        key = service_account.Credentials.from_service_account_file(os.path.join('/opt/ml/processing/input', gcp_key))
        client = bigquery.Client(credentials=key)

        try:
            if write_mode == 'overwrite':
                write_mode_ = 'WRITE_TRUNCATE'
            elif write_mode == 'append':
                write_mode_ = 'WRITE_APPEND'
            else:
                self.logger.exception(f'No valid BigQuery write mode. Please check valid types: overwrite or append')
            table_id = project_id + '.' + tenant_id + '.' + table_name
            job_config = bigquery.LoadJobConfig(autodetect=False,
                                                source_format=bigquery.SourceFormat.CSV,
                                                allow_quoted_newlines=True,
                                                write_disposition=write_mode_)
            #client.delete_table(table_id, not_found_ok=True)
            load_job = client.load_table_from_dataframe(dataframe=df, destination=table_id, job_config=job_config)
            load_job.result()
            destination_table = client.get_table(table_id)
        except google.api_core.exceptions.NotFound as err:
            raise
        return destination_table.num_rows

    def populate_bigquery_table_with_schema(self, df, project_id=None, tenant_id=None, table_name=None, write_mode='overwrite', gcp_key='datup-supplyai-dev-gcp.json'):
        """
        Create a table in BigQuery DWH and insert the records from a dataframe
        :param df: Dataframe storing the records to insert into the database table
        :param projectId: Project identifier in GCP
        :param tenantId: Tenant or customer identifier
        :param table_name: BigQuery table name
        :return: Number of records inserted

        >>> records = populate_bigquery_table_with_schema(df, project_id='myproject', tenant_id='acme', table_name='mytable')
        >>> records = 1000
        """
        key = service_account.Credentials.from_service_account_file(os.path.join('/opt/ml/processing/input', gcp_key))
        client = bigquery.Client(credentials=key)

        try:
            if write_mode == 'overwrite':
                write_mode_ = 'WRITE_TRUNCATE'
            elif write_mode == 'append':
                write_mode_ = 'WRITE_APPEND'
            else:
                self.logger.exception(f'No valid BigQuery write mode. Please check valid types: overwrite or append')

            # Build schema dynamically
            df_schema = []
            date_cols = list(df.select_dtypes(include=['datetime64']).columns)
            string_cols = list(df.select_dtypes(include=['object']).columns)
            integer_cols = list(df.select_dtypes(include=['int64']).columns)
            float_cols = list(df.select_dtypes(include=['float64']).columns)
            [df_schema.append(bigquery.SchemaField(col, bigquery.enums.SqlTypeNames.DATE)) for col in date_cols]
            [df_schema.append(bigquery.SchemaField(col, bigquery.enums.SqlTypeNames.INT64)) for col in integer_cols]
            [df_schema.append(bigquery.SchemaField(col, bigquery.enums.SqlTypeNames.FLOAT64)) for col in float_cols]
            [df_schema.append(bigquery.SchemaField(col, bigquery.enums.SqlTypeNames.STRING)) for col in string_cols]
            #Load pandas dataframe into BigQuery table
            table_id = project_id + '.' + tenant_id + '.' + table_name
            job_config = bigquery.LoadJobConfig(autodetect=False,
                                                schema=df_schema,
                                                write_disposition=write_mode_)
            load_job = client.load_table_from_dataframe(dataframe=df, destination=table_id, job_config=job_config)
            load_job.result()
            destination_table = client.get_table(table_id)
        except google.api_core.exceptions.NotFound as err:
            raise
        return destination_table.num_rows
        
    def get_secret_for_bigquery(self,secretname=None):
        """
        Get the secret from AWS and return a json with the keys for
        made a query in Google BigQuery
        :param secretname: Name of the AWS secret
        """
        json = {
            "type":self.get_secret(secret_name=secretname)['type'],
            "project_id":self.get_secret(secret_name=secretname)['project_id'],
            "private_key_id":self.get_secret(secret_name=secretname)['private_key_id'],
            "private_key":self.get_secret(secret_name=secretname)['private_key'],
            "client_email":self.get_secret(secret_name=secretname)['client_email'],
            "client_id":self.get_secret(secret_name=secretname)['client_id'],
            "auth_uri":self.get_secret(secret_name=secretname)['auth_uri'],
            "token_uri":self.get_secret(secret_name=secretname)['token_uri'],
            "auth_provider_x509_cert_url":self.get_secret(secret_name=secretname)['auth_provider_x509_cert_url'],
            "client_x509_cert_url":self.get_secret(secret_name=secretname)['client_x509_cert_url'],
            "universe_domain":self.get_secret(secret_name=secretname)['universe_domain']
        }

        json['private_key']=json['private_key'].replace("\\n", "\n")

        return json
    
    def describe_bigquery_table(self, aws_secret=None, gcp_key=None) -> Dict[str, List[str]]:
        """
        Describe a table in BigQuery shows its data sets and tables contained.
        :return: Project, datasets and tables.

        >>> description = describe()
        >>> descripton = ...
        """
        try:
            if aws_secret==None:
                print("Using json file")
                key = service_account.Credentials.from_service_account_file(os.path.join('/opt/ml/processing/input', gcp_key))
            else:
                print("Using aws secret")
                key = service_account.Credentials.from_service_account_info(self.get_secret_for_bigquery(aws_secret))
            
            client = bigquery.Client(credentials=key)
            print('Proyecto: ', client.project)
            datasets = client.list_datasets()
            table_client: List[str] = []
            component_client: Dict[str, List[str]] = {}
            for dataset in datasets:
                print('\nDataset: ',dataset.reference ,'\nTablas:')
                tables = client.list_tables(dataset.reference)
                for table in tables:
                    print(' ',table.table_id)
                    table_client.append(table.table_id)
                component_client[dataset.reference] = table_client

            client.close()
        except Exception as e:
            print(f"Falla la consulta en base de datos big query: {e}")
            raise
        else:
            return component_client
        
    def download_bigquery_table(self,
                                project_id=None, 
                                tenant_id=None, 
                                table_name=None, 
                                aws_secret=None, 
                                gcp_key=None, 
                                sqlQuery=None):
        """
        Download a query from a data set in BigQuery.

        :param projectId: Project identifier in GCP
        :param tenantId: Tenant or customer identifier
        :param table_name: BigQuery table name
        :param aw_secret: Name of the AWS secret
        :param query: SQl query.
        :return: Dataframe from query.

        >>> records = populate_dbtable(df, hostname='202.10.0.1', db_user='johndoe', db_passwd='123456', db_name='dbo.TheDataBase')
        >>> records = 1000
        """

        try:
            if aws_secret==None: #If gcp key is read from json file
                print("Using json file")
                key = service_account.Credentials.from_service_account_file(os.path.join('/opt/ml/processing/input', gcp_key))
            else: #If aws_secret has a value
                print("Using aws secret")
                key = service_account.Credentials.from_service_account_info(self.get_secret_for_bigquery(aws_secret))
                
        except TypeError:
            print("Please, use a valid aws_secret or json file")
        
        client = bigquery.Client(credentials=key)
        try:
            sql = sqlQuery
            df = client.query(sql).to_dataframe()
            print(f"¡Historical forecast download success from date!")
        except Exception as e:
            raise f"Falla la consulta en base de datos big query: {e}"
        else:
            return df

    def populate_dbtable(self,
                         df,
                         hostname=None,
                         db_user=None,
                         db_passwd=None,
                         db_name=None,
                         port='3306',
                         table_name=None,
                         db_type='mysql',
                         replace=True):
        """
        Create a table in a MySQL database and insert the records from a dataframe

        :param df: Dataframe storing the records to insert into the database table
        :param hostname: Public IP address or hostname of the remote database server
        :param db_user: Username of the database
        :param db_passwd: Password of the database
        :param db_name: Name of the target database
        :param port: TCP port number of the database (usually 3306)
        :param table_name: Name of target table
        :param db_type: Name of database type. Choose from mysql, mssql. Default mysql.
        :param replace: If True replace table records whether exists. Otherwise append records. Default True.
        :return inserted_records: Number of records inserted

        >>> records = populate_dbtable(df, hostname='202.10.0.1', db_user='johndoe', db_passwd='123456', db_name='dbo.TheDataBase')
        >>> records = 1000
        """
        if db_type == 'mysql':
            db_api = 'mysql+mysqlconnector://'
        elif db_type == 'mysql_legacy':
            db_api = 'mysql+pymysql://'
        elif db_type == 'mssql':
            db_api = 'mssql+pymssql://'
        else:
            self.logger.exception(f'No valid database type. Please check valid types: mysql, mssql')

        try:
            engine = create_engine(db_api + db_user + ':' + db_passwd + '@' + hostname + ':' + str(port) + '/' + db_name)
            if replace:
                df.to_sql(table_name, con=engine, if_exists='replace', index=False)
            else:
                df.to_sql(table_name, con=engine, if_exists='append', index=False)
            #inserted_records = engine.execute('SELECT COUNT(*) FROM ' + table_name).fetchall()[0][0]
            inserted_records = df.shape[0]
        except ConnectionRefusedError as err:
            logger.exception(f'Refused connection to the database. Please check parameters: {err}')
            raise
        return inserted_records

    def populate_dbtable_threads(self,
                                df,
                                hostname=None,
                                db_user=None,
                                db_passwd=None,
                                db_name=None,
                                port='3306',
                                table_name=None,
                                db_type='mysql',
                                replace = True,
                                chunk_size=500,
                                batch_size=10000,
                                threads=2):
        """
        Create a table in a MySQL database and insert the records from a dataframe

        :param df: Dataframe storing the records to insert into the database table
        :param hostname: Public IP address or hostname of the remote database server
        :param db_user: Username of the database
        :param db_passwd: Password of the database
        :param db_name: Name of the target database
        :param port: TCP port number of the database (usually 3306)
        :param table_name: Name of target table
        :param db_type: Name of database type. Choose from mysql, mssql. Default mysql.
        :param replace: If True replace table records whether exists. Otherwise append records. Default True.
        :param chunk_size: Number of records to insert. Default 500.
        :param batch_size: Number of rows per batch. Default 10000.
        :param threads: Number of threads to use for parallel execution. Default 2.
        :return inserted_records: Number of records inserted

        >>> records = populate_dbtable(df, hostname='202.10.0.1', db_user='johndoe', db_passwd='123456', db_name='dbo.TheDataBase')
        >>> records = 1000
        """
        try: 
            if db_type == 'mysql':
                db_api = 'mysql+mysqlconnector://'
            elif db_type == 'mysql_legacy':
                db_api = 'mysql+pymysql://'
            elif db_type == 'mssql':
                db_api = 'mssql+pymssql://'
            else:
                raise ValueError(f"No valid database type. Please check valid types: mysql, mssql")

            # Validación inicial
            if df.empty:
                print(f"[WARNING] El DataFrame para la tabla {table_name} está vacío. Saltando...")
                return 0
            if not table_name:
                print("[ERROR] No se especificó un nombre de tabla. Saltando...")
                return 0
            
            total_inserted_records = 0
            
            # Creación de batches y el motor
            total_rows = len(df)
            batches = [df.iloc[start:start + batch_size] for start in range(0, total_rows, batch_size)]
            engine = create_engine(f"{db_api}{db_user}:{db_passwd}@{hostname}:{port}/{db_name}")

            #Si replace, realizamos ya la eliminación de los registros anteriores y dejamos creada la estructura nueva 
            #Se hace por fuera de los hilos para que no genere problemas con el acceso paralelo a la tabla
            action = 'replace' if replace else 'append'

            if replace:
                print(f"[INFO] Reemplazando la tabla {table_name} antes de iniciar la carga.")
                df.iloc[0:0].to_sql(table_name, con=engine, if_exists='replace', index=False)
                action = 'append'  # Evitamos que los hilos vuelvan a reemplazar

            # Función interna para procesar cada batch. 
            # Si replace es True, al iniciar se reemplaza y todos los otros batches deben agregarse al primero
            def process_batch(batch, start_idx):
                try:
                    # Obtener rango de líneas
                    start_line = start_idx
                    end_line = start_idx + len(batch) - 1
                    thread_name = current_thread().name
                    print(f"[INFO] [{thread_name}] Procesando batch de líneas {start_line}-{end_line} en la tabla {table_name} con acción {action}.")
                    batch.to_sql(table_name, con=engine, if_exists='append', index=False, chunksize=chunk_size)
                    return len(batch)
                except Exception as err:
                    print(f"[ERROR] Error al cargar batch: {err}")
                    raise

            # Ejecutar la carga en paralelo
            print(f"[INFO] Iniciando carga para la tabla {table_name}. Total de filas: {total_rows}")
            with ThreadPoolExecutor(max_workers=threads) as executor:
                results = executor.map(
                    lambda idx_batch: process_batch(batches[idx_batch], start_idx=(idx_batch * batch_size)),
                    range(len(batches)))
                total_inserted_records = sum(results)

            print(f"[INFO] Carga completa para la tabla {table_name}. Total de registros insertados: {total_inserted_records}")
            return total_inserted_records
        
        except Exception as e:
            print(f"[ERROR] Error durante la carga de la tabla {table_name}: {e}")
            return 0



    def download_dbtable(self, hostname=None, db_user=None, db_passwd=None, db_name=None, port='3306', table_name=None, schema=None, db_type='mysql', query=None):
        """Return a dataframe containing the data extracted from MSSQL database's table supporting PyODBC connector

        :param hostname: Public IP address or hostname of the remote database server
        :param db_user: Username of the database
        :param db_passwd: Password of the database
        :param db_name: Name of the target database
        :param port: TCP port number of the database. Default 3306
        :param table_name: Name of target table
        :param schema: Name of database schema
        :param db_type: Name of database type. Choose from mysql, mssql, postgres, mysql_legacy. Default mysql.
        :param query: SQL statement to use as query.
        :return df: Dataframe containing the data from database's table

        >>> df = download_dbtable(hostname='202.10.0.1', db_user='johndoe', db_passwd='123456', db_name='dbo.TheDataBase', query='SELECT * FROM table')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        if db_type == 'mysql':
            db_api = 'mysql+mysqlconnector://'
        elif db_type == 'mysql_legacy':
            db_api = 'mysql+pymysql://'
        elif db_type == 'mssql':
            db_api = 'mssql+pymssql://'
        elif db_type == 'postgres':
            db_api = 'postgresql://'
        elif db_type == 'sap_hana':
            db_api = 'hana+hdbcli://'
        else:
            self.logger.exception(f'No valid database type. Please check valid types: mysql, mssql')

        try:
            if db_type == 'sap_hana':
                engine = create_engine(db_api + db_user + ':' + db_passwd + '@' + hostname + ':' + str(port) + '?currentSchema=' + schema)
            else:
                engine = create_engine(db_api + db_user + ':' + db_passwd + '@' + hostname + ':' + str(port) + '/' + db_name)
            connection = engine.connect()
            stmt = text(query)
            df = pd.read_sql_query(stmt, connection)
        except ConnectionRefusedError as err:
            logger.exception(f'Refused connection to the database. Please check parameters: {err}')
            raise
        return df

    def download_rdstable(self, rds_arn=None, secret_arn=None, database_name=None, sql_query=None, query_params=None):
        """
        Return query results to RDS database

        :param rds_arn: Database instance or clusrter's ARN
        :param secret_arn: Secret Manager resource ARN
        :param database_name: Database name to query on instance or cluster
        :param sql_query: Query string on SQL syntax
        :param query_params: List of dictionary values to put into the query string
        :return response: Records queried from the RDS database

        >>> response = download_rdstable(rds_arn='arn:rds:mycluster', \
                                         secret_arn='arn:secret:mysecret', \
                                         database_name='mydb', \
                                         sql_query=[{'name': 'paramId', 'value': {'stringValue': 'myvalue'}}], \
                                         query_params=None)
        >>> response = [{'date': '2021-06-07'}, {'name': 'John Doe'}, {'salary': 1000}]
        """
        client = boto3.client('rds-data',
                              region_name='us-east-1',
                              aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key)
        try:
            # Query project table
            response = client.execute_statement(parameters=query_params,
                                                resourceArn=rds_arn,
                                                secretArn=secret_arn,
                                                database=database_name,
                                                sql=sql_query)
        except client.exceptions.BadRequestException as err:
            print(f'Incorrect request. Please check query syntax and parameters: {err}')
            return False
        return response['records']

    def download_csv(self,
                     q_name,
                     datalake_path=None,
                     sep=',',
                     index_col=None,
                     usecols=None,
                     num_records=None,
                     dayfirst=False,
                     compression='infer',
                     encoding='utf-8',
                     date_cols=None,
                     types=None,
                     thousands=None,
                     decimal='.',
                     low_memory=True):
        """Return a dataframe from a csv file stored in the datalake

        :param q_name: Plain file (.csv) to download and stored in a dataframe
        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :param sep: Field delimiter of the downloaded file. Default ','
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator
        :param decimal: Decimal separator. Default '.'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_csv(q_name='Q', datalake_path='as-is/folder')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.csv')
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, q_name + '.csv', file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, q_name, q_name + '.csv'), file_path)
            df = pd.read_csv(file_path,
                             sep=sep,
                             index_col=index_col,
                             usecols=usecols,
                             nrows=num_records,
                             dayfirst=dayfirst,
                             compression=compression,
                             encoding=encoding,
                             low_memory=low_memory,
                             parse_dates=date_cols,
                             thousands=thousands,
                             decimal=decimal,
                             dtype=types)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No csv file found. Please check paths: {err}')
            raise
        return df

    def download_json_file(self, json_name=None, datalake_path=None):
        """
        Return a JSON file downloaded from the datalake

        :param json_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :return response: JSON file contents

        >>>
        >>>
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, json_name + '.json')
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, json_name + '.csv', file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, json_name + '.json'), file_path)
            with open(file_path, 'r') as json_file:
                response = json.load(json_file)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return response

    def download_csv_from_bucket(self,
                                 datalake=None,
                                 datalake_path=None,
                                 sep=',',
                                 index_col=None,
                                 usecols=None,
                                 num_records=None,
                                 dayfirst=False,
                                 compression='infer',
                                 encoding='utf-8',
                                 date_cols=None,
                                 types=None,
                                 thousands=None,
                                 decimal='.',
                                 low_memory=True):
        """Return a dataframe from a file stored in a S3 bucket

        :param datalake: S3 bucket name
        :param datalake_path: Path to download the file from the bucket. Do not include datalake name. Default None.
        :param sep: Field delimiter of the downloaded file. Default ','
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator
        :param decimal: Decimal separator. Default '.'
        :return df: Dataframe containing the data from the file stored in the bucket

        >>> df = download_csv_from_bucket(datalake='my-bucket', datalake_path='as-is/folder/file.csv')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, 'object.csv')
        try:
            s3_client.download_file(datalake, os.path.join(datalake_path), file_path)
            df = pd.read_csv(file_path,
                             sep=sep,
                             index_col=index_col,
                             usecols=usecols,
                             nrows=num_records,
                             dayfirst=dayfirst,
                             compression=compression,
                             encoding=encoding,
                             low_memory=low_memory,
                             thousands=thousands,
                             parse_dates=date_cols,
                             decimal=decimal,
                             dtype=types)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return df

    def download_object_csv(self,
                            datalake_path=None,
                            sep=',',
                            index_col=None,
                            usecols=None,
                            num_records=None,
                            dayfirst=False,
                            compression='infer',
                            encoding='utf-8',
                            date_cols=None,
                            types=None,
                            thousands=None,
                            decimal='.',
                            low_memory=True):
        """Return a dataframe from a file stored in the datalake

        :param datalake_path: Path to download the file from the S3 datalake. Do not include datalake name. Default None.
        :param sep: Field delimiter of the downloaded file. Default ','
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator
        :param decimal: Decimal separator. Default '.'
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_object_csv(datalake_path='as-is/folder/file.txt')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, 'object.dat')
        try:
            s3_client.download_file(self.datalake, os.path.join(datalake_path), file_path)
            df = pd.read_csv(file_path,
                             sep=sep,
                             index_col=index_col,
                             usecols=usecols,
                             nrows=num_records,
                             dayfirst=dayfirst,
                             compression=compression,
                             encoding=encoding,
                             low_memory=low_memory,
                             thousands=thousands,
                             parse_dates=date_cols,
                             decimal=decimal,
                             dtype=types)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return df

    def download_txt(self,
                     q_name,
                     datalake_path=None,
                     sep='\t',
                     index_col=None,
                     usecols=None,
                     num_records=None,
                     dayfirst=False,
                     compression='infer',
                     encoding='utf-8',
                     date_cols=None,
                     types=None,
                     thousands=None,
                     low_memory=True,
                     decimal='.'):
        """Return a dataframe from a csv file stored in the datalake

        :param q_name: Plain file (.txt) to download and stored in a dataframe
        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :param sep: Field delimiter of the downloaded file. Default '\t'
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator.
        :param decimal: Decimal separator. Default '.'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_txt(q_name='Q', datalake_path='as-is/folder')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.txt')
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, q_name + '.txt', file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, q_name + '.txt'), file_path)

            df = pd.read_csv(file_path,
                             sep=sep,
                             index_col=index_col,
                             usecols=usecols,
                             nrows=num_records,
                             dayfirst=dayfirst,
                             compression=compression,
                             encoding=encoding,
                             low_memory=low_memory,
                             parse_dates=date_cols,
                             thousands=thousands,
                             decimal=decimal,
                             dtype=types)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No csv file found. Please check paths: {err}')
            raise
        return df

    def download_all_objects_csv(self,
                                 datalake_path=None,
                                 sep=',',
                                 index_col=None,
                                 num_records=None,
                                 dayfirst=False,
                                 compression='infer',
                                 encoding='utf-8',
                                 low_memory=True,
                                 date_cols=None,
                                 types=None,
                                 thousands=None,
                                 decimal='.'):
        """Return a dataframe from a file stored in the datalake

        :param datalake_path: Path to download the file from the S3 datalake. Do not include datalake name. Default None.
        :param sep: Field delimiter of the downloaded file. Default ','
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param num_records: Number of records to fetch from the source. Default None
        :param dayfirst: DD/MM format dates, international and European format. Default False
        :param compression: For on-the-fly decompression of on-disk data. Default 'infer'
        :param encoding: Encoding to use for UTF when reading/writing. Default 'utf-8'
        :param low_memory: Internally process the file in chunks, resulting in lower memory use while parsing, but possibly mixed type inference. Default True
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :param thousands: Thousands separator
        :param decimal: Decimal separator. Default '.'
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_all_objects_csv(datalake_path='as-is/folder/file')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_resource = boto3.resource('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)

        try:
            df = pd.DataFrame()
            datalake = s3_resource.Bucket(self.datalake)
            objects = datalake.objects.filter(Prefix=datalake_path)
            for obj in objects:
                path, filename = os.path.split(obj.key)
                if filename != '_SUCCESS' and filename != '_CHECK':
                    datalake.download_file(obj.key, os.path.join('/tmp', filename))
                    df_tmp = pd.read_csv(os.path.join('/tmp', filename),
                                         sep=sep,
                                         index_col=index_col,
                                         nrows=num_records,
                                         dayfirst=dayfirst,
                                         compression=compression,
                                         encoding=encoding,
                                         low_memory=low_memory,
                                         parse_dates=date_cols,
                                         thousands=thousands,
                                         decimal=decimal,
                                         dtype=types)
                    df = pd.concat([df, df_tmp], axis='rows').drop_duplicates()
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return df

    def download_dynamodb(self, table_name, tenant_id):
        """
        Return a dataframe with the data fetch from DynamoDB

        :param table_name: Table name in DynamoDB table
        :param tenant_id: Partition column mapping tenant's ID to whom belongs the records
        :return df: Dataframe to store records fetched from DynamoDB
        >>> df = download_dynamodb(table_name='sampleTbl', tenant_id='1234')
        >>> df =
                tenantId    Date         Attr
        idx0    A121        2020-12-01   3
        """
        dydb_client = boto3.client('dynamodb', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        dynamodb_session = Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=self.region)
        dydb = dynamodb_session.resource('dynamodb')
        try:
            dynamo_tbl = dydb.Table(table_name)
            response = dynamo_tbl.query(
                KeyConditionExpression=Key('tenantId').eq(md5(tenant_id.encode('utf-8')).hexdigest()) &\
                                       Key('Fecha').between('2010-01-01', '2025-12-31')
            )
            items = response['Items']
        except dydb_client.exceptions.ResourceNotFoundException as err:
            print(f'Table not found. Please check names :{err}')
            return False
            raise
        return items

    def download_excel(self,
                       q_name,
                       sheet_name,
                       datalake_path=None,
                       index_col=None,
                       usecols=None,
                       num_records=None,
                       date_cols=None,
                       types=None,
                       header_=0,
                       skiprows_=None):
        """Return a dataframe from a csv file stored in the datalake

        :param q_name: Excel file to download and stored in a dataframe. Include extension xls, xlsx, ods, etc.
        :param sheet_name: Excel sheet to download and stored in a dataframe
        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param num_records: Number of records to fetch from the source. Default None
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_excel(q_name='Q', sheet_name='sheet1', datalake_path='as-is/folder')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name)
        try:
            if datalake_path is None:
                s3_client.download_file(self.datalake, q_name, file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, q_name), file_path)
            df = pd.read_excel(file_path,
                               sheet_name=sheet_name,
                               index_col=index_col,
                               usecols=usecols,
                               engine='openpyxl',
                               nrows=num_records,
                               parse_dates=date_cols,
                               dtype=types,
                               header=header_,
                               skiprows=skiprows_)
            df = df.dropna(how='all')
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            raise
        return df

    def download_excel_from_bucket(self,
                                   datalake=None,
                                   datalake_path=None,
                                   sheet_name=0,
                                   index_col=None,
                                   usecols=None,
                                   num_records=None,
                                   date_cols=None,
                                   types=None,
                                   header_=0,
                                   skiprows_=None):
        """Return a dataframe from a file stored in a S3 bucket

        :param datalake: S3 bucket name
        :param datalake_path: Path to download the file from the bucket. Do not include datalake name. Default None.
        :param sheet_name: Excel sheet to download and stored in a dataframe
        :param index_col: Column(s) to use as the row labels of the DataFrame, either given as string name or column index.
        :param usecols: Columns to use in returning dataframe.
        :param num_records: Number of records to fetch from the source. Default None
        :param date_cols: List of date columns to parse as datetime type. Default None
        :param types: Dict with data columns as keys and data types as values. Default None
        :return df: Dataframe containing the data from the file stored in the datalake

        >>> df = download_excel_from_bucket(datalake='my-bucket', datalake_path='as-is/folder/file.csv')
        >>> df
              var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, 'object.xlsx')
        try:
            s3_client.download_file(datalake, os.path.join(datalake_path), file_path)
            df = pd.read_excel(file_path,
                               sheet_name=sheet_name,
                               index_col=index_col,
                               usecols=usecols,
                               engine='openpyxl',
                               nrows=num_records,
                               parse_dates=date_cols,
                               dtype=types,
                               header=header_,
                               skiprows=skiprows_)
            df = df.dropna(how='all')
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
        except FileNotFoundError as err:
            self.logger.exception(f'No object file found. Please check paths: {err}')
            raise
        return df

    def download_xml(self, url_=None, header_=None, body_=None):
        """Return a response in XML format from a SOAP web service

        :param url_: URL endpoint to access SOAP web service
        :param header_: Header in rest api configuration parameters
        :param body_: Body input parameters
        :return response: Plain  text with data xml

        address = 'http://200.200.200.200:81/service.asmx'
        headers = {'Content-Type':'text/xml;charset=UTF-8'}
        body = ""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
                     <soapenv:Header/>
                            <soapenv:Body>
                                <tem:EjecutarConsultaXML>
                                    <!--Optional:-->
                                    <tem:pvstrxmlParametros>
                                        <![CDATA[
                                        <Consulta>
                                            <NombreConexion>Datup_Real</NombreConexion>
                                            <IdCia>2</IdCia>
                                            <IdProveedor>Analytics</IdProveedor>
                                            <IdConsulta>CONSULTA_VENTAS</IdConsulta>
                                            <Usuario>myuser</Usuario>
                                            <Clave>mypassword</Clave>
                                            <Parametros>
                                                <p_periodo_ini>202105</p_periodo_ini>
                                                <p_periodo_fin>202105</p_periodo_fin>
                                            </Parametros>
                                        </Consulta>]]>
                                    </tem:pvstrxmlParametros>
                                </tem:EjecutarConsultaXML>
                            </soapenv:Body>
                        </soapenv:Envelope>""

        >>> response = download_xml(url_=address, header_=headers, body_=body)
        >>> response =
                        '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><EjecutarConsultaXMLResponse xmlns="http://tempuri.org/"><EjecutarConsultaXMLResult><xs:schema id="NewDataSet"
                        xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"><xs:element name="NewDataSet" msdata:IsDataSet="true"
                        msdata:UseCurrentLocale="true"><xs:complexType><xs:choice minOccurs="0" maxOccurs="unbounded"><xs:element name="Resultado"><xs:complexType><xs:sequence><xs:element
                        name="Compañia" type="xs:short" minOccurs="0" /><xs:element name="Llave_x0020_Documento" type="xs:int" minOccurs="0"'
        """
        try:
            r = requests.post(url_, headers=header_, data=body_, allow_redirects=True)
            response = r.text
        except requests.exceptions.HTTPError as err:
            self.logger.exception(f'Http error: {err}')
            raise
        except requests.exceptions.ConnectionError as err:
            self.logger.exception(f'Error connecting: {err}')
            raise
        except requests.exceptions.Timeout as err:
            self.logger.exception(f'Timeout error: {err}')
            raise
        except requests.exceptions.RequestException as err:
            self.logger.exception(f'Oops: Something else: {err}')
            raise
        return response
    
    def download_parquet(self, q_name, datalake_path=None, columns=None, engine='pyarrow', filters=None):
        """Return a dataframe from a parquet file stored in the datalake

        :param q_name: File name (without extension) to download and store in a dataframe.
        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :param columns: Subset of columns to read from the Parquet file. Default None (reads all columns).
        :param engine: Engine to use for reading Parquet files. Default 'pyarrow'.
        :param filters: Filters to apply to the Parquet file rows while reading. Default None.
        :return df: DataFrame containing the data from the Parquet file stored in the datalake.

        >>> df = download_parquet(q_name='Q', datalake_path='as-is/folder')
        >>> df
            var1    var2    var3
        idx0     1       2       3
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.parquet')
        print(f'Engine: {engine}')

        try:
            # Download the Parquet file from S3
            if datalake_path is None:
                s3_client.download_file(self.datalake, q_name + '.parquet', file_path)
            else:
                s3_client.download_file(self.datalake, os.path.join(datalake_path, q_name, q_name + '.parquet'), file_path)

            # Read the Parquet file into a DataFrame
            df = pd.read_parquet(file_path, columns=columns, engine=engine, filters=filters)
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            raise
        except FileNotFoundError as err:
            self.logger.exception(f'No Parquet file found. Please check paths: {err}')
            raise
        except Exception as e:
            self.logger.exception(f'Failed to read the Parquet file: {e}')
            raise
        return df


    def download_models(self, datalake_path=None):
        """Returns True as successful download of the n_backtests models trained by attup model

        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :return: True if success, else False.

        >>> models = download_models(datalake_path='path/to/data')
        >>> True
        """

        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        for i in range(self.backtests + 1):
            q_name = "model" + str(i)
            file_path = os.path.join(Config.LOCAL_PATH, q_name + '.h5')
            print(file_path)
            try:
                if datalake_path is None:
                    s3_client.download_file(self.datalake, q_name + '.h5', file_path)
                else:
                    s3_client.download_file(self.datalake, os.path.join(datalake_path, "models", q_name + '.h5'), file_path)
            except ClientError as err:
                self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            except FileNotFoundError as err:
                self.logger.exception(f'No csv file found. Please check paths: {err}')
                raise
            return True

    def download_models_tft(self, datalake_path=None):
        """Returns True as successful download of the n_backtests models trained by attup model

        :param datalake_path: Path to download the file from the S3 datalake. Default None.
        :return: True if success, else False.

        >>> models = download_models(datalake_path='path/to/data')
        >>> True
        """

        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        for i in range(self.backtests + 1):
            q_name = "model" + str(i)
            file_path = os.path.join(Config.LOCAL_PATH, q_name + '.ckpt')
            print(file_path)
            try:
                if datalake_path is None:
                    s3_client.download_file(self.datalake, q_name + '.ckpt', file_path)
                else:
                    s3_client.download_file(self.datalake, os.path.join(datalake_path, "models", q_name + '.ckpt'), file_path)
            except ClientError as err:
                self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            except FileNotFoundError as err:
                self.logger.exception(f'No csv file found. Please check paths: {err}')
                raise
            return True

    def upload_csv(self, df, q_name, datalake_path, sep=',', encoding='utf-8', date_format='%Y-%m-%d', lineterminator=None):
        """Return a success or failure boolean attempting to upload a local file to the datalake

        :param df: Dataframe to upload
        :param q_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :param sep: Field delimiter for the output file. Default ','
        :param date_format: Format string for datetime objects of output file. Default '%Y-%m-%d'
        :param encoding: A string representing the encoding to use in the output file. Default 'utf-8'
        :return: True if success, else False.

        >>> upload_csv(df=df, q_name='Q', datalake_path='as-is/folder')
        >>> True
        """
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.csv')
        df.to_csv(file_path, sep=sep, encoding=encoding, date_format=date_format, index=False, lineterminator=lineterminator)
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        try:
            response = s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, q_name, q_name + '.csv'))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True

    def upload_dynamodb(self, df, table_name, tenant_id, sort_col):
        """
        Return a success or failure boolean attempting to upload timeseries data to DynamoDB

        :param df: Dataframe to upload to DynamoDB table
        :param table_name: Table name in DynamoDB table
        :param tenant_id: Partition column mapping tenant's ID to whom belongs the records
        :param sort_col: Sorting column mapping usually to date column
        :return response: HTTP status code response. If 400 success, failure otherwise

        >>> upload_dynamodb(df=df, table_name=sampleTbl, tenant_id='acme', sort_col='Date')
        >>> True
        """
        dydb_client = boto3.client('dynamodb', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        dynamodb_session = Session(aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key, region_name=self.region)
        dydb = dynamodb_session.resource('dynamodb')
        try:
            dynamo_tbl = dydb.Table(table_name)
            with dynamo_tbl.batch_writer() as batch:
                for row in df.itertuples(index=False):
                    record = {}
                    record.update({'tenantId': md5(tenant_id.encode('utf-8')).hexdigest()})
                    record.update({sort_col: row[0].strftime('%Y-%m-%d')})
                    for ix, rec in enumerate(row[1:]):
                        record.update({df.columns[ix + 1]: Decimal(str(rec))})
                    batch.put_item(Item=record)
        except dydb_client.exceptions.ResourceNotFoundException as err:
            print(f'Table not found. Please check names :{err}')
            return False
            raise
        return True

    def upload_json(self, df, q_name=None, datalake_path=None, orient_=None, date_format_=None, date_unit_='s', compression_=None, indent_=4):
        """
        Return a success or failure response after attempting to upload a dataframe in JSON format

        :param df: Dataframe to upload in JSON format
        :param q_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :param orient_: Expected JSON string format. Possible values split, records, index, table, columns, values
        :param date_format_: Type of date conversion. epoch = epoch milliseconds, iso = ISO8601.
        :param date_unit_: The time unit to encode to, governs timestamp and ISO8601 precisione, e.g. s, ms, us, ns.
        :param compression_: A string representing the compression to use in the output file, e.g. gzip, bz2, zip, xz.
        :param indent_: Length of whitespace used to indent each record. Default 4.
        :return response: Success or failure uploading the dataframe

        >>> upload_json(df, q_name='Qtest', orient_='columns')
        >>> True
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.json')
        try:
            df.to_json(file_path, orient=orient_, date_format=date_format_, date_unit=date_unit_, compression=compression_, indent=indent_)
            response = s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, q_name + '.json'))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True

    def upload_json_file(self, message=None, json_name=None, datalake_path=None, indent_=4):
        """
        Return a success or failure response after attempting to upload a JSON file


        :param message: Dict type to convert to JSON and upload to datalake
        :param json_name: File name to save dataframe
        :param datalake_path: Path to upload the Q to S3 datalake
        :param indent_: Length of whitespace used to indent each record. Default 4.
        :return : Success or failure uploading the dataframe

        >>> upload_json_file(message=resp_dict, json_name='myjson', datalake_path='/path/to/data')
        >>> True
        """

        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        file_path = os.path.join(Config.LOCAL_PATH, json_name + '.json')
        try:
            with open(file_path, 'w') as json_file:
                json.dump(message, json_file, indent=indent_)
            s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, json_name + '.json'))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True

    def upload_timestream(self, df, db_name, table_name):
        """
        Return a success or failure boolean attempting to upload timeseries data to timestream database

        :param df: Dataframe to upload to Timestream table
        :param db_name: Database name in Timestream service
        :param table_name: Table name in Timestream service
        :return response: HTTP status code response. If 400 success, failure otherwise

        >>> upload_timestream(df=df, db_name=dbSample, table_name=tbSample)
        >>> True
        """
        ts_client = boto3.client('timestream-write',
                                 region_name=self.region,
                                 aws_access_key_id=self.access_key,
                                 aws_secret_access_key=self.secret_key)
        dimensions = [{'Name': 'tenantId', 'Value': '1000', 'DimensionValueType': 'VARCHAR'}]
        records = []
        for row in df.itertuples(index=False):
            for ix, rec in enumerate(row[1:]):
                records.append({
                    'Dimensions': dimensions,
                    'MeasureName': df.columns[ix + 1],
                    'MeasureValue': str(rec),
                    'MeasureValueType': 'DOUBLE',
                    'Time': str(int(pd.to_datetime(row[0]).timestamp())),
                    'TimeUnit': 'SECONDS',
                    'Version': 3
                })
        try:
            response = ts_client.write_records(DatabaseName=db_name, TableName=table_name, Records=records)
            status = response['ResponseMetadata']['HTTPStatusCode']
            print(f'Processed records: {len(records)}. WriteRecords status: {status}')
            self.logger.exception(f'Processed records: {len(records)}. WriteRecords status: {status}')
        except ts_client.exceptions.RejectedRecordsException as err:
            print(f'{err}')
            self.logger.exception(f'{err}')
            for e in err.response["RejectedRecords"]:
                print("Rejected Index " + str(e["RecordIndex"]) + ": " + e["Reason"])
                self.logger.exception("Rejected Index " + str(e["RecordIndex"]) + ": " + e["Reason"])
            return False
        except ts_client.exceptions.ValidationException as err:
            print(f"{err.response['Error']['Message']}")
            self.logger.exception(f"{err.response['Error']['Message']}")
            return False
        return status

    def upload_models(self, datalake_path):
        """Return a success or failure boolean attempting to upload a tensorflow models to the datalake.

        :param datalake_path: Path to upload the attup trained models to S3 datalake
        :return: True if success, else False.

        >>> upload_models(datalake_path='as-is/folder')
        >>> True
        """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)

        for i in range(self.backtests + 1):
            q_name = "model" + str(i)
            print(q_name)
            file_path = os.path.join(Config.LOCAL_PATH, q_name + '.h5')
            try:
                response = s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, "models", q_name + '.h5'))
            except ClientError as err:
                self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
                return False
            except FileNotFoundError as err:
                self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
                return False
        return True

    def upload_models_tft(self, q_name, datalake_path):
        """Return a success or failure boolean attempting to upload a tensorflow models to the datalake.

            :param datalake_path: Path to upload the attup trained models to S3 datalake
            :return: True if success, else False.

            >>> upload_models(datalake_path='as-is/folder')
            >>> True
            """
        s3_client = boto3.client('s3', region_name=self.region, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        print(q_name)
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.ckpt')
        try:
            response = s3_client.upload_file(file_path, self.datalake, os.path.join(datalake_path, "models", q_name + '.ckpt'))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True

    def upload_object(self, datalake_name=None, datalake_path='', object_name=None):
        """Return a success or failure boolean attempting to upload a local file to the datalake

        :param datalake_name: S3 bucket name (datalake) to upload the object
        :param datalake_path: Path to upload the Q to S3 datalake
        :param object_name: Object name to upload to the S3 bucket (datalake)
        :return: True if success, else False.

        >>> upload_object(datalake_name='datup-datalake-datup', datalake_path='path/to/data', object_name='datup.dat')
        >>> True
        """
        file_path = os.path.join(Config.LOCAL_PATH, object_name)
        s3_client = boto3.client('s3', region_name='us-east-1', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        try:
            response = s3_client.upload_file(file_path, datalake_name, os.path.join(datalake_path, object_name))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True

    def upload_log(self):
        """Return a success or failure boolean attempting to upload a local file to the datalake

        :param datalake_path: Path to upload the Q to S3 datalake
        :return: True if success, else False.

        >>> upload_log()
        >>> True
        """
        file_path = os.path.join(Config.LOCAL_PATH, self.logfile)
        s3_client = boto3.client('s3', region_name='us-east-1', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        try:
            response = s3_client.upload_file(file_path, self.datalake, os.path.join(self.log_path, self.logfile))
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No excel file or sheet name found. Please check paths: {err}')
            return False
        return True

    def upload_parquet(self, df, q_name, datalake_path, compression='snappy', engine='pyarrow'):
        """Return a success or failure boolean attempting to upload a local parquet file to the datalake

        :param df: Dataframe to upload
        :param q_name: File name to save dataframe
        :param datalake_path: Path to upload the file to S3 datalake
        :param compression: Compression to use in the parquet file. Default 'snappy'
        :param engine: Engine to use for writing parquet files. Default 'pyarrow'
        :return: True if success, else False.

        >>> upload_parquet(df=df, q_name='Q', datalake_path='as-is/folder')
        >>> True
        """
        file_path = os.path.join(Config.LOCAL_PATH, q_name + '.parquet')
        
        print(f'Compression: {compression}')
        print(f'Engine: {engine}')
        
        # Save DataFrame as Parquet file
        try:
            df.to_parquet(file_path, engine=engine, compression=compression, index=False)
        except Exception as e:
            self.logger.exception(f'Failed to save the DataFrame as a Parquet file: {e}')
            return False

        s3_client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
        try:
            # Upload the Parquet file to S3
            response = s3_client.upload_file(
                file_path,
                self.datalake,
                os.path.join(datalake_path, q_name, q_name + '.parquet')
            )
        except ClientError as err:
            self.logger.exception(f'No connection to the datalake. Please check the paths: {err}')
            return False
        except FileNotFoundError as err:
            self.logger.exception(f'No Parquet file found. Please check paths: {err}')
            return False

        return True


    def copy_between_datalakes(self, q_name=None, src_datalake=None, src_path=None, dst_datalake=None, dst_path=None):
        """
        Return True whether successful copy between datalake buckets occurs

        :param q_name: File or dataset name including the type or extension
        :param src_datalake: Source datalake's bucket name
        :param src_path: Source datalake's key path, excluding dataset name
        :param dst_datalake: Destination datalake's bucket name
        :param dst_path: Destination datalake's key path, excluding dataset name
        :return : True if success, else False.

        >>> copy_between_datalakes(q_name='mycube', src_datalake='bucket-a', src_path='path/to/file', dst_datalake='bucket-b', dst_path='path/to/file')
        >>> True
        """

        s3_client = boto3.resource('s3',
                                   region_name='us-east-1',
                                   aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        try:
            copy_source = {'Bucket': src_datalake, 'Key': os.path.join(src_path, q_name)}
            filename, filetype = q_name.split('.')
            if filetype == 'csv':
                s3_client.meta.client.copy(copy_source, dst_datalake, os.path.join(dst_path, filename, filename + '.' + filetype))
            elif filetype == 'xls' or filetype == 'xlsx' or filetype == 'XLS' or filetype == 'XLSX':
                s3_client.meta.client.copy(copy_source, dst_datalake, os.path.join(dst_path, filename + '.' + filetype))
            else:
                self.logger.debug(f'No valid dataset type. Please check database or datalake to debug.')
        except FileNotFoundError as err:
            self.logger.exception(f'No file or datalake found. Please check paths: {err}')
            return False
        return True
    
    def download_bucket_last_excel_file(self,
                                        bucket_name, 
                                        folder,
                                        datalake=None,
                                        sheet_name=0,
                                        index_col=None,
                                        usecols=None,
                                        num_records=None,
                                        date_cols=None,
                                        types=None,
                                        header_=0,
                                        skiprows_=None):
        """
        Esta función descarga el archivo Excel más reciente (último modificado) 
        de una carpeta en un bucket de S3, sin importar el nombre del archivo.
        Input:
        - bucket_name: Nombre del bucket de S3.
        - folder: Carpeta en el bucket donde se buscará el archivo.
        - datalake: Nombre del datalake donde se buscará el archivo.
        - sheet_name: Nombre o índice de la hoja a cargar.
        - index_col: Nombre o índice de la columna a usar como índice.
        - usecols: Columnas a seleccionar.
        - num_records: Número de registros a cargar.
        - date_cols: Columnas a parsear como fechas.
        - types: Tipos de datos de las columnas.
        - header_: Fila a usar como encabezado.
        - skiprows_: Número de filas a salt
        Output:
        - df: DataFrame de pandas con los datos del archivo Excel.
        """
        # Configura tu cliente de S3
        s3 = boto3.client('s3')

        # Lista los archivos en la carpeta especificada
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder)

        # Verifica si se encontraron archivos
        if 'Contents' in response:
            # Filtra los archivos Excel
            archivos_excel = [obj for obj in response['Contents'] if obj['Key'].endswith('.xlsx') or obj['Key'].endswith('.xls')]
            file_list = pd.DataFrame(archivos_excel)
            print('Archivos encontrados:\n',file_list[['Key', 'LastModified']])
            if archivos_excel:
                # Find the most recent file
                most_recent_file = max(archivos_excel, key=lambda x: x['LastModified'])
                archivo_s3 = most_recent_file['Key']
                print(f'Archivo más reciente encontrado: {archivo_s3}')

                # Carga el archivo de Excel en un DataFrame de pandas
                df = self.download_excel_from_bucket(datalake=datalake,
                                                     datalake_path=archivo_s3,
                                                     sheet_name=sheet_name,
                                                     index_col=index_col,
                                                     usecols=usecols,
                                                     num_records=num_records,
                                                     date_cols=date_cols,
                                                     types=types,
                                                     header_=header_,
                                                     skiprows_=skiprows_)
                print(f'Archivo cargado: {archivo_s3} \n')
                return df
            else:
                print('No se encontraron archivos Excel en la carpeta especificada.')
        else:
            print('No se encontraron archivos en la carpeta especificada.')
    
    def rename_and_upload_delta_hist_file(self,
                                          df,
                                          prefix='DEMAND',
                                          col_date='Fecha',
                                          datalake_path='dev/raw/as-is/forecast/historic_data',
                                          sep=',',
                                          encoding='utf-8',
                                          date_format='%Y-%m-%d',
                                          lineterminator=None):
        """
        Rename and upload the file with the prefix and YYYYMM date to datalake.
        Input:
        - df: DataFrame to upload.
        - prefix: Prefix for the file name.
        - col_date: Column name with the date.
        - datalake_path: Path in the datalake to upload the file.
        - sep: Separator for the CSV file.
        - encoding: Encoding for the CSV file.
        - date_format: Date format for the CSV file.
        - lineterminator: Line terminator for the CSV file.
        Output:
        - return: True if success, else False.
        """
        df[col_date] = pd.to_datetime(df[col_date])
        date_min = df[col_date].min()
        date_max = df[col_date].max()

        date_min = str(date_min)[0:7].replace('-','')
        date_max = str(date_max)[0:7].replace('-','')

        print(f'Fecha mínima: {date_min}')
        print(f'Fecha máxima: {date_max}')

        if date_min == date_max:
            print(f'El mes y año de las fechas min y max son iguales. Guardando archivo con nombre: {prefix}{date_min}.csv al datalake: {datalake_path}')
            self.upload_csv(df, q_name=prefix+date_min,
                        datalake_path=datalake_path,
                        sep=sep,
                        encoding=encoding,
                        date_format=date_format,
                        lineterminator=lineterminator)
        else:
            print('El mes y año de las fechas min y max son diferentes. Revisar datos.')
            return False
        return True
