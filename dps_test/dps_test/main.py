import sys

from urllib.parse import urlparse
import click

from .client import APIClient

@click.command()
@click.option('--url', required=True, help='The URL of the server to test.')
def cli(url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        error(f'Invalid URL "{url}". Double check URL is valid (and that it includes a scheme)')
        
    client = APIClient(url)
    
    if client.server_type == 'database_manager':
        if not client.server_info['debug']:
            error(f'Database manager is not capable of integration tests.\nThe database manager must be in debug mode. Do this by setting the DBM_DEBUG environment variable to a truthy value')
            
        capabilities = set(client.server_info['capabilities'])
        required_capabilities = {'fetch_signals', 'aggregate_signals', 'insert_signals', 'delete_dataset'}
        if capabilities != required_capabilities:
            error(f'''Database manager is not capabile of integration tests.
The DataStore must implement exactly {", ".join(required_capabilities)} in order to support integration tests, but
the server's DataStore only supports {', '.join(capabilities)}''')

        
    else:
        error(f'Server has invalid server type of "{client.server_type}"')

def error(message):
    print(f'Error: {message}.')
    sys.exit()

from unittest import TestCase
from datetime import datetime, timedelta

class TestDatabaseManager(TestCase):
    def test_basic(self):
        pass

