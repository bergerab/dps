import time

import numpy as np
import pandas as pd

from influx import make_influxdb_client

class CaptureData:
    def __init__(self, signal_names):
        self.start_time = None
        self.end_time = None
        self.x_data = None
        self.y_data_matrix = None
        self.df = None
        self.duration = 0
        self.signal_names = signal_names

    def start(self):
        self.start_time = time.time_ns()        
        return self

    def end(self, x_data, y_data_matrix):
        self.x_data = x_data
        self.y_data_matrix = y_data_matrix
        self.end_time = time.time_ns()        
        return self

    def set_capture_time(self, next_capture):
        # Add capture time to indicate when this data was captured (different than what time the data actually represents)
        capture_times = []
        #duration = next_capture.start_time - self.start_time
        duration = self.end_time - self.start_time
        step = (1 / self.df.shape[0]) * duration

        capture_time = self.start_time
        for i in range(self.df.shape[0]):
            capture_time += step
            capture_times.append(capture_time)

        self.df['SimTime'] = self.df['Time']
        self.df['Time'] = capture_times
        self.df = self.df.set_index(pd.DatetimeIndex(self.df['Time']))

    def prepare_data(self):
        data = dict(zip(['Time'] + self.signal_names, np.concatenate((np.array([list(self.x_data)]), self.y_data_matrix))))
        self.df = pd.DataFrame.from_dict(data)
        self.set_capture_time(None)

    def send(self, next_capture):
        if self.df is None:
            self.prepare_data()
        client = make_influxdb_client()
        ret = client.write_points(self.df, 'signals', batch_size=10000)
