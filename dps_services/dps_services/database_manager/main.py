import json

from flask import Flask

import dps_services.util as util

app = Flask(__name__)

@app.route(util.make_api_url('query'))
def query():
    return 'Hello, World!'

'''
Request:
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb", "vc"],
            "interval": {
                "from": <int:nanoseconds>,
                "to": <int:nanoseconds>
            }
        }
    ]
}

Response:
{
    "results": [
        {
            "samples": [[<float>, <float>], [<float>, <float>]],
            "times": [<int:nanoseconds>, <int:nanoseconds>]
            "query": {
                    "dataset": "somename",
                    "signals": ["va", "vb", "vc"],
                    "interval": {
                        "from": <int:nanoseconds>,
                        "to": <int:nanoseconds>
                    }
                },
        }
    ]
}

Request: (aggregation)
{
    "queries": [
        {
            "dataset": "somename",
            "signals": ["va", "vb"],
            "interval": {
                "from": <int:nanoseconds>,
                "to": <int:nanoseconds>
            }
            "aggregation": "count" <can be COUNT, AVERAGE, MIN or MAX>
        }
    ]
}

Response: (aggregation)
{
    "results": [
        {
            "results": [<number>, <number>],
            "query": {
                    "dataset": "somename",
                    "signals": ["va", "vb"],
                    "interval": {
                        "from": <int:nanoseconds>,
                        "to": <int:nanoseconds>
                    }
                },
        }
    ]
}

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

if __name__ == '__main__':
   app.run(debug=True)
