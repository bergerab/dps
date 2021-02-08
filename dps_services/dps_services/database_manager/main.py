import json
import os
from datetime import datetime

import requests

from flask import request, make_response, jsonify

from expiringdict import ExpiringDict

import dps_services.util as util
import dps_client.insert_pb2 as insert_pb2

from .data_store import DataStore
from .insert import load_insert_protobuf
from .insert import load_insert_json

def init_app(app, AppDataStore, debug=False):
    DPSMANURL  = os.getenv('DPS_MANAGER_URL', None)
    if DPSMANURL is None:
        raise Exception('You must provide the URL of your DPS Manager in the environment variable: DPS_MANAGER_URL.')
    if DPSMANURL[-1] != '/':
        DPSMANURL += '/'
    
    auth_cache = ExpiringDict(max_len=1000, max_age_seconds=60 * 10)
    '''
    A cache of all logged in API keys. This allows an API key to work for 10 minutes after its last authentication with DPS Manager.
    This means if you remove an API key, the key will still work for 10 minutes (unless you reboot the DPS Database Manager). 
    It also helps performance. This means keys will only need to re-login every 10 minutes.
    '''
    
    def authenticate():
        auth = request.headers.get('Authorization')
        if not auth:
            return make_response(jsonify({ 'message': 'Request is missing Authorization header.' }), 403)
        type, key = auth.split(' ')
        if not type or not key:
            return make_response(jsonify({ 'message': 'Invalid Authorization header.' }), 403)
        
        if key in auth_cache and auth_cache[key] == True:
            return True
        else:
            resp = requests.post(DPSMANURL + 'api/v1/authenticate_api_key',
                          json={
                              'key': key,
                          })
            if resp.status_code >= 400:
                return make_response({'error': resp.text}, resp.status_code)
    
            jo = resp.json()
            if jo['allowed'] == True:
                auth_cache[key] = True
                return True
            else:
                return make_response(jsonify({ 'message': 'API key failed authentication.' }), 403)    

    @app.route('/' + util.make_api_url('insert'), methods=['POST'])
    def insert():
        ret = authenticate()
        if ret != True:
            return ret
        if request.content_type == 'application/protobuf':
            insert_request = insert_pb2.InsertRequest()
            insert_request.ParseFromString(request.data)
            o = load_insert_protobuf(insert_request)
        else: # Otherwise, assume JSON.
            o = load_insert_json(request.get_json())
        AppDataStore.insert(o)
        # return make_response({})
        return make_response('{}')

    @app.route('/' + util.make_api_url('delete_dataset'), methods=['POST'])
    @util.json_api
    def delete_dataset(jo):
        ret = authenticate()
        if ret != True:
            return ret
        AppDataStore.delete(jo)
        return True

    @app.route('/' + util.make_api_url('query'), methods=['POST'])
    @util.json_api
    def query(jo):
        ret = authenticate()
        if ret != True:
            return ret
        return AppDataStore.query(jo)

    @app.route('/' + util.make_api_url('get_signal_names'), methods=['POST'])
    @util.json_api
    def get_signal_names(jo):
        ret = authenticate()
        if ret != True:
            return ret
        return AppDataStore.execute_get_signal_names(jo)

    @app.route('/' + util.make_api_url('get_dataset_names'), methods=['POST'])
    @util.json_api
    def get_dataset_names(jo):
        ret = authenticate()
        if ret != True:
            return ret
        return AppDataStore.execute_get_dataset_names(jo)

    @app.route('/' + util.make_api_url('get_range'), methods=['POST'])
    @util.json_api
    def get_range(jo):
        ret = authenticate()
        if ret != True:
            return ret
        return AppDataStore.execute_get_range(jo)

    @app.route('/', methods=['GET'])
    def info():
        capabilities = []
        # Only support delete_dataset if in debug mode (because it is only for integration testing)
        if AppDataStore.delete_dataset is not DataStore.delete_dataset:
            capabilities.append('delete_dataset')
        if AppDataStore.fetch_signals is not DataStore.fetch_signals:
            capabilities.append('fetch_signals')
        if AppDataStore.get_signal_names is not DataStore.get_signal_names:
            capabilities.append('get_signal_names')
        if AppDataStore.get_dataset_names is not DataStore.get_dataset_names:
            capabilities.append('get_dataset_names')
        if AppDataStore.get_range is not DataStore.get_range:
            capabilities.append('get_range')
        if AppDataStore.aggregate_signals is not DataStore.aggregate_signals:
            capabilities.append('aggregate_signals')
        if AppDataStore.insert_signals is not DataStore.insert_signals:
            capabilities.append('insert_signals')
        
        return {
            'type': 'database-manager',
            'version': '1.0.0',
            'protocols': ['application/json', 'application/protobuf'],
            'capabilities': capabilities,
            'debug': debug,
        }

    return app
