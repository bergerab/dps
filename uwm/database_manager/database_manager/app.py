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
        if dataset is None:
            dataset = Dataset(name=dataset_name)
            self.dbc.add(dataset)
            self.dbc.commit()

        signals = []
        for signal_name in signal_names:
            signal = dbc.get_signal_by_name_and_dataset_id(signal_name, dataset.dataset_id)
            if signal is None:
                signal = Signal(dataset_id=dataset.dataset_id, name=signal_name)
                self.dbc.add(signal)
                self.dbc.commit()
            signals.append(signal)
            
        for i, batch in enumerate(batches):
            for j, sample in enumerate(batch):
                time = times[i]
                signal = signals[j]
            
                signal_data = SignalData(signal_id=signal.signal_id, value=sample, time=time)
                self.dbc.add(signal_data)
                self.dbc.commit()

    def fetch_signals(self, result, dataset_name, signal_names, interval):
        signal_values = self.time_filter(self.dbc.query(SignalData), interval).all()

    def aggregate_signals(self, result, dataset_name, signal_names, interval, aggregation):
        f = None
        if aggregation == 'max':
            f = func.max
        elif aggregation == 'min':
            f = func.min
        elif aggregation == 'average':
            f = func.avg
        else:
            raise Exception(f'aggregate_signals was given an unsupported aggregation of "{aggregation}".')
        val = self.time_filter(self.dbc.query(f(SignalData.value)), interval).scalar()

    def time_filter(self, query, interval):
        return query.filter(and_(SignalData.time >= interval.start, SignalData.time <= interval.end))
        
def make_app():
    app = dbm.make_app(TimescaleDBDataStore)

    # For integration testing, expose an endpoint to clear all data.
    if DEBUG:
        @app.route(util.make_api_url('clear'), methods=['POST'])
        @util.json_api        
        def clear(jo):
            dataset_name = jo['dataset_name']
            dbc = DatabaseClient()
            dbc.clear(dataset_name)
            return True
    
    return app

if __name__ == '__main__':
    make_app().run(debug=DEBUG, port=3001)
