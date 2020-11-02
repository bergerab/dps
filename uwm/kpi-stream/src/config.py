import os
import sys
import json

def require_config(config, key):
    if key not in config:
        print('Config.json must have a key named ' + key)
        sys.exit(1)

def load_config():
    if os.path.exists('config.json'):
        config = json.loads(open('config.json').read())
    else:
        print('You must create a config.json file')
        sys.exit(1)

    require_config(config, 'INFLUXDB_HOST')
    require_config(config, 'INFLUXDB_PORT')
    require_config(config, 'TYPHOON_SETTINGS_DIR')    

    return config

def typhoon_path(file_path):
    p = os.path.join(CONFIG['TYPHOON_SETTINGS_DIR'], file_path)
    p = os.path.abspath(p)
    if not os.path.exists(p):
        raise Exception('Could not find Typhoon file "%s"' % file_path)
    return p

CONFIG = load_config()
