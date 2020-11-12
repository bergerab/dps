import json

from flask import Flask
from flask import request, make_response

import dps_services.util as util
import dps_client.insert_pb2 as insert_pb2

from .data_store import DataStore
from .insert import load_insert_protobuf
from .insert import load_insert_json

def make_app(AppDataStore, debug=False):
    app = Flask(__name__)

    @app.route('/' + util.make_api_url('insert'), methods=['POST'])
    def insert():
        if request.content_type == 'application/protobuf':
            insert_request = insert_pb2.InsertRequest()
            insert_request.ParseFromString(request.data)
            o = load_insert_protobuf(insert_request)
            print('loaded object')
        else: # Otherwise, assume JSON.
            o = load_insert_json(request.get_json())
        AppDataStore.insert(o)
        return make_response({})

    if debug:
        @app.route('/' + util.make_api_url('delete_dataset'), methods=['POST'])
        @util.json_api
        def delete_dataset(jo):
            AppDataStore.delete(jo)
            return True

    @app.route('/' + util.make_api_url('query'), methods=['POST'])
    @util.json_api
    def query(jo):
        return AppDataStore.query(jo)

    @app.route('/' + util.make_api_url('get_signal_names'), methods=['POST'])
    @util.json_api
    def get_signal_names(jo):
        return AppDataStore.execute_get_signal_names(jo)

    @app.route('/', methods=['GET'])
    def info():
        capabilities = []
        # Only support delete_dataset if in debug mode (because it is only for integration testing)
        if debug and AppDataStore.delete_dataset is not DataStore.delete_dataset:
            capabilities.append('delete_dataset')
        if AppDataStore.fetch_signals is not DataStore.fetch_signals:
            capabilities.append('fetch_signals')
        if AppDataStore.get_signal_names is not DataStore.get_signal_names:
            capabilities.append('get_signal_names')
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
