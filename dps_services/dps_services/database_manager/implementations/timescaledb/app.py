'''
Running requires installation of the dps_services package and 
'''
import dps_services.database_manager as dbm
import psycopg2

from .config import CONNECTION

class TimescaleDBDataStore(dbm.DataStore):
    def insert_signals(self, dataset, signals, samples, times):
        with psycopg2.connect(CONNECTION) as conn:
            pass
        raise Exception('DataStore.insert unimplemented')

    def fetch_signals(self, result, dataset, signals, interval):
        with psycopg2.connect(CONNECTION) as conn:
            pass
        raise Exception('DataStore.fetch_signals unimplemented')

    def aggregate_signals(self, result, dataset, signals, interval, aggregation):
        with psycopg2.connect(CONNECTION) as conn:
            pass
        raise Exception('DataStore.aggregate_signals unimplemented')

app = dbm.make_app(TimescaleDBDataStore)

if __name__ == '__main__':
   app.run()
