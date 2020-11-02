import typhoon.api.hil as hil







def enable_pv():
    hil.set_scada_input_value('PV.Enable', 1.0)
    hil.set_scada_input_value('PV.Connect', 1.0)

def enable_wind():
    hil.set_scada_input_value('Wind.Connect', 1.0)
    hil.set_scada_input_value('Wind.Enable', 1.0)

def enable_fuel_cell():
    hil.set_scada_input_value('Fuel_Cell.Connect', 1.0)
    hil.set_scada_input_value('Fuel_Cell.Enable', 1.0)    

def enable_ess():
    hil.set_scada_input_value('ESS.On', 1.0)
    hil.set_scada_input_value('ESS.mode', 1.0)

    hil.set_scada_input_value('ESS.Vref', 208.0)
    hil.set_scada_input_value('ESS.f_ref', 60.0)
    hil.set_scada_input_value('ESS.Pref', 100*1000.0)
    hil.set_scada_input_value('ESS.Qref', 0*1000.0)

def enable_gen800():
    path_to_component = "Diesel_Gen."
    path_to_inputs = "DG_in."
    path_to_outputs = "DG_out."

    hil.set_scada_input_value('DG_800kW.Gen_On', 1.0)
    hil.set_scada_input_value('DG_800kW.Gen_Control_Mode', 2.0)
    
    pf_ref = 1.0
    sign = 1.0

    Sb  = 1.067     # MVA
    fb  = 60        # Hz
    pms = 2         # number of pole pairs
    wb  = fb*60/pms # RPM
    Vtb = 4160.0    # V    

    hil.set_scada_input_value(path_to_inputs + 'pf_ref', sign*pf_ref) # TODO: double chec kthis is the right path
    hil.set_scada_input_value('DG_800kW.Gen_OP_mode', 1.0) # any way to start this at 0 then after some delay, set to 1.0 , to avoid distubance?

    hil.set_scada_input_value('DG_800kW.wref', 1800.0/wb)
    hil.set_scada_input_value('DG_800kW.Pref', 0.8/Sb)
    hil.set_scada_input_value('DG_800kW.Vref', 4160.0/Vtb)

def enable_backup_gen():
    path_to_component = "Diesel_Gen."
    path_to_inputs = "DG_in."
    path_to_outputs = "DG_out."

    Sb  = 0.07       # MVA
    fb  = 60         # Hz
    pms = 2          # number of pole pairs
    wb  = fb*60/pms  # RPM
    Vtb = 208.0      # V

    hil.set_scada_input_value('Back-Up.DG_in.Gen_On', 1.0)
    hil.set_scada_input_value('Back-Up.DG_in.Gen_Control_Mode', 2.0)

    pf_ref = 1.0
    sign = 1.0
    
    hil.set_scada_input_value('Back-Up.DG_in.pf_ref', sign*pf_ref)
    hil.set_scada_input_value('Back-Up.DG_in.Gen_OP_mode', 0.0)
    hil.set_scada_input_value('Back-Up.Enable', 1.0)

    hil.set_scada_input_value('Back-Up.DG_in.wref', 1800/wb)
    hil.set_scada_input_value('Back-Up.DG_in.Pref', 0.06/Sb)
    hil.set_scada_input_value('Back-Up.DG_in.Vref', 208/Vtb)

def initialize_grid():
    hil.set_scada_input_value('c_option', 0.0)    
    hil.set_scada_input_value('op_mode', 0.0)    
    
def set_25_load_control():
    hil.set_contactor('Interruptible load.S1',swControl=True, swState=True)

def set_50_load_control():
    hil.set_contactor('Load 50 %.S1', swControl=True, swState=True)

def set_75_load_control():
    hil.set_contactor('Load 75 %.S1', swControl=True, swState=True)

def set_100_load_control():
    hil.set_contactor('Load 100 %.S1', swControl=True, swState=True)

def set_25_load():
    set_25_load_control()

def set_50_load():
    set_25_load_control()
    set_50_load_control()

def set_75_load():
    set_25_load_control()
    set_50_load_control()
    set_75_load_control()

def set_100_load():
    set_25_load_control()
    set_50_load_control()
    set_75_load_control()
    set_100_load_control()

