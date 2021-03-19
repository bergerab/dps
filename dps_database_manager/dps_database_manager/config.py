import os

USERNAME   = os.getenv('TSDB_USERNAME', 'postgres')
PASSWORD   = os.getenv('TSDB_PASSWORD', 'password')
URL        = os.getenv('TSDB_URL', 'localhost')
PORT       = os.getenv('TSDB_PORT', 5432)
DATABASE   = os.getenv('TSDB_DATABASE', 'postgres')
DEBUG      = bool(os.getenv('DBM_DEBUG'))
CONNECTION = f'postgresql://{USERNAME}:{PASSWORD}@{URL}:{PORT}/{DATABASE}' \
    if PASSWORD else f'postgresql://{USERNAME}@{URL}:{PORT}/{DATABASE}'
