from contextlib import contextmanager

from sqlalchemy import create_engine, Table, Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    signal_data_id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey('signals.signal_id'))
    value = Column(Float())
    time = Column(DateTime())

class DatabaseClient:
    def __init__(self):
        self.engine = create_engine(CONNECTION)
        self.Session = sessionmaker(bind=self.engine)

        # Keep caches for datasets and signals to avoid database lookups.
        self.cache()

    def cache(self):
        with self.scope() as session:
            self.signals = session.query(Signal).all()
            self.datasets = session.query(Dataset).all()            

    def get_cached_signal(self, signal_name):
        def lookup():
            for signal in self.signals:
                if signal.name == signal_name:
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

    def get_cached_dataset(self, dataset_name):
        def lookup():
            for dataset in self.datasets:
                if dataset.name == dataset_name:
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
