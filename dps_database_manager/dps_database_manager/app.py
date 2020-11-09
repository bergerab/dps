import sys
from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.sql import func

import dps_services.database_manager as dbm
import dps_services.util as util
from db import *
from config import DEBUG

dbc = None

class TimescaleDBDataStore(dbm.DataStore):
    def insert_signals(self, dataset_name, signal_names, batches, times):
        with dbc.scope() as session:
            dataset = dbc.get_dataset_by_name(dataset_name)
            # If the dataset, doesn't exist in the database, create it and continue.
            if dataset is None:
                dataset = Dataset(name=dataset_name)
                dbc.add(session, dataset)
                session.commit()

            signals = []
            for signal_name in signal_names:
                signal = dbc.get_signal_by_name_and_dataset_id(signal_name, dataset.dataset_id)
                # If any of the signals, don't exist in the database, create it and continue.            
                if signal is None:
                    signal = Signal(dataset_id=dataset.dataset_id, name=signal_name)
                    dbc.add(session, signal)
                    session.commit()
                signals.append(signal)

            for i, batch in enumerate(batches):
                for j, sample in enumerate(batch):
                    time = times[i]
                    signal = signals[j]
                
                    # Add the actual signal_data to the database for each (one signal_data for each sample).
                    signal_data = SignalData(signal_id=signal.signal_id, value=sample, time=time)
                    dbc.add(session, signal_data)
            session.commit()
            session.expunge_all()

    def get_signal_names(self, result, dataset_name, query, limit, offset):
        dataset = dbc.get_dataset_by_name(dataset_name)
        with dbc.scope() as session:
            for signal in session.query(Signal).filter_by(dataset_id=dataset.dataset_id) \
                                               .filter(Signal.name.ilike(f'%{query}%')) \
                                               .order_by(Signal.name).all()[offset:offset+limit]:
                if signal.dataset_id == dataset.dataset_id:
                    result.add(signal.name)

    def fetch_signals(self, result, dataset_name, signal_names, interval, limit):
        dataset_id = dbc.get_cached_dataset(dataset_name).dataset_id
        signal_ids = list(map(lambda x: dbc.get_cached_signal(x).signal_id, signal_names))

        # Get all signal_data within the time interval ordered by time (ascending).
        # We have to take this data and batch all values that share a timestamp together (in increasing time order).
        with dbc.scope() as session:
            q = self.time_filter(session.query(SignalData), interval, dataset_id, signal_ids).order_by(SignalData.time.asc())
            if limit:
                q = q.limit(limit)
            signal_datas = q.all()

        if not signal_datas:
            return

        buffer = []
        previous_time = signal_datas[0].time
        for i, signal_data in enumerate(signal_datas):
            # If the time has changed, or if this is the last batch,
            # flush the buffer (call result.add(frame, time) with it)
            if signal_data.time != previous_time:
                flush_buffer(result, buffer, previous_time, signal_ids)
                previous_time = signal_data.time
                buffer = [signal_data]
            else:
                # When the time value doesn't change since the last one,
                # append the data to the buffer (so it can all be sent
                # with the same time value).
                buffer.append(signal_data)
        if buffer:
            flush_buffer(result, buffer, previous_time, signal_ids)

    def aggregate_signals(self, result, dataset_name, signal_names, interval, aggregation):
        dataset_id = dbc.get_cached_dataset(dataset_name).dataset_id
        signal_ids = list(map(lambda x: dbc.get_cached_signal(x).signal_id, signal_names))        
        
        # Get the correct SQLAlchemy functions for each of the "aggregation" directives
        # Complete list is: max, min, average, and count.
        f = None
        if aggregation == 'max':
            f = func.max
        elif aggregation == 'min':
            f = func.min
        elif aggregation == 'average':
            f = func.avg
        elif aggregation == 'count':
            f = func.count
        else:
            raise Exception(f'aggregate_signals was given an unsupported aggregation of "{aggregation}".')

        with dbc.scope() as session:
            for signal_id, signal_name in zip(signal_ids, signal_names):
                signal_datas = session.query(f(SignalData.value)).filter(SignalData.signal_id == signal_id)
                result.set(signal_name, self.time_filter(signal_datas, interval, dataset_id, signal_ids).scalar())

    def time_filter(self, query, interval, dataset_id, signal_ids):
        return query.filter(and_(Dataset.dataset_id == dataset_id, SignalData.time >= interval.start, SignalData.time <= interval.end, SignalData.signal_id.in_(signal_ids)))

    # NOTE: Implementing delete_dataset is optional. It is only needed if you want to run the integration tests.
    def delete_dataset(self, dataset_name):
        dbc.delete_dataset(dataset_name)

# A helper function used for `fetch_signals`
def flush_buffer(result, buffer, previous_time, signal_ids):
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
    result.add(frame, previous_time)
        
def make_app():
    global dbc
    dbc = DatabaseClient()
    return dbm.make_app(TimescaleDBDataStore, DEBUG)

if __name__ == '__main__':
    try:
        make_app().run(debug=DEBUG, port=3002)
    finally:
        dbc.engine.dispose()
