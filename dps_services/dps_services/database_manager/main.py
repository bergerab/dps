import json

from flask import Flask

import dps_services.util as util

def make_app(DataStore):
    app = Flask(__name__)

    @app.route(util.make_api_url('insert'), methods=['POST'])
    @util.json_api
    def insert(jo):
        DataStore.insert(jo)
        return True

    @app.route(util.make_api_url('query'), methods=['POST'])    
    @util.json_api
    def query(jo):
        return DataStore.query(jo)

    return app

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
