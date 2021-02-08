from sys import argv, exit
from dateutil import parser
from datetime import datetime
import asyncio
import threading
import time

from kpi import PV_Array

from influx import make_influxdb_client, load_file_to_influxdb, InfluxStream

from dataframe_stream import Stream

modes = [
    'load',
    'stream',
    'async_stream',
    'async_kpi_stream',    
    'kpi_stream',
    'capture',
]

kpis = {
    'pv_array': PV_Array
}

def ensure(condition, message):
    if not condition:
        print(message)
        exit(1)

def parse_date(s):
    if s in ['today', 'now']:
        return datetime.utcnow()
    return parser.parse(s)

if __name__ == '__main__':
    ensure(len(argv) > 1, 'You need to specify a mode as the first argument.')
    
    mode = argv[1].lower()

    ensure(mode in modes, mode + ' is not a valid mode. Valid modes are: ' + ', '.join(modes))

    if mode == 'capture':
        import capture
        capture.main()
        #t1 = threading.Thread(target=capture.main, name='capture_and_send') 

        #t1.start()

        #try:
        #    while threading.active_count() > 0:
        #        time.sleep(0.5)
        #except KeyboardInterrupt:
        #    capture.cancel = True
        #    print('Killing child threads...')
    if mode == 'load':
        ensure(len(argv) > 5, 'You must specify the measurement name, start time, the duration (in ms), then at least one path')

        measurement = argv[2]
        start_time = parse_date(argv[3])
        duration = argv[4]
        paths = argv[5:]

        client = make_influxdb_client()
        for path in paths:
            load_file_to_influxdb(client, measurement, path, start_time, duration)

        print('OK')
    elif mode == 'stream':
        ensure(len(argv) > 3, 'You must specify a measurement, and a start time.')

        measurement = argv[2]
        start_time = parse_date(argv[3])

        client = make_influxdb_client()        
        influx_stream = InfluxStream(client, measurement, start_time, None, None)
        gen = influx_stream.get_gen()
        for df in gen():
            print(df)
    elif mode == 'async_stream':
        ensure(len(argv) > 3, 'You must specify a measurement, and a start time.')

        measurement = argv[2]
        start_time = parse_date(argv[3])

        client = make_influxdb_client()        
        influx_stream = InfluxStream(client, measurement, start_time, None, 1.0)
        gen = influx_stream.get_async_gen()

        async def run():
            async for df in gen():
                print(df)
                
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())
    elif mode == 'async_kpi_stream':
        ensure(len(argv) > 3, 'You must specify a kpi name, a measurement, and a start time.')

        kpi_name = argv[2]
        measurement = argv[3]
        start_time = parse_date(argv[4])

        ensure(kpi_name in kpis, 'Given KPI ' + kpi_name + ' is not supported. Supported KPIs: ' + ', '.join(kpis))

        Kpi = kpis[kpi_name]

        client = make_influxdb_client()
        influx_stream = InfluxStream(client, measurement, start_time, None, 1.0, ['Time', 'Imp', 'Vmp', 'Idc', 'Vdc'])

        async def run():
            asyncio.create_task(influx_stream.async_run())
            gen = influx_stream.chan.get_gen()
            async for row in gen():
                print(row)
                
        loop = asyncio.get_event_loop()
        
        def wakeup():
            '''
            Hack for asyncio on windows where SIGINT wouldn't register
            '''
            loop.call_later(0.5, wakeup)
        loop.call_later(0.5, wakeup)        
        loop.run_until_complete(run())

        IV = Stream(gen)
        kpi_stream = Kpi().run(IV)
        kpi_stream.stream_plot(0.1, [0,1])
    elif mode == 'kpi_stream':
        ensure(len(argv) > 3, 'You must specify a kpi name, a measurement, and a start time.')

        kpi_name = argv[2]
        measurement = argv[3]
        start_time = parse_date(argv[4])

        ensure(kpi_name in kpis, 'Given KPI ' + kpi_name + ' is not supported. Supported KPIs: ' + ', '.join(kpis))

        Kpi = kpis[kpi_name]

        client = make_influxdb_client()
        influx_stream = InfluxStream(client, measurement, start_time, None, None, ['Time', 'Imp', 'Vmp', 'Idc', 'Vdc'])
        gen = influx_stream.get_gen()

        IV = Stream(gen)
        kpi_stream = Kpi().run(IV)
        kpi_stream.stream_plot(0.1, [0,1])
        
