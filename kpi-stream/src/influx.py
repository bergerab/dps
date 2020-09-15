from config import CONFIG
import pandas as pd
from influxdb import DataFrameClient, InfluxDBClient
from datetime import datetime, timedelta
import time
import asyncio

def make_influxdb_client(regular=False):
    database = CONFIG['INFLUXDB_DATABASE']

    if regular:
        client = InfluxDBClient(host=CONFIG['INFLUXDB_HOST'], port=CONFIG['INFLUXDB_PORT'], database=database)
    else:
        client = DataFrameClient(host=CONFIG['INFLUXDB_HOST'], port=CONFIG['INFLUXDB_PORT'], database=database)
    client.create_database(database)
    return client

def load_file_to_influxdb(client, measurement, filepath, start_time, duration):
    '''
    This is an old function that I'm keeping around in case we need it
    it was from before we used Typhoon directly to get data.
    
    start_time specifies when the data started being collected
    duration specifies how much time the CSV represents (in milliseconds)
    '''
    df = pd.read_csv(filepath)
    
    duration = float(duration) # not sure why i need this
    time = start_time
    for i, row in df.iterrows():
        offset = (i / len(df)) * duration

        time += timedelta(milliseconds=offset)
        df.at[i, 'Time'] = time
        if i % 1000 == 0:
            print(i)

    print(df)
    df = df.set_index(pd.DatetimeIndex(df['Time']))
    ret = client.write_points(df, measurement, batch_size=100000)
    print(ret)

def format_time(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S.000000000')

class InfluxStream:
    def __init__(self, client, measurement, start_time, sample_rate, data_rate=1.0, columns=None):
        '''
        start_time => where to start in the data
        data_rate => 1 is realtime, 2 is twice realtime, 0.5 is half realtime 
        sample_rate => the sample rate of the data in the database
        '''
        self.client = client
        self.measurement = measurement
        self.start_time = start_time
        self.sample_rate = sample_rate
        self.data_rate = data_rate
        self.columns = columns

        self.stream_time = self.start_time

        # This channel is only relevant for async influx streams
        self.chan = BufferedChannel()

    def get_gen(self):
        return self.sync_run

    def get_async_gen(self):
        return self.async_run

    def prepare_query(self):
        before_time = self.stream_time
        self.stream_time += timedelta(seconds=1)
        query = f'select * from {self.measurement} where CaptureTime >= \'{format_time(before_time)}\' and CaptureTime < \'{format_time(self.stream_time)}\''
        print(query)
        return query

    def run_query(self):
        dict = self.client.query(self.prepare_query())
        return dict

    def validate_columns(self, df):
        for col in self.columns:
            if col not in df.columns:
                raise Exception('Expected to find a column named "' + col + '" in the DataFrame, but didn\'t find it.')

    async def async_run(self):
        while True:
            before_query = int(round(time.time() * 1000))
            dict = self.run_query()
            query_duration = int(round(time.time() * 1000)) - before_query

            if len(dict) < 1:
                print('no data')
            else:
                df = list(dict.values())[0]

                # if given columns, yield each row, otherwise yield each dataframe
                if self.columns:
                    self.validate_columns(df)
                    df = df[self.columns]
                    self.chan.put(df)
                else:
                    self.chan.put(df)                    

            sleep_duration = 1/self.data_rate
            await asyncio.sleep(sleep_duration - (query_duration/1000.0))

    def sync_run(self):
        while True:
            dict = self.run_query()

            if len(dict) < 1:
                print('no data')
            else:
                df = list(dict.values())[0]

                # if given columns, yield each row, otherwise yield each dataframe
                if self.columns:
                    self.validate_columns(df)
                    df = df[self.columns]
                    rows = df.values.tolist()                                
                    for row in rows:
                        yield row
                else:
                    yield df
                    

class BufferedChannel:
    def __init__(self):
        self.buffer = []
        self.subscribers = []

    def put(self, value):
        if self.subscribers:
            while self.subscribers:
                self.subscribers.pop().set_result(value)
        else:
            self.buffer.append(value) # everything will be in the wrong order

    def get(self):
        future = asyncio.Future()        
        if self.buffer:
            value = self.buffer.pop()
            future.set_result(value)
        else:
            self.subscribers.append(future)
        return future

    def get_gen(self):
        async def gen():
            while True:
                df = await self.get()
                rows = df.values.tolist()
                for row in rows:
                    yield row

        return gen
