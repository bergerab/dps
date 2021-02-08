import threading
from datetime import datetime, timedelta
import time
import os
import pandas as pd

from flask import Flask, request, redirect, url_for
from yattag import Doc

import capture as cap
from html_helpers import render_page, div, a, title, button, table, navitem, ftable, quote
import html_helpers as hh
from influx import make_influxdb_client
from kpi import compute_battery_kpis

from models import PVAndWindModel, BatteryGeneratorAndFuelCellModel

app = Flask(__name__)

current_simulation = None
'''
The current (unfinished simulation).
'''

class Task:
    def __init__(self, name, status='Running'):
        self.name = name
        self.start = datetime.utcnow()
        self.end = None
        self.status = status

    def set_status(self, status):
        self.status = status

    def stop(self):
        self.end = datetime.utcnow()
        self.status = 'Completed'

class Warning:
    def __init__(self, name, resolution):
        self.name = name
        self.resolution = resolution
        self.time = datetime.utcnow()

load_tasks = []
simulation_tasks = []
batch_process_tasks = []
system_warnings = []
last_system_check = None
'''
The time of the last system health check.
'''

def show(x):
    if x is None:
        return '<i>None</i>'
    if isinstance(x, datetime):
        return str(x) + ' UTC'
    if isinstance(x, float):
        return str(round(x, 2)) + '%'
    return str(x)

@app.route('/')
def index(notifications=[]):
    check_system_health()

    doc, tag, text = Doc().tagtext()
    with tag('div', klass='box'):
        with tag('div', klass='box-header'):
            text('System Alerts')
            hh.help(doc, 'Shows critical system health information.')
        with tag('div', klass='box-body'):
            table(doc, ['Name', 'Details', 'Time'], [list(map(show, [x.name, x.resolution, x.time])) for x in reversed(system_warnings)])
    
    with tag('div', klass='box'):
        with tag('div', klass='box-header'):
            text('Load Log')
            hh.help(doc, 'Load tasks that have been made since the edge computer has been online.\nIncludes current running load tasks and their status.')
        with tag('div', klass='box-body'):
            table(doc, ['Name', 'Status', 'Progress', 'Start', 'End'], [list(map(show, [x.name, x.status, x.progress, x.start, x.end])) for x in reversed(load_tasks)])

    with tag('div', klass='box'):
        with tag('div', klass='box-header'):
            text('Simulation Log')
            hh.help(doc, 'Simulations that have been run since the edge computer has been online.\nIncludes currently running simulations.')            
        with tag('div', klass='box-body'):
            table(doc, ['Name', 'Status', 'Start', 'End'], [list(map(show, [x.name, x.status, x.start, x.end])) for x in reversed(simulation_tasks)])

    with tag('div', klass='box'):
        with tag('div', klass='box-header'):
            text('Batch Process Log')
            hh.help(doc, 'Batch processes that have been run since the edge computer has been online.\nIncludes currently running batch processes.')            
        with tag('div', klass='box-body'):
            table(doc, ['Name', 'Status', 'Start', 'End'], [list(map(show, [x.name, x.status, x.start, x.end])) for x in reversed(batch_process_tasks)])

    return render_page(doc, notifications=notifications)

@app.route('/batch')
def batch():
    notifications = []
    errors = []
    
    doc, tag, text = Doc().tagtext()

    target = request.args.get('name')

    start_time = request.args.get('start_time', (datetime.utcnow() - timedelta(hours=1)).strftime('%m/%d/%Y %H:%M:%S'))
    try:
        start_time = datetime.strptime(start_time, '%m/%d/%Y %H:%M:%S')
    except Exception as e:
        errors.append(str(e))
        start_time = datetime.utcnow()

    end_time = request.args.get('end_time', datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S'))
    try:
        end_time = datetime.strptime(end_time, '%m/%d/%Y %H:%M:%S')
    except Exception as e:
        errors.append(str(e))
        end_time = datetime.utcnow()

    if len(list(filter(lambda x: x.name == target and not x.end, batch_process_tasks))):
        errors.append('You must wait for the last batch process to complete before starting another.')

    if target and not errors:
        print(target, start_time, end_time)
        task = Task('Battery')
        def main():
            try: 
                client = make_influxdb_client(True)
                ret = compute_battery_kpis(client, start_time, end_time)
            except Exception as e:
                task.status = 'Error'
            task.stop()
        batch_process_tasks.append(task)
        t = threading.Thread(target=main, name='batch_process')
        t.start()
        return redirect(url_for('index'))                            

    with doc.tag('div', klass='box'):
        with doc.tag('div', klass='box-header'):
            doc.text('Batch Process')
            hh.help(doc, 'Process historical data in large quantities for later analysis.')
        with doc.tag('div', klass='box-body'):
            with doc.tag('form'):
                def render_select(doc):
                    with doc.tag('select', name='name', value=str(target)):
                        with doc.tag('option', value='battery'):
                            doc.text('Battery')

                def render_start_time(doc):
                    doc.stag('input', type='text', name='start_time', value=start_time.strftime('%m/%d/%Y %H:%M:%S'))
                    hh.help(doc, 'The time that the batch process begins processing from.')

                def render_end_time(doc):
                    doc.stag('input', type='text', name='end_time', value=end_time.strftime('%m/%d/%Y %H:%M:%S'))
                    hh.help(doc, 'The time that the batch process ends processing.')                    
                    
                ftable(doc, [
                    ['Name:', render_select],
                    ['Start Time (UTC):', render_start_time],
                    ['End Time (UTC):', render_end_time],
                    ['', lambda doc: doc.stag('input', type='submit', value='Run Batch Process')]
                ])
    
    return render_page(doc, notifications=notifications, errors=errors)

@app.route('/stream')
def stream():
    global current_simulation

    notifications = []
    errors = []
    
    target = request.args.get('name') # which simulation to run
    stream_kpis = request.args.get('stream-kpis') # which simulation to run
    stream_kpis = False if stream_kpis is None else bool(stream_kpis)
    stop = request.args.get('stop') # stops the simulation, if it is running
    
    doc, tag, text = Doc().tagtext()
    with doc.tag('div', klass='box'):
        with doc.tag('div', klass='box-header'):
            doc.text('Simulate')
            hh.help(doc, 'Start a Typhoon Virtual HIL simulation.\nNote: only one simulation can be run at once.')
        with doc.tag('div', klass='box-body'):
            if cap.running:
                if stop or (cap.cancel and cap.running):
                    cap.cancel = True
                    time.sleep(0.5) # TODO: horrible, horrible -- I didn't want to bother with this... The "Simulation Log" table wasn't showing that it was cancelled because there is some delay
                    return redirect(url_for('index'))                    
                else:
                    with tag('div', klass="row"):
                        doc.text('A simulation %s is running... To run another simulation, cancel this one, and start a new one.' % current_simulation.name)
                    button(doc, 'Stop Simulation', '?stop=1')
            elif target:
                def start(name, k):
                    global current_simulation
                    simulation = Task(name)
                    current_simulation = simulation
                    simulation_tasks.append(simulation)
                    cap.reset()
                    cap.stream_kpis = stream_kpis
                    def main():
                        k()
                        simulation.stop()
                    t = threading.Thread(target=main, name='ui_main')
                    t.start()
                if target == 'pv':
                    start('PV Array', lambda: cap.run(PVAndWindModel('pv')))
                elif target == 'wind':
                    start('Wind Turbine', lambda: cap.run(PVAndWindModel('wind')))
                elif target == 'batt_gen_fc':
                    start('Battery, Generator, and Fuel Cell', lambda: cap.run(BatteryGeneratorAndFuelCellModel()))            
                else:
                    errors.append('Was given an unsupported simulation target of %s.' % quote(target))
                    current_simulation = None
                    
                if current_simulation:
                    return redirect(url_for('index'))
            else:
                with doc.tag('form', method='GET'):
                    def main(doc):
                        with doc.tag('select', name='name'):
                            with doc.tag('option', value='pv'):
                                doc.text('PV Array')
                            with doc.tag('option', value='wind'):
                                doc.text('Wind Turbine')
                            with doc.tag('option', value='batt_gen_fc'):
                                doc.text('Battery, Generator, and Fuel Cell')
                    def checkbox(doc):
                        doc.stag('input', type='checkbox', name='stream-kpis', id='stream-kpis', checked=stream_kpis)
                        with doc.tag('label', klass='checkbox-label', **{ 'for': 'stream-kpis'}):
                            doc.text('Stream KPIs')
                        hh.help(doc, 'Whether or not to calculate KPIs during the capturing process.')
                    
                    ftable(doc, [
                        ['Name: ', main],
                        ['', checkbox],
                        ['', lambda doc: doc.stag('input', type='submit', value="Run Simulation")]])
    return render_page(doc, notifications=notifications, errors=errors)

def load_target_to_measurement_name(target):
    if target == 'Battery Charge':
        return 'battery_charge'
    elif target == 'Battery Discharge':
        return 'battery_discharge'
    else:
        raise Exception('Invalid load target')

@app.route('/database')
def database():
    target = request.args.get('target', None)
    
    doc, tag, text = Doc().tagtext()
    errors = []
    notifications = []    

    client = make_influxdb_client()
    if target == 'battery_kpi':
        client.drop_measurement('battery_kpi')
        notifications.append('Successfully removed all battery KPIs.')
    elif target == 'battery_signals':
        client.drop_measurement('battery_charge')
        client.drop_measurement('battery_discharge')
        notifications.append('Successfully removed all battery signals.')

    with tag('div', klass='box'):
        with tag('div', klass='box-header'):
            text('Database Maintenance - Delete Data')
            hh.help(doc, 'Remove old data from the database.')
        with tag('div', klass='box-body'):
            with tag('form', method='GET'):
                def render_select(doc):
                    with doc.tag('select', name='target', value=str(target)):
                        with doc.tag('option', value='battery_signals'):
                            doc.text('Battery Signals')
                        with doc.tag('option', value='battery_kpi'):
                            doc.text('Battery KPIs')

                rows = []
                rows.append(['Data:', render_select])
                rows.append(['', lambda doc: doc.stag('input', type='submit', value='Delete Data')])                
                ftable(doc, rows)

    return render_page(doc, errors=errors, notifications=notifications)

@app.route('/load')
def load():
    target = request.args.get('target')
    
    doc, tag, text = Doc().tagtext()
    errors = []

    with tag('div', klass='box'):
        with tag('div', klass='box-header'):
            text('Data Loading')
            if target:
                text(' - ' + target)
            else:
                hh.help(doc, 'Load test data for components of the system for batch analysis.')
        with tag('div', klass='box-body'):
            if target:
                if target == 'Battery Charge' or target == 'Battery Discharge':
                    filepath = request.args.get('filepath', None)
                    if filepath and not os.path.exists(filepath):
                        errors.append('File Path %s doesn\'t exist on this Edge Computer.' % quote(filepath))
                    
                    time = request.args.get('time', datetime.utcnow().strftime('%m/%d/%Y %H:%M:%S'))
                    try:
                        time = datetime.strptime(time, '%m/%d/%Y %H:%M:%S')
                    except Exception as e:
                        errors.append(str(e))
                        time = datetime.utcnow()
                        
                    time_index = int(request.args.get('time-index', 0))
                    current_index = int(request.args.get('current-index', 1))
                    voltage_index = int(request.args.get('voltage-index', 2))
#                    soc_index = int(request.args.get('soc-index', 3))
                    
                    task = Task(target)
                    task.count = 0 # keep the count of how many rows have been processed
                    task.progress = 0.0
                    
                    df = None
                    if filepath:
                        if errors:
                            pass
                        else:
                            try:
                                def main():
                                    try:
                                        csv = pd.read_csv(filepath, dtype='float16')
                                        line_count = len(csv)
                                        
                                        columns = list(csv.columns)
                                        columns[time_index] = 'Time'
                                        columns[current_index] = 'Current'
                                        columns[voltage_index] = 'Voltage'
#                                        columns[soc_index] = 'SOC'
                                        
                                        client = make_influxdb_client()
                                        measurement = load_target_to_measurement_name(target)
                                        chunksize = 500000
                                        for df in pd.read_csv(filepath, chunksize=chunksize):
                                            df.columns = columns
                                            task.count += len(df)
                                            
                                            dates = []
                                            for index, value in df['Time'].items():
                                                dates.append(time + timedelta(seconds=value))
                                            df = df.set_index(pd.DatetimeIndex(dates))
#                                            df = df.resample('1ms').mean() # downsample -- only take every second
                                            ret = client.write_points(df, measurement, batch_size=chunksize)
                                            task.progress = (task.count / line_count) * 100
                                            
                                        task.stop()
                                    except Exception as e:
                                        task.stop()                                        
                                        task.status = 'Error'
                                        raise e

                                    
                                t = threading.Thread(target=main, name='load_task')
                                t.start()
                            except Exception as e:
                                errors.append(str(e))

                    if not errors and len(list(filter(lambda x: x.name == target and not x.end, load_tasks))):
                        text('A %s load task is already running. You have you wait for it to complete before starting a new one.' % target)
                    elif not errors and filepath: # if we got input
                        load_tasks.append(task)
                        return redirect(url_for('index'))
                    else:
                        rows = []
                        
                        def render_file_path(doc):
                            doc.stag('input', type='text', name='filepath', style='width: 400px;', required='required', value='' if filepath is None else filepath)
                            hh.help(doc, 'The filepath (on the edge computer) of the data.')                                                                                

                        rows.append(['File Path:', render_file_path])
                        
                        def render_start_time(doc):
                            doc.stag('input', type='text', name='time', required='required', value=time.strftime('%m/%d/%Y %H:%M:%S'), style='width: 300px;')
                            hh.help(doc, 'The time that the data was captured -- make sure charge/discharge data have the same start time.')                                                    
                        rows.append(['Data Start Time (UTC):', render_start_time])

                        def render_time_index(doc):
                            doc.stag('input', type='number', required="required", name='time-index', value=time_index)
                            hh.help(doc, 'The (zero-indexed) column index of the capture time from the input file.\nTime must be in delta seconds since the beginning of the capture.')
                        
                        rows.append(['Indicies:', lambda doc: ftable(doc, [
                            ['Time:', render_time_index],
                            ['Current:', lambda doc: doc.stag('input', type='number', required="required", name='current-index', value=current_index)],
                            ['Voltage:', lambda doc: doc.stag('input', type='number', required="required", name='voltage-index', value=voltage_index)],
#                            ['State of Charge:', lambda doc: doc.stag('input', type='number', required="required", name='soc-index', value=soc_index)],                        
                        ])])                    

                        with tag('form', method='GET'):
                            doc.stag('input', type='hidden', name='target', value=target)
                            rows.append(['', lambda doc: doc.stag('input', type='submit', value='Load Data')])
                            ftable(doc, rows)
                else:
                    error(doc, 'Was given an unsupported load target of %s.' % quote(target))
            else:
                with tag('div', klass='vbox'):
                    with tag('div', klass='buttons'):                    
                        button(doc, 'Battery Charge', '?target=Battery Charge')
                        button(doc, 'Battery Discharge', '?target=Battery Discharge')

    # Should lead to page that asks for a local filepath on the system where
    # both charge and discharge files are present
    return render_page(doc, errors=errors)

@app.route('/visualize')
def visualize():
    doc, tag, text = Doc().tagtext()

    with tag('div', klass='box'):
        with tag('div', klass='box-header'):
            text('Grafana Visualizations')
            hh.help(doc, 'Links to visualizations hosted in a local Grafana server.')
        with tag('div', klass='box-body'):
            with tag('div', klass='vbox'):
                with tag('div', klass='buttons'):
                    button(doc, 'PV Array', 'http://localhost:3000/d/9pZaPZgGk/pv-array', target='blank')
                    button(doc, 'Wind Turbine', 'http://localhost:3000/d/o4KViNgGz/wind-turbine', target='blank')
                    button(doc, 'Transformer', 'http://localhost:3000/d/XIe2niGGz/transformer', target='blank')
                    button(doc, 'Generator', 'http://localhost:3000/d/HC3JeIRMk/diesel-generator-800', target='blank')
                    button(doc, 'Fuel Cell', 'http://localhost:3000/d/uqB1CSgMk/fuel-cell', target='blank')
                    button(doc, 'Battery', 'http://localhost:3000/d/Xvm96uZMz/battery', target='blank')
    
    return render_page(doc)

def add_warning(warning):
    # Name has to be unique
    if len(list(filter(lambda x: x.name == warning.name, system_warnings))) > 0:
        return
    system_warnings.append(warning)

def remove_warning(name):
    global system_warnings
    system_warnings = list(filter(lambda x: x.name != name, system_warnings))

def check_system_health():
    
    def check():
        global last_system_check
        
    
        # debounce
        if last_system_check and (datetime.utcnow() - last_system_check).total_seconds() < 10:
            return

        last_system_check = datetime.utcnow()
        influx_warning_name = 'Lost InfluxDB Connectivity'
        try:
            client = make_influxdb_client()                
            ret = client.ping()
            remove_warning(influx_warning_name)
        except Exception as e:
            add_warning(Warning(influx_warning_name, 'Ensure InfluxDB is configured correctly, that the server is online, and accessible.\nNo data can be captured, loaded, or queried until this is resolved.'))

    t = threading.Thread(target=check, name='system_health_check')
    t.start()
    
if __name__ == '__main__':
    app.run(debug=True)
