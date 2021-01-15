PV_VA = 'PV_Va'
PV_VB = 'PV_Vb'
PV_VC = 'PV_Vc'
PV_IA = 'PV_Ia'
PV_IB = 'PV_Ib'
PV_IC = 'PV_Ic'
PV_VMP = 'PV_Vmp'
PV_IMP = 'PV_Imp'
PV_S = 'PV_Plant.Control.Grid_follow.irr_in'

PV_SIGNALS = [
    PV_VA,  PV_VB, PV_VC,
    PV_IA,  PV_IB, PV_IC,
    PV_VMP, PV_IMP,
    PV_S,
]

WD_VA = 'Wd_Va'
WD_VB = 'Wd_Vb'
WD_VC = 'Wd_Vc'
WD_IA = 'Wd_Ia'
WD_IB = 'Wd_Ib'
WD_IC = 'Wd_Ic'
WD_VEL = 'Wind Power Plant (Switching).Control.Grid_follow.wind_speed'

WD_SIGNALS = [
    WD_VA, WD_VB, WD_VC,
    WD_IA, WD_IB, WD_IC,
    WD_VEL,
]

FC_MF = 'FC_mf'
FC_VDC = 'FC_Vdc'
FC_IDC = 'FC_Idc'

FC_SIGNALS = [
    FC_MF,
    FC_VDC, FC_IDC,
]

BATT_SOC = 'Batt_SOC'

BATT_SIGNALS = [
    BATT_SOC
]

GEN800_VA = 'DG_800kW.Diesel_Gen.Measurements.Va'
GEN800_VB = 'DG_800kW.Diesel_Gen.Measurements.Vb'
GEN800_VC = 'DG_800kW.Diesel_Gen.Measurements.Vc'
GEN800_IA = 'DG_800kW.Diesel_Gen.Measurements.Ia'
GEN800_IB = 'DG_800kW.Diesel_Gen.Measurements.Ib'
GEN800_IC = 'DG_800kW.Diesel_Gen.Measurements.Ic'
GEN800_FC = 'DG_800kW.Diesel_Gen.Measurements.Fuel consumption'
GEN800_POWER = 'Diesel Generator Power'

GEN800_SIGNALS = [
    GEN800_VA, GEN800_VB, GEN800_VC,
    GEN800_IA, GEN800_IB, GEN800_IC,
    GEN800_FC,
]

TRANS_VA_P = 'Va_prim'
TRANS_VB_P = 'Vb_prim'
TRANS_VC_P = 'Vc_prim'
TRANS_IA_P = 'Ia_Prim'
TRANS_IB_P = 'Ib_Prim'
TRANS_IC_P = 'Ic_Prim'
TRANS_VA_S = 'Va_sec'
TRANS_VB_S = 'Vb_sec'
TRANS_VC_S = 'Vc_sec'
TRANS_IA_S = 'Ia_sec'
TRANS_IB_S = 'Ib_sec'
TRANS_IC_S = 'Ic_sec'

TRANS_SIGNALS = [
    TRANS_VA_P, TRANS_VB_P, TRANS_VC_P,
    TRANS_IA_P, TRANS_IB_P, TRANS_IC_P,
    TRANS_VA_S, TRANS_VB_S, TRANS_VC_S,
    TRANS_IA_S, TRANS_IB_S, TRANS_IC_S,        
]
