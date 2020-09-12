import os

USERNAME = os.getenv('TSDB_USERNAME', 'postgres')
PASSWORD = os.getenv('TSDB_PASSWORD', '3nchWKa*95iiV#')
URL = os.getenv('TSDB_URL', 'localhost')
PORT = os.getenv('TSDB_PORT', 5432)
DATABASE = os.getenv('TSDB_DATABASE', 'postgres')
DEBUG = bool(os.getenv('DBM_DEBUG', False))

if not PASSWORD:
    CONNECTION = f'postgres://{USERNAME}@{URL}:{PORT}/{DATABASE}'
else:
    CONNECTION = f'postgres://{USERNAME}:{PASSWORD}@{URL}:{PORT}/{DATABASE}'
