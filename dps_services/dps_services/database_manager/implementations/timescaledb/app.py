'''
Running requires installation of the dps_services package and 
'''
import dps_services.database_manager as dbm
import psycopg2 as pg

from db import *

class TimescaleDBDataStore(dbm.DataStore):
    def insert_signals(self, dataset, signals, samples, times):
        with db.connect() as conn:
            cur = conn.cursor()
            # Insert dataset if it doesn't already exist
            insert_dataset(cur, dataset)
            conn.commit()
        
        raise Exception('DataStore.insert unimplemented')

    def fetch_signals(self, result, dataset, signals, interval):
        with db.connect() as conn:
            pass
        raise Exception('DataStore.fetch_signals unimplemented')

    def aggregate_signals(self, result, dataset, signals, interval, aggregation):
        with db.connect() as conn:
            pass
        raise Exception('DataStore.aggregate_signals unimplemented')

if __name__ == '__main__':
    app = dbm.make_app(TimescaleDBDataStore)    
    app.run(debug=True)
