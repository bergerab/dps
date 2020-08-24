import json

from flask import Flask, request, jsonify

import dps_services.util as util

def create_app(DataStore):
    app = Flask(__name__)

    @app.route(util.make_api_url('insert'), methods=['POST'])
    def insert():
        insert_request = request.get_json()
        return jsonify(DataStore.insert(insert_request))
    
    @app.route(util.make_api_url('query'), methods=['POST'])
    def query():
        query_request = request.get_json()
        return jsonify(DataStore.query(query_request))

'''
Request: (insert)
{
    "inserts": [
        {
            "dataset": <string>,
            "samples": [[<float>, <float>], [<float>, <float>]],
            "signals": [<string>, <string>],
            "times": [<int:nanoseconds>, <int:nanoseconds>]
        }
    ]
}

Response: (insert)
HTTP 200 or 201
'''
