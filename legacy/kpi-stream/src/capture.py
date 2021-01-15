'''
Threaded implementation of the data analytics platform.

Three threads are used: ~capture~, ~send~, and ~analyze~.

Data is captured from Typhoon HIL in the ~capture~ thread,
then the raw data is sent to InfluxDB via ~send~, and finally,
KPIs are computed on the raw data via ~analyze~.

This code is _not_ thread-safe. Meaning you cannot run two
instances of this code at once. In the current version of Typhoon HIL,
it wouldn't be helpful it if was thread-safe anyway. This is because
Typhoon HIL only allows running one simulation on a computer at once.
If you want to run two Typhoon simulations, you would need two computers.
That would make the effort of creating a thread-safe Python driver
useless because that is simply not a use-case.
'''

import time
import threading
from datetime import datetime, timedelta

from influx import make_influxdb_client, load_file_to_influxdb, InfluxStream
from config import typhoon_path

import pandas as pd

from dataframe_stream import DataFrameStream
from models import PVAndWindModel

capture_ready = threading.Event()
'''
Event that indicates a capture was taken from Typhoon and can be sent
to InfluxDB.
'''

analysis_ready = threading.Event()
'''
Event that indicates raw signal data was sent to InfluxDB, and is ready
to be used for KPI computations.
'''

cancel = False
'''
Global cancellation token for ~capture~, ~send~, and ~analyze~ threads.
'''

previous_capture = None
'''
The ~capture~ thread keeps a buffer of one capture so that we can process
the last batch of data while we are capturing the next batch of data.
'''

current_capture = None
'''
The latest CaptureData for the last capture from Typhoon.
'''

analysis_queue = []
'''
A copy of the captures that have yet to be processed.
'''

model = None
'''
A Typhoon HIL configuration used for listing which signals to capture
and some simulation initialization.
'''

verbose = True
'''
Indicates if logging should actually print to stdout or be silenced.
'''

running = False
'''
Indicates of a simulation is running.
'''

on_end = lambda: None
'''
A function that is called when the simulation completes.
'''

stream_kpis = True
'''
Whether or not to compute KPIs, or just capture signals.
'''

def reset():
    '''
    Resets the globals to their initial state
    '''
    global capture_ready
    capture_ready = threading.Event()
    global analysis_ready
    analysis_ready = threading.Event()
    global cancel
    cancel = False
    global previous_capture
    previous_capture = None
    global current_capture
    current_capture = None
    global analysis_queue
    analysis_queue = []
    global model
    model = None
    global running
    running = False
    global on_end
    on_end = lambda: None
    global stream_kpis
    stream_kpis = True

def capture():
    '''
    A thread that captures data from the given Typhoon model
    and puts the data into shared variable ~previous_capture~
    for the other threads to handle.
    '''

    def quit():
        '''
        Fakes that the capture was successful (so the ~capture~ thread gains control
        so it can quit itself). Then stops the simulation.
        '''
        global cancel
        cancel = True
        capture_ready.set()
        model.stop()

    def receive(capture):
        global current_capture
        global previous_capture
        
        if not capture:
            log('capture: Typhoon Python API didn\'t send a capture. Exiting...')
            quit()
            return False
        
        log('capture: Ended new capture at ', datetime.fromtimestamp(capture.end_time // 1000000000).strftime('%Y-%m-%d %H:%M:%S'))
       
        if previous_capture:
            log('capture: set capture ready')
            current_capture = capture
            capture_ready.set()
        else:
            previous_capture = capture
            
        return True
    
    def stop(force=None):
        '''
        Checks if this thread was killed, if so print debug message and stop simulation.
        '''
        if check_quit('capture') or force == True: 
            quit()
            return
    
    model.start(receive, stop)

def send():
    '''
    A thread that sends data from shared variable ~previous_capture~
    and sends it to InfluxDB (configured via ~src/config.json~).
    '''
    global previous_capture

    while True:
        log('send: waiting for capture to complete...')
        capture_ready.wait()
        if check_quit('send'): 
            analysis_ready.set()
            return
        log('send: capture is complete.')

        previous_capture.prepare_data()
        if stream_kpis:
            analysis_queue.append(previous_capture.df)
        analysis_ready.set()

        previous_capture.send(current_capture)

        log('send: setting previous_capture')
        previous_capture = current_capture
        capture_ready.clear()

def analyze():
    '''
    A thread that performs the KPI calculations.
    '''
    while True:
        if len(analysis_queue) == 0:
            '''
            If there's no data in the queue, wait for data to arrive.
            '''
            analysis_ready.clear()
            log('analyze: waiting for analysis_queue...')
            analysis_ready.wait()
        if check_quit('analyze'): return
        df = analysis_queue.pop(0)
        log('analyze: analyzing batch...')

        before = time.time_ns()

        output = model.process(df)
        for measurement, df in output:
            df = df.set_index(pd.DatetimeIndex(df['Time']))
            client = make_influxdb_client()
            ret = client.write_points(df, measurement, batch_size=20000)
        
        log('ANALYZE: after ', time.time_ns() - before)

        log('analyze: sent batch to influxdb.')

def check_quit(name):
    '''
    Check cancellation token ~cancel~.
    If cancelling, logs the name of the thread that is being killed.
    '''
    if cancel:
        log(name + ': quitting...')
        return True
    return False

def run(requested_model):
    '''
    Starts three threads: ~capture~, ~send~, and ~analyze~.

    Capture captures data from the given Typhoon HIL model ~model~
    and sends it to both ~send~ and ~analyze~.

    In parallel, ~send~ and ~analyze~ execute.

    ~send~ sends the raw signal data to InfluxDB.
    ~analyze~ performs the KPI calculations on the raw signal
    data, then sends the result to InfluxDB.
    '''
    
    global cancel
    global model
    global running

    running = True

    model = requested_model
    '''
    Tell the threads which model to use for KPI computations.
    '''

    t1 = threading.Thread(target=capture, name='capture')
    t2 = threading.Thread(target=send, name='send')
    if stream_kpis:
        t3 = threading.Thread(target=analyze, name='analyze')

    t1.start()
    t2.start()
    if stream_kpis:
        t3.start()

    try:
        '''
            Keeps the thread that reads keyboard input from becoming blocked.
            Allows Python to pick up a SIGINT while joining threads.
        '''
        while threading.active_count() > 0:
            if cancel:
                log('main: quitting...')
                return
            time.sleep(0.5)
    except KeyboardInterrupt:
        cancel = True
        log('main: killing child threads...')
    finally:
        running = False
        on_end()

def log(*msgs):
    '''
    Logs the messages ~msgs~ if the printing mode ~verbose~ is true.
    '''
    if verbose:
        print(*msgs)

if __name__ == '__main__':
    run(PVAndWindModel('wind'))
