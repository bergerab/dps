import functools
import traceback

from flask import request, jsonify, make_response

from .validation import ValidationException

def to_json(x):
    if x is True:
        return jsonify({ 'message': 'OK' })
    return jsonify(x)

def json_api(view):
    @functools.wraps(view)
    def view_wrapper():
        jo = request.get_json()
        try:
            ret = view(jo)
            if not isinstance(ret, dict):
                return ret
            return make_response(to_json(ret), 200)
        except ValidationException as e:
            return make_error_response(e, 400)
        except Exception as e:
            return make_error_response(e, 500)            
    return view_wrapper

def make_error_response(e, status_code):
    return make_response(jsonify({ 'error': traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__) }), status_code)    
    
def make_api_url(name, version=1):
    return f'api/v{version}/{name}'
