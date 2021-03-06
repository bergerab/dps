import sys
import unittest
from datetime import datetime, timedelta

from urllib.parse import urlparse
import click

from .client import APIClient
from .test_database_manager import make_test_case as make_database_manager_test
from .test_labview_integration import make_test_case as make_labview_integration_test
from .test_dps_manager import make_test_case as make_dps_manager_test

@click.command()
@click.option('--url', required=True, help='The URL of the server to test.')
def cli(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        error(f'Invalid URL "{url}". Double check URL is valid (and that it includes a scheme)')

    client = APIClient(url)
    
    if client.server_type == 'database-manager':
        if not client.server_info['debug']:
            error(f'Database manager is not capable of integration tests.\nThe database manager must be in debug mode. Do this by setting the DBM_DEBUG environment variable to a truthy value')
            
        capabilities = set(client.server_info['capabilities'])
        required_capabilities = {'fetch_signals', 'aggregate_signals', 'insert_signals', 'delete_dataset'}
        if capabilities != required_capabilities:
            error(f'''Database manager is not capable of integration tests.
The DataStore must implement exactly {", ".join(required_capabilities)} in order to support integration tests, but
the server's DataStore only supports {', '.join(capabilities)}''')
        run_all_tests(make_database_manager_test(client))
        
    elif client.server_type == 'labview-integration':
        dbm_url = client.server_info['dbm_url']
        send_threshold = client.server_info['send_threshold']        
        print('Connecting to LabVIEW Integration Server\'s Database Manager...')
        run_all_tests(make_labview_integration_test(url, APIClient(dbm_url), send_threshold))        
    elif client.server_type == 'dps-manager':
        run_all_tests(make_dps_manager_test(client))
    else:
        error(f'Server has invalid server type of "{client.server_type}"')

def run_all_tests(TestCase):
    ts = unittest.TestSuite()
    ts.addTest(unittest.makeSuite(TestCase))        
    runner = unittest.TextTestRunner()
    runner.run(ts)

def error(message):
    print(f'Error: {message}.')
    sys.exit()
