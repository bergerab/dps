import sys
from datetime import datetime
from io import StringIO
import itertools

from sqlalchemy import and_
from sqlalchemy.sql import func

import dps_services.database_manager as dbm
import dps_services.util as util
from db import *
from config import DEBUG

dbc = None

class TimescaleDBDataStore(dbm.DataStore):
    UPSERT_QUERY = UpsertQuery('signal_data',
                               ('signal_id', 'time'),
                               ('value',))
    
    def insert_signals(self, dataset_name, signal_names, batches, times, upsert):
        '''
        `upsert` is a bool parameter that specifies if the signal should be upserted instead of inserted.

        This distinction is made, because for flat file imports, upsert is required when re-entering data.
        This is necessary if an upload of a file fails, or is cancelled. Upsert is not always desireable,
        because it has some overhead to check if a signal data already exists before inserting it. (this is
        something done by the database -- not our code). So real-time devices should do inserts, because they
        should never attempt to enter the same signal data more than once.

        I did some simple testing on my desktop, and found that upserting has an overhead of 20% - 30%.
        '''
        with dbc.scope() as session:
            t0 = datetime.now()
            
            dataset = dbc.get_dataset_by_name(dataset_name)
            # If the dataset, doesn't exist in the database, create it and continue.
            if dataset is None:
                dataset = Dataset(name=dataset_name)
                dbc.add(session, dataset)
                session.commit()

            print('fetching dataset took', datetime.now() - t0)
            t0 = datetime.now()

            signals = []
            for signal_name in signal_names:
                signal = dbc.get_signal_by_name_and_dataset_id(signal_name, dataset.dataset_id)
                # If any of the signals, don't exist in the database, create it and continue.            
                if signal is None:
                    signal = Signal(dataset_id=dataset.dataset_id, name=signal_name)
                    dbc.add(session, signal)
                    session.commit()
                signals.append(signal)

            print('fetching signals took', datetime.now() - t0)
            t0 = datetime.now()

            # I think this is the fastest way to generate the string we need
            # List comprehensions are fast (faster than loops):
            signal_datas = ''.join(
                (''.join((f'{signals[j].signal_id}\t{times[i]}\t{sample}\n' for j, sample in enumerate(batch))))
                for i, batch in enumerate(batches))

            print('preparing data took ', datetime.now() - t0)
            print('there are ', len(batches) * len(batches[0]))
            t0 = datetime.now()

            cursor = dbc.psycopg2_conn.cursor()
            if upsert:
                self.UPSERT_QUERY.execute(cursor, StringIO(signal_datas))
            else:
                cursor.copy_from(StringIO(signal_datas), 'signal_data', columns=('signal_id', 'time', 'value'))                

            print('copy_from took ', datetime.now() - t0)
            t0 = datetime.now()

            dbc.psycopg2_conn.commit()

    def get_signal_names(self, result, dataset_name, query, limit, offset):
        dataset = dbc.get_dataset_by_name(dataset_name)
        with dbc.scope() as session:
            q = session.query(Signal).filter_by(dataset_id=dataset.dataset_id) \
                                               .filter(Signal.name.ilike(f'%{query}%')) \
                                               .order_by(Signal.name)            
            for signal in q.all()[offset:offset+limit]:
                if signal.dataset_id == dataset.dataset_id:
                    result.add(signal.name)
            result.set_total(q.count())

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
        if interval:
            return query.filter(and_(Dataset.dataset_id == dataset_id, SignalData.time >= interval.start, SignalData.time <= interval.end, SignalData.signal_id.in_(signal_ids)))
        else:
            return query.filter(and_(Dataset.dataset_id == dataset_id, SignalData.signal_id.in_(signal_ids)))            

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
        make_app().run(debug=DEBUG, port=3002, threaded=True)
    finally:
        dbc.engine.dispose()
        dbc.psycopg2_conn.close()
