'''
Running requires installation of the dps_services package and 
'''
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.sql import func

import dps_services.database_manager as dbm
from db import *

def parse_datetime(datetime_string):
    return datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S.%f')

class TimescaleDBDataStore(dbm.DataStore):
    def __init__(self):
        self.dbc = DatabaseClient()

    def insert_signals(self, dataset_name, signal_names, batches, times):
        dataset = self.dbc.get_dataset_by_name(dataset_name)
        if dataset is None:
            dataset = Dataset(name=dataset_name)
            self.dbc.add(dataset)
            self.dbc.commit()

        signals = []
        for signal_name in signal_names:
            signal = self.dbc.get_signal_by_name(signal_name)
            if signal is None:
                signal = Signal(dataset_id=dataset.dataset_id, name=signal_name)
                self.dbc.add(signal)
                self.dbc.commit()
            signals.append(signal)
            
        for i, batch in enumerate(batches):
            for j, sample in enumerate(batch):
                time = times[i]
                signal = signals[j]
            
                signal_data = SignalData(signal_id=signal.signal_id, value=sample, time=parse_datetime(time))
                self.dbc.add(signal_data)
                self.dbc.commit()

    def fetch_signals_query(self, result, dataset, signals, interval):
        return self.dbc.query(SignalData).filter(and_(SignalData.time >= interval.start, SignalData.time <= interval.end))

    def fetch_signals(self, result, dataset, signals, interval):
        return fetch_signals(result, dataset, signals, interval).all()        

    def aggregate_signals(self, result, dataset, signals, interval, aggregation):
        raise Exception('DataStore.aggregate_signals unimplemented')

if __name__ == '__main__':
    app = dbm.make_app(TimescaleDBDataStore)
    app.run(port=3001)
