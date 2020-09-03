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
        engine = create_engine(CONNECTION)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        # Caches for datasets and signals
        self.datasets = self.query(Dataset).all()
        self.signals = self.query(Signal).all()

    def get_dataset_by_name(self, dataset_name):
        for dataset in self.datasets:
            if dataset.name.strip() == dataset_name:
                return dataset
        return None

    def get_signal_by_name(self, signal_name):
        for signal in self.signals:
            if signal.name.strip() == signal_name:
                return signal
        return None

    def commit(self):
        self.session.commit()

    def query(self, cls):
        return self.session.query(cls)

    def add(self, obj):
        # Not perfect - if commit fails, the cache doesn't rollback
        if isinstance(obj, Dataset):
            self.datasets.append(obj)
        if isinstance(obj, Signal):
            self.signals.append(obj)
        return self.session.add(obj)
