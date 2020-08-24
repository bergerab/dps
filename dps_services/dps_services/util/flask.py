import functools

from flask import request, jsonify

def json_api(view):
    @functools.wraps(view)
    def view_wrapper():
        jo = request.get_json()
        return jsonify(view(jo))
    return view_wrapper
    
def make_api_url(name, version=1):
    return f'/api/v{version}/{name}'
