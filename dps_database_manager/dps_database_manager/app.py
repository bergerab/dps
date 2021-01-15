import sys
from datetime import datetime
from io import StringIO
import itertools
import math
import requests

from sqlalchemy import and_, not_
from sqlalchemy.sql import func
from expiringdict import ExpiringDict

import dps_services.database_manager as dbm
import dps_services.util as util
from db import *
from config import DEBUG

dbc = None

VERBOSE = False

def log(*args):
    if VERBOSE:
        print(*args)

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

            # I think this is the fastest way to generate the string we need
            # List comprehensions are fast (faster than loops):
            signal_datas = ''.join(
                (''.join((f'{signals[j].signal_id}\t{times[i]}\t{sample}\n' for j, sample in enumerate(batch) if sample is not None and not math.isnan(sample))))
                for i, batch in enumerate(batches))

            conn = dbc.psycopg2_connpool.getconn()
            try:
                cursor = conn.cursor()
                if upsert:
                    self.UPSERT_QUERY.execute(cursor, StringIO(signal_datas))
                else:
                    # copy_from is the fastest way to insert bulk data into postgres
                    # it might be even faster to use a binary stream instead of a string stream
                    # but I didn't bother writing that.
                    cursor.copy_from(StringIO(signal_datas), 'signal_data', columns=('signal_id', 'time', 'value'))                
                conn.commit()
            finally:
                dbc.psycopg2_connpool.putconn(conn)

    def get_signal_names(self, result, dataset_name, query, limit, offset):
        if dataset_name is not None:
            dataset = dbc.get_cached_dataset(dataset_name, error_on_not_found=False)
            if not dataset:
                return
        with dbc.scope() as session:
            q = session.query(Signal)
            if dataset_name is not None:
                q = q.filter_by(dataset_id=dataset.dataset_id)
            q = q.filter(Signal.name.ilike(f'%{query}%')) \
                 .order_by(Signal.name)            
            for signal in q.all()[offset:offset+limit]:
                if dataset_name == None or signal.dataset_id == dataset.dataset_id:
                    result.add(signal.name)
            result.set_total(q.count())

    def get_dataset_names(self, result, query, limit, offset):
        with dbc.scope() as session:
            q = session.query(Dataset).filter(and_(Dataset.name.ilike(f'%{query}%'), not_(Dataset.name.ilike('batch_process%')))).order_by(Dataset.name)
            for dataset in q.all()[offset:offset+limit]:
                result.add(dataset.name)
            result.set_total(q.count())

    def get_range(self, result, dataset_name, signal_name):
        '''
        Gets the times of the first and last datapoints for the signal.
        '''
        if dataset_name is None:
            dataset_id = None
        else:
            ds = dbc.get_cached_dataset(dataset_name, error_on_not_found=False)
            if not ds:
                return
            dataset_id = ds.dataset_id
        signal = dbc.get_cached_signal(signal_name, dataset_id)
        if not signal:
            return
        signal_id = signal.signal_id

        # Get all signal_data within the time interval ordered by time (ascending).
        # We have to take this data and batch all values that share a timestamp together (in increasing time order).
        with dbc.scope() as session:
            firstQ = self.time_filter(session.query(SignalData), None, [signal_id]).order_by(SignalData.time.asc())
            first = firstQ.first()
            if not first: # If there are no records, quit early.
                return
            
            lastQ = self.time_filter(session.query(SignalData), None, [signal_id]).order_by(SignalData.time.desc())
            last = lastQ.first()
            
            result.set_first(first.time)
            result.set_last(last.time)

    def fetch_signals(self, result, dataset_name, signal_names, interval, limit):
        if dataset_name is None:
            dataset_id = None
        else:
            ds = dbc.get_cached_dataset(dataset_name, error_on_not_found=False)
            if not ds:
                return
            dataset_id = ds.dataset_id
        signal_ids = list(map(lambda x: dbc.get_cached_signal(x, dataset_id).signal_id, signal_names))

        # Get all signal_data within the time interval ordered by time (ascending).
        # We have to take this data and batch all values that share a timestamp together (in increasing time order).
        with dbc.scope() as session:
            q = self.time_filter(session.query(SignalData), interval, signal_ids).order_by(SignalData.time.asc())
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
        if dataset_name is None:
            dataset_id = None
        else:
            ds = dbc.get_cached_dataset(dataset_name, error_on_not_found=False)
            if not ds:
                return
            dataset_id = ds.dataset_id
        signal_ids = list(map(lambda x: dbc.get_cached_signal(x, dataset_id).signal_id, signal_names))

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
                result.set(signal_name, self.time_filter(signal_datas, interval, signal_ids).scalar())

    def time_filter(self, query, interval, signal_ids):
        if interval:
            return query.filter(and_(SignalData.time >= interval.start, SignalData.time <= interval.end, SignalData.signal_id.in_(signal_ids)))
        else:
            return query.filter(and_(SignalData.signal_id.in_(signal_ids)))            

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

app = make_app()

if __name__ == '__main__':
    try:
        app.run(debug=DEBUG, port=3002, threaded=True)
    finally:
        dbc.engine.dispose()
