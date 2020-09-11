'''
Running requires installation of the dps_services package and 
'''
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.sql import func

import dps_services.database_manager as dbm
from db import *

dbc = DatabaseClient()

def parse_datetime(datetime_string):
    return datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S.%f')

class TimescaleDBDataStore(dbm.DataStore):
    def insert_signals(self, dataset_name, signal_names, batches, times):
        dataset = dbc.get_dataset_by_name(dataset_name)
        if dataset is None:
            dataset = Dataset(name=dataset_name)
            dbc.add(dataset)
            dbc.commit()

        signals = []
        for signal_name in signal_names:
            signal = dbc.get_signal_by_name_and_dataset_id(signal_name, dataset.dataset_id)
            if signal is None:
                signal = Signal(dataset_id=dataset.dataset_id, name=signal_name)
                dbc.add(signal)
                dbc.commit()
            signals.append(signal)
            
        for i, batch in enumerate(batches):
            for j, sample in enumerate(batch):
                time = times[i]
                signal = signals[j]
            
                signal_data = SignalData(signal_id=signal.signal_id, value=sample, time=parse_datetime(time))
                dbc.add(signal_data)
                dbc.commit()

    def fetch_signals_query(self, result, dataset, signals, interval):
        return dbc.query(SignalData).filter(and_(SignalData.time >= interval.start, SignalData.time <= interval.end))

    def fetch_signals(self, result, dataset, signals, interval):
        return fetch_signals_query(result, dataset, signals, interval).all()        

    def aggregate_signals(self, result, dataset, signals, interval, aggregation):
        pass
        
if __name__ == '__main__':
    app = dbm.make_app(TimescaleDBDataStore)
    app.run(debug=True)
