import os

USERNAME = os.getenv('TSDB_USERNAME', 'postgres')
PASSWORD = os.getenv('TSDB_PASSWORD', 'password')
URL = os.getenv('TSDB_URL', 'localhost')
PORT = os.getenv('TSDB_PORT', 5432)
DATABASE = os.getenv('TSDB_DATABASE', 'postgres')

CONNECTION = f'postgres://{USERNAME}:{PASSWORD}@{URL}:{PORT}/{DATABASE}'
