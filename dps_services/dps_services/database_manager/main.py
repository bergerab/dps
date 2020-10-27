import json

from flask import Flask

import dps_services.util as util
from .data_store import DataStore

def make_app(AppDataStore, debug=False):
    app = Flask(__name__)

    @app.route('/' + util.make_api_url('insert'), methods=['POST'])
    @util.json_api
    def insert(jo):
        AppDataStore.insert(jo)
        return True

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

    @app.route('/', methods=['GET'])    
    def info():
        capabilities = []
        # Only support delete_dataset if in debug mode (because it is only for integration testing)
        if debug and AppDataStore.delete_dataset is not DataStore.delete_dataset:
            capabilities.append('delete_dataset')
        if AppDataStore.fetch_signals is not DataStore.fetch_signals:
            capabilities.append('fetch_signals')
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
