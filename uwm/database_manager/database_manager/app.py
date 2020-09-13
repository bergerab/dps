'''
Running requires installation of the dps_services package and 
'''
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.sql import func

import dps_services.database_manager as dbm
import dps_services.util as util
from db import *
from config import DEBUG

class TimescaleDBDataStore(dbm.DataStore):
    def __init__(self):
        self.dbc = DatabaseClient()

    def insert_signals(self, dataset_name, signal_names, batches, times):
        dataset = self.dbc.get_dataset_by_name(dataset_name)
        # If the dataset, doesn't exist in the database, create it and continue.
        if dataset is None:
            dataset = Dataset(name=dataset_name)
            self.dbc.add(dataset)
            self.dbc.commit()

        signals = []
        for signal_name in signal_names:
            signal = self.dbc.get_signal_by_name_and_dataset_id(signal_name, dataset.dataset_id)
            # If any of the signals, don't exist in the database, create it and continue.            
            if signal is None:
                signal = Signal(dataset_id=dataset.dataset_id, name=signal_name)
                self.dbc.add(signal)
                self.dbc.commit()
            signals.append(signal)
            
        for i, batch in enumerate(batches):
            for j, sample in enumerate(batch):
                time = times[i]
                signal = signals[j]
                
                # Add the actual signal_data to the database for each (one signal_data for each sample).
                signal_data = SignalData(signal_id=signal.signal_id, value=sample, time=time)
                self.dbc.add(signal_data)
        self.dbc.commit()

    def fetch_signals(self, result, dataset_name, signal_names, interval):
        dataset_id = self.dbc.get_cached_dataset(dataset_name).dataset_id
        signal_ids = list(map(lambda x: self.dbc.get_cached_signal(x).signal_id, signal_names))

        # Get all signal_data within the time interval ordered by time (ascending).
        # We have to take this data and batch all values that share a timestamp together (in increasing time order).
        signal_datas = self.time_filter(self.dbc.query(SignalData), interval, dataset_id).order_by(SignalData.time.asc()).all()

        if not signal_datas:
            return

        buffer = []
        time = signal_datas[0].time
        for i, signal_data in enumerate(signal_datas):
            is_last = i == len(signal_datas) - 1
            # If the time has changed, or if this is the last batch,
            # flush the buffer (call result.add(frame, time) with it)
            if signal_data.time != time or is_last:
                if is_last:
                    buffer.append(signal_data)
                    
                frame = []
                for signal_id in signal_ids:
                    # Search if the signal is present in the buffer, if it is, that
                    # means there is a value we must send for that signal.
                    # Otherwise if the signal isn't present, send a 0.
                    signal_existed = False
                    for signal in buffer: # If the signal is in the buffer (there was data for this signal at this time)
                        if signal.signal_id == signal_id:
                            frame.append(signal.value)
                            signal_existed = True 
                            break
                    if not signal_existed:
                        frame.append(0)
                result.add(frame, time)
                time = signal_data.time
                
                if not is_last:
                    buffer = [signal_data]
            else:
                # When the time value doesn't change since the last one,
                # append the data to the buffer (so it can all be sent
                # with the same time value).
                buffer.append(signal_data)

    def aggregate_signals(self, result, dataset_name, signal_names, interval, aggregation):
        dataset_id = self.dbc.get_cached_dataset(dataset_name).dataset_id
        
        # Get the correct SQLAlchemy functions for each of the "aggregation" directives
        f = None
        if aggregation == 'max':
            f = func.max
        elif aggregation == 'min':
            f = func.min
        elif aggregation == 'average':
            f = func.avg
        else:
            raise Exception(f'aggregate_signals was given an unsupported aggregation of "{aggregation}".')
        
        val = self.time_filter(self.dbc.query(f(SignalData.value)), interval, dataset_id).scalar()

    def time_filter(self, query, interval, dataset_id):
        return query.filter(and_(Dataset.dataset_id == dataset_id, SignalData.time >= interval.start, SignalData.time <= interval.end))

    # NOTE: Implementing delete_dataset is optional. It is only needed if you want to run the integration tests.
    def delete_dataset(self, dataset_name):
        self.dbc.delete_dataset(dataset_name)
        
def make_app():
    return dbm.make_app(TimescaleDBDataStore, DEBUG)

if __name__ == '__main__':
    make_app().run(debug=DEBUG, port=3001)
