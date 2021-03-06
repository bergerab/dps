from contextlib import contextmanager

from sqlalchemy import create_engine, Table, Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import psycopg2
from psycopg2.pool import SimpleConnectionPool        

from config import CONNECTION

Base = declarative_base()

class Dataset(Base):
    __tablename__ = 'datasets'
    dataset_id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)

class Signal(Base):
    __tablename__ = 'signals'
    signal_id = Column(Integer, primary_key=True)
    name = Column(String(200))
    dataset_id = Column(Integer, ForeignKey('datasets.dataset_id'))

class SignalData(Base):
    __tablename__ = 'signal_data'
    signal_id = Column(Integer, ForeignKey('signals.signal_id'), primary_key=True)
    value = Column(Float())
    time = Column(DateTime(), primary_key=True)

class DatabaseClient:
    def __init__(self):
        self.engine = create_engine(CONNECTION, echo=False)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)

        # Keep a direct database driver connection for inserts (high speed)
        self.psycopg2_connpool = SimpleConnectionPool(1, 10, dsn=CONNECTION)

        # Keep caches for datasets and signals to avoid database lookups.
        self.cache()

    def cache(self):
        with self.scope() as session:
            self.signals = session.query(Signal).all()
            self.datasets = session.query(Dataset).all()            

    def get_cached_signal(self, signal_name, dataset_id):
        def lookup():
            for signal in self.signals:
                if signal.name == signal_name and (dataset_id is None or signal.dataset_id == dataset_id):
                    return signal
        signal = lookup()
        if signal:
            return signal
        # If signal not found in cache, refresh the cache.
        self.cache()
        signal = lookup()
        if signal:
            return signal
        # If the signal is still not found, error.
        raise Exception(f'Signal "{signal_name}" does not exist.')

    def get_cached_dataset(self, dataset_name, filter_func=None, error_on_not_found=True):
        if filter_func is None:
            filter_func = lambda dataset, name: dataset.name == dataset_name
        def lookup():
            for dataset in self.datasets:
                if filter_func(dataset, dataset_name):
                    return dataset
        dataset = lookup()
        if dataset:
            return dataset
        # If signal not found in cache, refresh the cache.
        self.cache()        
        dataset = lookup()
        if dataset:
            return dataset
        # If the signal is still not found, error.
        if error_on_not_found:
            raise Exception(f'Dataset "{dataset_name}" does not exist.')

    def get_dataset_by_name(self, dataset_name):
        for dataset in self.datasets:
            if dataset.name == dataset_name:
                return dataset
        return None

    def get_signal_by_name_and_dataset_id(self, signal_name, dataset_id):
        for signal in self.signals:
            if signal.dataset_id == dataset_id and signal.name == signal_name:
                return signal
        return None

    def delete_dataset(self, dataset_name):
        with self.scope() as session:
            dataset = session.query(Dataset).filter_by(name=dataset_name).first()
            if not dataset:
                return
            signals = session.query(Signal).filter_by(dataset_id=dataset.dataset_id).all()
            for signal in signals:
                session.query(SignalData).filter_by(signal_id=signal.signal_id).delete()
            session.query(Signal).filter_by(dataset_id=dataset.dataset_id).delete()
            session.delete(dataset)
            session.commit()
            
            # Refresh the caches.
            self.cache()

    def scope(self):
        return session_scope(self.Session)

    def add(self, session, obj):
        # Not perfect - if commit fails, the cache doesn't rollback.
        if isinstance(obj, Dataset):
            self.datasets.append(obj)
        if isinstance(obj, Signal):
            self.signals.append(obj)
        return session.add(obj)

@contextmanager
def session_scope(Session):
    # Required expire_on_commit=False to support caching.
    session = Session(expire_on_commit=False)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class UpsertQuery:
    def __init__(self, table_name, selector_fields, setter_fields):
        self.table_name = table_name
        self.selector_fields = selector_fields
        self.setter_fields = setter_fields

        sql_template = '''
            WITH updates AS (
                UPDATE %(target)s t
                    SET %(set)s        
                FROM source s
                WHERE %(where_t_pk_eq_s_pk)s 
                RETURNING %(s_pk)s
            )
            INSERT INTO %(target)s (%(columns)s)
                SELECT %(source_columns)s 
                FROM source s LEFT JOIN updates t USING(%(pk)s)
                WHERE %(where_t_pk_is_null)s
        '''
        self.query = sql_template % dict(
            target = table_name,
            set = ',\n'.join(["%s = s.%s" % (x,x) for x in setter_fields]),
            where_t_pk_eq_s_pk = ' AND '.join(["t.%s = s.%s" % (x,x) for x in selector_fields]),
            s_pk = ','.join(["s.%s" % x for x in selector_fields]),
            columns = ','.join([x for x in selector_fields+setter_fields]),
            source_columns = ','.join(['s.%s' % x for x in selector_fields+setter_fields]), 
            pk = ','.join(selector_fields),
            where_t_pk_is_null = ' AND '.join(["t.%s IS NULL" % x for x in selector_fields]),
            t_pk = ','.join(["t.%s" % x for x in selector_fields]))

        self.create_temp_table_sql = 'CREATE TEMP TABLE source(LIKE %s INCLUDING ALL) ON COMMIT DROP;' % table_name

    def execute(self, cursor, data):
        cur = cursor
        cur.execute(self.create_temp_table_sql);  
        cur.copy_from(data, 'source', columns=self.selector_fields + self.setter_fields)
        cur.execute(self.query)
        cur.execute('DROP TABLE source')
        data.close()
