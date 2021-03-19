import dps_batch_processor
import os

dps_batch_processor.do_cli('http://dps-manager:8000/',
                           'http://dps-database-manager:3002/',
                           os.environ.get('API_KEY'),
                           5,
                           50000,
                           interval=5,
                           verbose=True)
