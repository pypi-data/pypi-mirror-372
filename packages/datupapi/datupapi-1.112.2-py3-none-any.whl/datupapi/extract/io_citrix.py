import base64
import boto3
import json
import os
import pandas as pd
import requests

import time
from boto3.dynamodb.conditions import Key, Attr
from boto3.session import Session
from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import datetime
from datupapi.configure.config import Config
from datupapi.extract.io import IO
from google.cloud import bigquery
from google.oauth2 import service_account
import google
from hashlib import md5
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy import Integer, Float, String, DECIMAL
from sqlalchemy import insert, delete, exists, schema

import http.client as httplib
import urllib.parse
import urllib
import mimetypes
#from datupapi.extract.io_citrix import IO_Citrix


class IO_Citrix(Config):

    def __init__(self, config_file, logfile, log_path, *args, **kwargs):
        Config.__init__(self, config_file=config_file, logfile=logfile)
        self.log_path = log_path
        self.io = IO(config_file, logfile, log_path)
    

    #### EXPORT CITRIX
    def authenticate(self, hostname, client_id, client_secret, username, password):
        """
        Return Authenticate via username/password. Returns json token object.
        
        :param hostname: Hostname like "myaccount.sharefile.com"
        :param client_id: OAuth2 client_id key
        :param client_secret: OAuth2 client_secret key
        :param username: My@user.name
        :param password: Passwor
        :return : Authenticate.

        >>> token = authenticate(hostname, client_id, client_secret, username, password)
        >>> 200 OK
        """

        try:
            uri_path = '/oauth/token'
            
            headers = {'Content-Type':'application/x-www-form-urlencoded'}
            params = {'grant_type':'password', 'client_id':client_id, 'client_secret':client_secret,'username':username, 'password':password}
            
            http = httplib.HTTPSConnection(hostname)
            http.request('POST', uri_path, urllib.parse.urlencode(params), headers=headers)
            response = http.getresponse()
            
            print(response.status, response.reason)
            token = None
            if response.status == 200:
                token = json.loads(response.read())
                print('Received token info', token)
            
            http.close()
        except httplib.HTTPException as err:
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
        return token

    def get_hostname(self, token):
        """
        Return Hostname from authenticate.
        
        :param token: Token get from authenticate
        :return : Hostname.

        >>> get_hostname(token)
        """
        return '%s.sf-api.com'%(token['subdomain'])

    def get_authorization_header(self, token):
        """
        Return Authorization from authenticate.
        
        :param token: Token get from authenticate
        :return : Authorization.

        >>> get_authorization_header(token)
        """
        return {'Authorization':'Bearer %s'%(token['access_token'])}

    def get_content_type(self, filename):
        """
        Return Authorization from authenticate.
        
        :param filename: Name fon file
        :return : Authorization.

        >>> get_content_type(filename)
        """
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'   

    def get_item_by_path(self, token, uri_file_path):
        """
        Return code from citrix to get the path destination.
        
        :param token: Token get from authenticate
        :param uri_file_path: Uri file path from citrix, replace spaces by '%'
        :return : path from citrix.

        >>> get_hostname(token)
        """

        #DOCKER_CONFIG_PATH = os.path.join('/opt/ml/processing/input', 'config.yml')
        #io_citrix = IO_Citrix(config_file=DOCKER_CONFIG_PATH, logfile='data_extract', log_path='output/logs')

        uri_path = '/sf/v3/Items/ByPath?path='+uri_file_path

        print( 'GET %s%s'%(self.get_hostname(token), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname(token))
        http.request('GET', uri_path, headers=self.get_authorization_header(token))
        response = http.getresponse()
        
        print( response.status, response.reason)
        items = json.loads(response.read())
        print( items['Id'], items['CreationDate'], items['Name'])
        if 'Children' in items:
            children = items['Children'].copy()
            for child in children:
                print( child['Id'], items['CreationDate'], child['Name'])
        return items['Id']

    def multipart_form_post_upload(self, url, filepath):
        """ 
        Does a multipart form post upload of a file to a url.

        :param url: The url to upload file to
        :param filepath: The complete file path of the file to upload like, "c:/path/to/the.file
        :return: The http response.

        >>> multipart_form_post_upload(upload_config['ChunkUri'], local_path)
        """

        newline = b'\r\n'
        filename = os.path.basename(filepath)
        data = []
        headers = {}
        boundary = '----------%d' % int(time.time())
        headers['content-type'] = 'multipart/form-data; boundary=%s' % boundary
        data.append(('--%s' % boundary).encode('utf-8'))
        data.append(('Content-Disposition: form-data; name="%s"; filename="%s"' % ('File1', filename)).encode('utf-8'))
        data.append(('Content-Type: %s' % self.get_content_type(filename)).encode('utf-8'))
        data.append(('').encode('utf-8'))
        data.append(open(filepath, 'rb').read())
        data.append(('--%s--' % boundary).encode('utf-8'))
        data.append(('').encode('utf-8'))
        print(data)
        data_str = newline.join(data)
        headers['content-length'] = len(data_str)

        uri = urllib.parse.urlparse(url)
        http = httplib.HTTPSConnection(uri.netloc)
        http.putrequest('POST', '%s?%s'%(uri.path, uri.query))
        for hdr_name, hdr_value in headers.items():
            http.putheader(hdr_name, hdr_value)
        http.endheaders()
        http.send(data_str)
        return http.getresponse()

    def upload_file(self, token, path, local_path):
        """ 
        Uploads a File using the Standard upload method with a multipart/form mime encoded POST.
        
        :param token: Token get from authenticate
        :param path: Uri file path from citrix, replace spaces by '%'
        :param local_path: The full path of the file to upload, like 'c:/path/to/file.name' 
        >>> upload_file(token, 'allshared/Juan%20Valdez/Resultados/Forecast', "/content/ForecastsNFCGC_Diciembre (2).xlsx")
        """

        folder_id= self.get_item_by_path(token,path)
        uri_path = '/sf/v3/Items(%s)/Upload'%(folder_id)
        print('GET %s%s'%(self.get_hostname(token), uri_path))
        http = httplib.HTTPSConnection(self.get_hostname(token))
        http.request('GET', uri_path, headers=self.get_authorization_header(token))

        response = http.getresponse()
        upload_config = json.loads(response.read().decode('utf-8'))
        if 'ChunkUri' in upload_config:
            upload_response = self.multipart_form_post_upload(upload_config['ChunkUri'], local_path)
            print(upload_response.status, upload_response.reason)
            if upload_response.status!=200:
                print("ERROR ERROR ERROR "+local_path+"failed to upload!")
                raise ValueError('Recieved Response Status: '+upload_response.status+ ' ' + upload_response.reason+
                                '. \r\n Expected 200 OK!')
        else:
            print('No Upload URL received')


    def export_to_citrix(self, filename: str = None , citrixbucket: str = None):

        hostname = self.io.get_secret(secret_name='prod/upload/citrix')['hostname']
        username = self.io.get_secret(secret_name='prod/upload/citrix')['username']
        password = self.io.get_secret(secret_name='prod/upload/citrix')['password']
        client_id = self.io.get_secret(secret_name='prod/upload/citrix')['client_id']
        client_secret = self.io.get_secret(secret_name='prod/upload/citrix')['client_secret']
        try:
            self.logger.info("Lanzando Token para conexion al citrix")
            token = self.authenticate(hostname, client_id, client_secret, username, password)
            citrix_path = os.path.join('allshared', citrixbucket)
            self.upload_file(token, citrix_path, os.path.join('/tmp', filename))
            
            print("¡Upload success!")
        except Exception as err:
            self.logger.exception(f"Fail to load data to citrix: {err}")
            raise 

        else:

            self.logger.info("Consulta finalizada, datos extraidos correctamente AWS")
            print("¡SUCCESSFUL CITRIX LOAD!")