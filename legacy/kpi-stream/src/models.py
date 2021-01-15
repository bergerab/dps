import numpy as np

import time
import threading

import typhoon.api.hil as hil

import config
from hil_util import *
import signals as s
from capture_data import CaptureData
from kpi import PV_Array, FuelCell, DieselGenerator, WindTurbine, Battery, Transformer

class Model:
    '''
    A wrapper around the Typhoon HIL API.

    Provides a model (electrical system simulation) that can be started,
    and stopped. Does the initialization and error handling automatically.
    '''
    def __init__(self, signals=[], path=None):
        '''
        signals: a list of signal names (strings)
        '''
        self.signals = signals
        self.path = path
    
    def initialize(self):
        '''
        Models require setting up some system configuration
        (for example setting a source sine waveform, turning on inverters, etc...)
        '''
        raise Exception('Model initialization unimplemented.')

    def start(self, f, stop):
        '''
        path: path to the .cpd file for this model (provided by compiling a Typhoon schematic)
        '''
        success = hil.load_model(file=self.path, offlineMode=False, vhil_device=True)
        if not success:
            stop(True)
            self.stop()
            raise Exception('Error when attempting to load compiled Typhoon model %s' % self.path)
        hil.start_simulation()
        self.on_start()
        self.initialize()
        self._capture(f, stop)

    def on_start(self):
        '''
        I didn't want to mess with calling super.start() from derived classes,
        instead just override on_start to hook into the model starting.

        This is useful for starting a counter when the simulation starts.
        '''
        pass

    def _capture(self, f, stop):
        '''
        f: function that takes the capture -- returns true or false if it processed the capture successfully
        stop: function that runs while the capture is running -- if it returns true, the capture will stop
        '''
        trigger_settings = ['Forced']
        channel_settings = self.signals
        
        SAMPLES = 1000
        
        capture_settings = [100, len(channel_settings), SAMPLES]
        '''
        decimation, number of channels, number of samples
        
        This configures Typhoon to capture ~SAMPLES~ samples before returning a batch.
        Decimation means how many time steps to skip sampling when gathering a single sample.
        Typhoon runs a simulation with some fixed time step. Decimation is how many time steps
        per sample taken.
        
        In Typhoon, you cannot capture based on a simulation time window. It only allows to specify
        how many samples per batch.
        '''
        
        while True:        
            captured_data = []

            capture = CaptureData(channel_settings)
            if hil.start_capture(capture_settings,
                                 trigger_settings,
                                 channel_settings,
                                 dataBuffer=captured_data):
                capture.start()

                while hil.capture_in_progress():
                    if stop():
                        self.stop()
                        return

                success = False
                if not captured_data:
                    success = f(None)
                else:
                    (signal_names, y_data_matrix, x_data) = captured_data[0]                    
                    capture.end(x_data, y_data_matrix)
                    success = f(capture)
                
                if not success:
                    return
            else:
                stop(True)
                self.stop()
                raise Exception("Unable to start capture process.")

    def stop(self):
        hil.stop_simulation()
        self.on_stop()

    def on_stop(self):
        '''
        Useful for cleaning up any threads that are specific for this model.
        '''
        pass
    
class PVAndWindModel(Model):
    def __init__(self, switch='both'):
        '''
        ~switch~ controls if we should run both the Wind and PV KPIs or just one of them
        you can set it to 'pv' or 'wind' to just run those KPIs
        '''
        
        signals = []
        if switch == 'both' or switch == 'wind':
            signals += s.WD_SIGNALS
        if switch == 'both' or switch == 'pv':
            signals += s.PV_SIGNALS
            
        super(PVAndWindModel, self).__init__(signals, config.typhoon_path('PVAndWind\\PV_Wind Target files\\PV_Wind.cpd'))
        self.switch = switch
        self.timer_cancellation_token = False

        def read_csv(file_path):
            '''
            Reads text files delimited with a newline
            and put results in the numpy array
            '''
            lookup_file = open(file_path, 'r')
            calc_res = lookup_file.readlines()
            lookup_file.close()
            calc_res = np.array(calc_res).astype(float)
            return calc_res
        
        self.wind_speed = read_csv(config.typhoon_path('PVAndWind/wind_speed.txt'))
        self.solar_isolation = read_csv(config.typhoon_path('PVAndWind/solar_isolation.txt'))

        self.solar_isolation_counter = 0
        self.wind_speed_counter = 0

        # PV_S (Irradiation) isn't given to us from Typhoon
        # it comes from a file (this is set on a timer).
        self.PV_S = 0

    def initialize(self):
        hil.set_source_sine_waveform('Vs1', rms = 4160/(3**0.5), frequency = 60.0, phase = 0.0,harmonics_pu = ())

        # Initialize Wind components
        Sb = 50e3 #VA
        Vb = 208 #V
        fb = 60.0 #Hz
        Vdc = 350  # V        
        
        path_to_component = "Wind Power Plant (Switching)."
        path_to_inputs = "Wind_in."
        path_to_outputs = "Wind_out."

        hil.set_scada_input_value(path_to_inputs + 'V_ref', 208.0)
        hil.set_scada_input_value(path_to_inputs + 'Q_ref', 0.0)
        hil.set_scada_input_value(path_to_inputs + 'Q_mode', 1.0)

        # Initialize PV Array components
        path_to_component = "PV_Plant."
        path_to_inputs = "PV_in."
        path_to_outputs = "PV_out."        

        Sb = 290e3  # VA
        Vb = 208  # V
        fb = 60.0  # Hz
        Vdc = 350  # V

        hil.set_scada_input_value(path_to_inputs + 'Irradiation', 173.9)        
        hil.set_scada_input_value(path_to_inputs + 'Q_ref', 0.0*1000)
        hil.set_scada_input_value(path_to_inputs + 'V_ref', 208.0)
        hil.set_scada_input_value(path_to_inputs + 'Q_mode', 1.0)

        #            time.sleep(1) # turn on pv components
        hil.set_scada_input_value('PV_in.Connect', 1.0)            
        hil.set_scada_input_value('PV_in.Enable', 1.0)            

        #            time.sleep(1) # turn on wind components
        hil.set_scada_input_value('Wind_in.Connect', 1.0)        
        hil.set_scada_input_value('Wind_in.Enable', 1.0)
        

        def enable_with_delay():
            '''
            I had to add delay to turning the PV Array on,
            otherwise PV_Imp was not right.
            If Imp was enabled immediately, it would be some decreasing negative value.
            '''
            pass


        #hil.set_pv_input_file('Photovoltaic Panel1', file=config.typhoon_path('PVAndWind/solar.ipvx'))            
            
        enable_with_delay_thread = threading.Thread(target=enable_with_delay, name='enable_with_delay')
        enable_with_delay_thread.start()

    def process(self, df):
        '''
        Performs KPI calculations on the DataFrame ~df~
        Return list of (InfluxDB measurement string, DataFrame)
        '''
        result = []
        if self.switch == 'both' or self.switch == 'wind':
            result.append(('wind_kpi', WindTurbine(self.WD_V).run(df).to_df()))
        if self.switch == 'both' or self.switch == 'pv':
            result.append(('pv_array_kpi', PV_Array(self.PV_S).run(df).to_df()))
        return result

    def on_start(self):
        def solar_isolation_timer():
            while True:
                if self.timer_cancellation_token:
                    return
                PV_S = self.solar_isolation[self.solar_isolation_counter]*1000.0
                hil.set_scada_input_value('PV_in.Irradiation', PV_S)                
                #hil.set_pv_input_file('Photovoltaic Panel1', file=config.typhoon_path('PVAndWind/solar.ipvx'), illumination=self.PV_S, temperature=25.0)
                if False:
                    print('solar_isolation_timer: Setting solar isolation to %s' % self.PV_S)
                self.solar_isolation_counter += 1
                if self.solar_isolation_counter > len(self.solar_isolation) - 1:
                    self.solar_isolation_counter = 0
                time.sleep(2) # using 2 seconds -- because 1 second in Typhoon HIL != 1 second real-time

        def wind_speed_timer():
            while True:
                if self.timer_cancellation_token:
                    return
                self.WD_V = self.wind_speed[self.wind_speed_counter]
                hil.set_scada_input_value('Wind_in.wind_speed', self.WD_V)
                if False:
                    print('wind_speed_timer: Setting wind speed to %s' % self.WD_V)
                self.wind_speed_counter += 1
                if self.wind_speed_counter > len(self.wind_speed) - 1:
                    self.wind_speed_counter = 0
                time.sleep(0.5) # using 2 seconds -- because 1 second in Typhoon HIL != 1 second real-time                
            
        self.solar_isolation_timer = threading.Thread(target=solar_isolation_timer, name='solar_isolation_timer')
        self.wind_speed_timer = threading.Thread(target=wind_speed_timer, name='wind_speed_timer')

        self.solar_isolation_timer.start()
        self.wind_speed_timer.start()

    def on_stop(self):
        self.timer_cancellation_token = True # cancel timers
    
class BatteryGeneratorAndFuelCellModel(Model):
    def __init__(self):
        super(BatteryGeneratorAndFuelCellModel, self).__init__(s.FC_SIGNALS + s.BATT_SIGNALS + s.GEN800_SIGNALS + s.TRANS_SIGNALS, config.typhoon_path('BatteryGeneratorAndFuelCell\\Bat_Gen_FC_Grid Target files\\Bat_Gen_FC_Grid.cpd'))

    def initialize(self):
        def enable_with_delay():
            '''
            I had to add delay to turning the system on
            Otherwise some values can be wrong.
            '''

            time.sleep(3)                        
            
            # Enable Diesel Genset 800kW
            path_to_component = "Diesel_Gen."
            path_to_inputs = "DG_in."
            path_to_outputs = "DG_out."
            Sb = 1.067 # MVA
            fb = 60  # Hz
            pms = 2  # number of pole pairs
            wb = fb*60/pms  # RPM
            Vtb = 4160.0  # V
            sign = 1
            pf_ref = 1
            #            hil.set_scada_input_value(path_to_inputs + 'pf_ref', sign*pf_ref)            
            hil.set_scada_input_value('DG_800kW.Gen_OP_mode', 1.0) # "Grid following"
            hil.set_scada_input_value('DG_800kW.Gen_Control_Mode', 2.0)
            hil.set_scada_input_value('DG_800kW.wref', 1800/wb)
            hil.set_scada_input_value('DG_800kW.Pref', 0.8/Sb)
            hil.set_scada_input_value('DG_800kW.Vref', 4160/Vtb)

            # Enable Battery Inverter
            Path = "ESS."
            Component_name = "Battery inverter" + "."
            Vn = 208.0 #V
            fn = 60.0 #Hz
            Sn = 0.5e6 #VA
            hil.set_scada_input_value('ESS.Vref', 208)
            hil.set_scada_input_value('ESS.mode', 1.0)
            hil.set_scada_input_value('ESS.f_ref', 60)
            hil.set_scada_input_value('ESS.Pref', -500*1000.0)
            hil.set_scada_input_value('ESS.Qref', 0*1000.0)

            # Enable fuel cell
            Path = "Fuel_Cell." # Subsystem path to where the component is. The last '.' before the component name must be included here.
            Component_name = "SOFC inverter."
            Sb = 50e3 #VA
            Vb = 208 #V
            fb = 60.0 #Hz
            hil.set_scada_input_value('Fuel_Cell.Pref_FC', 50)
            hil.set_scada_input_value('Fuel_Cell.V_ref', 208.0)
            hil.set_scada_input_value('Fuel_Cell.Q_ref', 0.0)

            # Enable Diesel Genset
            path_to_component = "Diesel_Gen."
            path_to_inputs = "DG_in."
            path_to_outputs = "DG_out."
            Sb = 0.07  # MVA
            fb = 60  # Hz
            pms = 2  # number of pole pairs
            wb = fb*60/pms  # RPM
            Vtb = 208.0  # V
            sign = 1
            pf_ref = 1
#            hil.set_scada_input_value('Back-Up.DG_in.pf_ref', sign*pf_ref)
            hil.set_scada_input_value('Back-Up.DG_in.Gen_OP_mode', 0.0)
            hil.set_scada_input_value('Back-Up.DG_in.Gen_Control_Mode', 2.0)
            hil.set_scada_input_value('Back-Up.DG_in.wref', 1800/wb)
            hil.set_scada_input_value('Back-Up.DG_in.Pref', 0.06/Sb)
            hil.set_scada_input_value('Back-Up.DG_in.Vref', 208/Vtb)


            # Turn things on 
            hil.set_scada_input_value('DG_800kW.Gen_On', 1.0)

            hil.set_scada_input_value('ESS.On', 1.0)            

            hil.set_scada_input_value('Fuel_Cell.Connect', 1.0)
            hil.set_scada_input_value('Fuel_Cell.Enable', 1.0)
            
            hil.set_scada_input_value('Back-Up.DG_in.Gen_On', 1.0)
            

        enable_with_delay_thread = threading.Thread(target=enable_with_delay, name='enable_with_delay')
        enable_with_delay_thread.start()

    def process(self, df):
        '''
        Performs KPI calculations on the DataFrame ~df~
        Return list of (InfluxDB measurement string, DataFrame)
        '''
        return [
            ('battery_kpi', Battery().run(df).to_df()),
            ('transformer_kpi', Transformer().run(df).to_df()),
            ('generator_kpi', DieselGenerator().run(df).to_df()),
            ('fuel_cell_kpi', FuelCell().run(df).to_df()),            
        ]
