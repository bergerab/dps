import math
from datetime import datetime, timedelta
from datetime import timezone

import numpy as np

import signals as s
from dataframe_stream import DataFrameStream
from influx import format_time

def to_percent(x):
    return x*100

class KPI:
    base_harmonic = 60
    
    # thd of one batch
    def one_thd(self, batch, base_harmonic) : 
        fft_vals = np.absolute(np.fft.fft(batch))

        # look at twice the amount just in case we miss the base harmonic
        fund_freq, fund_freq_idx = max([(v,i) for i,v in enumerate(fft_vals[:2*base_harmonic])]) 

        sum = 0        
        harmonic = fund_freq_idx + base_harmonic
        offset = int(base_harmonic/2)

        while harmonic < len(fft_vals)/2:
            peak = np.max(fft_vals[harmonic - offset : harmonic + offset])
            sum += peak * peak
            harmonic += base_harmonic

        thd = np.sqrt(sum) / fund_freq

        return thd;

    # return power ratings and THDs
    def thd(self, IV, sample_rate, sample_size, hop_size=None) :
        base_harmonic = int(self.base_harmonic * (sample_size / sample_rate))

        if hop_size is None: hop_size = sample_size 

        # a list of rows specified by column names 
        # -> a stream of a window of rows        
        # -> a stream of a row of windows
        # -> a stream of a row of THDs
        # -> a dataframe of THDs
        return IV\
            .hopping_window(sample_size, hop_size)\
            .map(lambda x: np.transpose(x))\
            .mapAll(lambda batch: self.one_thd(batch, base_harmonic)) 

    def thd_line(self, IV, time, thdNames, sample_rate, sample_size, hop_size=None):
        if hop_size is None: hop_size = sample_size 

        thd = self.thd(IV, sample_rate, sample_size, hop_size)

        slicedTime = time\
            .hopping_window(sample_size, hop_size)\
            .map(lambda x: x[0])

        #return thd.to_signal(thdNames)
        return slicedTime.merge(thd).to_signal(['Time'] + thdNames)
    
    def to_df(self, IV):
        return self.run(IV).concat()

class Power_Electronics_Inverter(KPI):
    rated_power = 100*1000 # 100 kW

    def __init__(self, base_harmonic=60):
        self.base_harmonic = base_harmonic

    def one_rms(self, s):
        lst = list(map(lambda x: x*x, s))

        return np.sqrt(sum(lst)/len(lst))

    def rms(self, IorV, window_size, hop_size):
        return IorV.hopping_window(window_size, hop_size).map(lambda s: self.one_rms(s)) 

    def ac_power(self, I, V, time, window_size, hop_size):
        slicedTime = time\
            .hopping_window(window_size, hop_size)\
            .map(lambda x: x[0])
        power = self.rms(I, window_size, hop_size)\
                    .merge(self.rms(V, window_size, hop_size))\
                    .mapSpread(lambda I, V: I*V)

        return slicedTime.merge(power).to_signal(['Time', 'AC Power'])

    def thd_with_power_rating(self, IV, time, thdNames, sample_rate, sample_size) :
        thd = self.thd(IV, sample_rate, sample_size)

        powerRating = IV\
            .mapSpread(lambda Ia,Va,Ib,Vb,Ic,Vc: Ia*Va+Ib*Vb+Ic*Vc)\
            .tumbling_window(sample_size)\
            .map(lambda x: sum(x)/len(x)/self.rated_power) 
        
        data = powerRating.merge(thd)

        slicedTime = time\
            .tumbling_window(sample_size)\
            .map(lambda x: x[0])

        return slicedTime.merge(data).to_signal(['Time', 'Power rating'] + thdNames)

    def thd_at_power_level(self, IV, sample_rate, sample_size, power_level):
        data = self.thd(IV, sample_rate, sample_size)\
                   .filter(lambda x: round(x[0],2) == power_level)\
                   .map(lambda x: x[1:])

        sum = None
        len = 0

        def f(thds):
            nonlocal len
            nonlocal sum
            len = len + 1

            if(sum == None):
                sum = thds.copy()
            else:
                for i, thd in enumerate(thds):
                    sum[i] = sum[i] + thd
                    
        data.subscribe(f)

        if(len > 0):
            ret = list(map(lambda x: x/len, sum))
        else:
            ret = []
        return ret


    def efficiency(self, IV) :
        def f(Idc, Vdc, Ia, Va, Ib, Vb, Ic, Vc): 
            Pout = Ia * Va + Ib * Vb + Ic * Vc
            Pin = Idc * Vdc
            return [Pout/self.rated_power, Pout/Pin]

        return IV.mapSpread(f)

    def efficiency_kpi(self, IV, time) :
        return time.merge(self.efficiency(IV))\
                   .to_signal(['Time','Power rating', 'Efficiency']) 

    def weighted_efficiency_kpi(self, IV):
        def f(efficiency_list, rating_efficiency):
            rating, efficiency = rating_efficiency
            x = round(rating, 2)
            if(x == 0.1):
                efficiency_list[0].append(efficiency)
            elif(x == 0.2):
                efficiency_list[1].append(efficiency)
            elif(x == 0.3):
                efficiency_list[2].append(efficiency)
            elif(x == 0.5):
                efficiency_list[3].append(efficiency)
            elif(x == 0.75):
                efficiency_list[4].append(efficiency)
            elif(x == 1):
                efficiency_list[5].append(efficiency)

            return efficiency_list 

        # collect efficiency values at each power rating
        lst = self.efficiency(IV).scan(f, [[],[],[],[],[],[]]).last()

        # average the efficiency for each power rating
        ave = list(map(lambda l: 0 if len(l) == 0 else sum(l)/len(l), lst))

        # weighted efficiency
        return 0.04 * ave[0] + 0.05 * ave[1] + 0.12 * ave[2] + 0.21 * ave[3] + 0.53 * ave[4] + 0.05 * ave[5]

class PV_Array(Power_Electronics_Inverter):
    Voc = 520
    Isc = 970
    A = 1450 # m2

    def __init__(self, PV_S):
        super(PV_Array, self).__init__()

        # TODO: not really a proper solution
        # we want to know PV_S for each sample (given to us by Typhoon for example)
        # but this might work (it could cause small glitches in the KPIs if the PV_S
        # doesn't line up properly with what it was when the data was captured)
        self.PV_S = PV_S

    def fillFactor_efficiency_efficiencyMax(self, IV):
        def calc(Va, Vb, Vc, Ia, Ib, Ic, Vmp, Imp, S):
            PV_Pmax = Vmp*Imp
            PV_Pin = self.A*S
            PV_Pout = Va*Ia + Vb*Ib + Vc*Ic            
            PV_FF = PV_Pmax / (self.Voc * self.Isc)
            PV_EArray = min(100 * (self.Voc * self.Isc * PV_FF) / (self.A * S), 99.99)
            PV_EInverter = min(100 * (PV_Pout / PV_Pmax), 99.99)
            PV_LD = 100 * (S/1000)
            
            return [
                PV_Pmax,
                PV_Pin,
                PV_Pout,
                PV_FF,
                PV_EArray,
                PV_EInverter,
                PV_LD,
            ]
        
        data = IV.mapWithTime(calc)
        return data.to_signal(['Time', 'PV_Pmax', 'PV_Pin', 'PV_Pout', 'PV_FF', 'PV_EArray', 'PV_EInverter', 'PV_LD'])

    def run(self, df):
        IV = proj(df, ['Time'] + s.PV_SIGNALS)
        fill_and_efficiency = self.fillFactor_efficiency_efficiencyMax(IV)

        sample_rate, sample_size = 1000, 1000 # TODO: We should just set the base harmonic (60) instead of doing this sample_rate/sample_size thing
        IV = proj(df, [s.PV_VA, s.PV_VB, s.PV_VC, s.PV_IA, s.PV_IB, s.PV_IC])        
        thds = self.thd_line(IV, proj(df, ['Time']), ['PV_THD_Va', 'PV_THD_Vb', 'PV_THD_Vc', 'PV_THD_Ia', 'PV_THD_Ib', 'PV_THD_Ic'], sample_rate, sample_size)

        stream = fill_and_efficiency \
            .interpolateMergeWithTime(thds) \
            .to_signal([
                'Time',
                'PV_Pmax', 'PV_Pin', 'PV_Pout',
                'PV_FF', 'PV_EArray', 'PV_EInverter',
                'PV_LD',
                'PV_THD_Va', 'PV_THD_Vb', 'PV_THD_Vc', 'PV_THD_Ia', 'PV_THD_Ib', 'PV_THD_Ic',                
            ])

        return stream


class FuelCell(KPI):
    Sb = 50e3 # VA
    Vb = 208  # V
    fb = 60.0 # Hz

    def run(self, df):
        def calc(FC_mf, FC_Vdc, FC_Idc):
            MAX_CURRENT = 150
            if FC_Idc > MAX_CURRENT: # Handle transients (when system boots)
                FC_Idc = 0
            
            WH_2_HHV = 39.39 # Kwh/Kg
            Pout = (FC_Idc * FC_Vdc) / 1000
            Pin = WH_2_HHV * FC_mf # for some reason, our efficiency percent was 10's place off, multiplying by 10 to correct that
            FC_EE = float((Pout/Pin) * 100)

            if FC_EE > 100: # for transients
                FC_EE = 0.0
            
            return [
                FC_EE,
                FC_Idc,
            ]
        
        IV = proj(df, ['Time', s.FC_MF, s.FC_VDC, s.FC_IDC])
        return IV.mapWithTime(calc)\
                .to_signal(['Time', 'FC_EE', 'FC_IDC_FIX'])


class Transformer(KPI):
    def run(self, df):
        def calc(Va_p, Vb_p, Vc_p, Ia_p, Ib_p, Ic_p,
                 Va_s, Vb_s, Vc_s, Ia_s, Ib_s, Ic_s):
            Pprim = (Va_p * Ia_p) + (Vb_p * Ib_p) + (Vc_p * Ic_p)
            Psec = (Va_s * Ia_s) + (Vb_s * Ib_s) + (Vc_s * Ic_s)
            TRANS_E = float(Psec / Pprim if Pprim != 0 else 0.0) * 100.0 # Avoid division by zero
            if Pprim < 0 or Psec < 0: # account for if the system is off
                TRANS_E = 0
            return [
                Pprim,
                Psec,
                TRANS_E,
            ]
        
        IV = proj(df, ['Time',
                       s.TRANS_VA_P, s.TRANS_VB_P, s.TRANS_VC_P,
                       s.TRANS_IA_P, s.TRANS_IB_P, s.TRANS_IC_P,
                       s.TRANS_VA_S, s.TRANS_VB_S, s.TRANS_VC_S,
                       s.TRANS_IA_S, s.TRANS_IB_S, s.TRANS_IC_S])

        return IV.mapWithTime(calc)\
                 .to_signal(['Time', 'TRANS_Pprim', 'TRANS_Psec', 'TRANS_E'])
    
class DieselGenerator:
    # window_size should be 2 second of data to allow sampling by average
    def fuel_consumption_kpi(self, fuel, window_size):
        return fuel.to_signal(['Time', 'Fuel Consumption'])
        # return fuel\
        #         .tumbling_window(window_size)\
        #         .map(lambda x: np.transpose(x))\
        #         .map(lambda x: [x[0][0], sum(x[1])/window_size])\
        #         .to_signal(['Time', 'Fuel Consumption'])

    def efficiency_kpi(self, IV):
        def calc(Ia, Ib, Ic, Va, Vb, Vc, Fc):
            Pout = (Va * Ia + Vb * Ib + Vc * Ic) / 1000
            Ediesel = 0.293 * 139
            Pin = Ediesel * Fc
            DG_E = (Pout / Pin) * 100
            return [
                DG_E,
            ]
        return IV\
                .mapWithTime(calc)\
                .to_signal(['Time', 'Efficiency'])

    def run(self, df):
        consumptionIV = proj(df, ['Time', s.GEN800_FC])
        efficiencyIV = proj(df, ['Time', s.GEN800_IA, s.GEN800_IB, s.GEN800_IC,
                                         s.GEN800_VA, s.GEN800_VB, s.GEN800_VC,
                                         s.GEN800_FC])

        consumption = self.fuel_consumption_kpi(consumptionIV, 4000)
        efficiency = self.efficiency_kpi(efficiencyIV)

        stream = consumption.mergeWithTime(efficiency).to_signal(['Time', 'Fuel Consumption', 'Efficiency'])

        return stream

# class BackupGenerator(Diesel_Generator):
#     def run(self, df):
#         consumptionIV = proj(df, ['Time', s.BGEN_IA])
#         efficiencyIV = proj(df, ['Time', s.BGEN_IA, s.BGEN_IB, s.BGEN_IC,
#                                  s.BGEN_VA, s.BGEN_VB, s.BGEN_VC,
#                                  s.BGEN_FC])

        
#         consumptionIV = proj(df, ['Time', s.BACKUP_GEN_IA]) # TODO: replace IA with Fuel Consumption, when Garry gives us that
#         efficiencyIV = proj(df, ['Time', s.BACKUP_GEN_IA, s.BACKUP_GEN_IB, s.BACKUP_GEN_IC,
#                                          s.BACKUP_GEN_VA, s.BACKUP_GEN_VB, s.BACKUP_GEN_VC])

#         consumption = self.fuel_consumption_kpi(consumptionIV, 4000)
#         efficiency = self.efficiency_kpi(efficiencyIV)

#         stream = consumption.mergeWithTime(efficiency).to_signal(['Time', 'Fuel Consumption', 'Efficiency'])

#         return stream
        
# Calculate the efficiency and capacity factor KPI for Wind Turbine
class WindTurbine(KPI):
    density = 1.225 # kg/m3
    area = 448 # m2
    velocity = 16 # m/s
    P_rated = 50*1000 # 50 KW

    def __init__(self, WD_V):
        super(WindTurbine, self).__init__()

        # TODO: not really a proper solution
        # we want to know WD_V for each sample (given to us by Typhoon for example)
        # but this might work (it could cause small glitches in the KPIs if the WD_V
        # doesn't line up properly with what it was when the data was captured)
        self.WD_V = WD_V

    # data: Stream (Ia, Ib, Ic, Va, Vb, Vc)
    # return: Stream Power
    def power(self, data):
        power = lambda Ia, Ib, Ic, Va, Vb, Vc: Va * Ia + Vb * Ib + Vc * Ic

        return data.mapWithTime(power)

    # data: Stream (Ia, Ib, Ic, Va, Vb, Vc)
    # time: Stream Time
    # return: DataFrame (Time, Efficiency)
    def efficiency_kpi(self, data):
        P_w = (self.density * self.area * self.velocity * self.velocity * self.velocity) * (8/27)

        return self.power(data)\
                .mapWithTime(lambda P_out: P_out / P_w)\
                .to_signal(['Time', 'Efficiency']) 

    # return capacity factor, which is a fraction 
    def capacity_factor_kpi(self, data):
        def f(t1_sofar, t2_v):
            t1, sofar = t1_sofar
            t2, v = t2_v
            return [t2, sofar + v*(t2-t1)]

        t, x = self.power(data).scan(f, [0,0]).last()

        return (x/t) / self.P_rated 

    def run(self, df):
        IV = proj(df, ['Time', s.WD_VA, s.WD_VB, s.WD_VC,
                               s.WD_IA, s.WD_IB, s.WD_IC,
                    s.WD_VEL])
        
        def calc(Va, Vb, Vc, Ia, Ib, Ic, Vel):
            density = 1.25
            area = 95.8
            Pw = (8/27)*density*area*math.pow(Vel, 3)
            Poutw = Va*Ia + Vb*Ib + Vc*Ic
            
            return [
                to_percent(Poutw/Pw), # Efficiency
                to_percent(Pw/145500), # Load % -- I was told to use 50,000 as the number here, but that wasn't right         
            ]

        data = IV.mapWithTime(calc)

        sample_rate, sample_size = 1000, 1000  # TODO: We should just set the base harmonic (60) instead of doing this sample_rate/sample_size thing
        
        IV = proj(df, [s.WD_VA, s.WD_VB, s.WD_VC, s.WD_IA, s.WD_IB, s.WD_IC])        
        thds = self.thd_line(IV, proj(df, ['Time']), ['WD_THD_Va', 'WD_THD_Vb', 'WD_THD_Vc', 'WD_THD_Ia', 'WD_THD_Ib', 'WD_THD_Ic'], sample_rate, sample_size)

        return data.interpolateMergeWithTime(thds) \
                   .to_signal(['Time', 'WD_E', 'WD_LD',
                               'WD_THD_Va', 'WD_THD_Vb', 'WD_THD_Vc', 'WD_THD_Ia', 'WD_THD_Ib', 'WD_THD_Ic' ])

class Battery:
    SOC_t0 = 1 # initial state of charge

    Nominal_capacity = 480 * 1000 * 3600 # 480 kWh
    Vdc_link = 350 # 350 V
    C_rated = Nominal_capacity / Vdc_link
    
    def cap(self, x):
        if(x > 1): x = 1
        elif(x < 0): x = 0
        return x

    # amp seconds
    def capacity(self, Idc):
        return Idc.integrate()
        

    # watt seconds
    def energy(self, IV):
        return IV.mapWithTime(lambda I,V: I*V)\
                .integrate()

    # amp hours
    def capacity_kpi(self, Idc):
        return self.capacity(Idc)\
                .mapWithTime(lambda x: x/3600)\
                .to_signal(['Time', 'Capacity'])

    # State of charge during discharge 
    def soc_kpi(self, Idc):
        return self.capacity(Idc)\
                .mapWithTime(lambda capacity: self.SOC_t0 - capacity/self.C_rated)\
                .to_signal(['Time', 'State of charge']) 

    # State of health 
    def soh_kpi(self, Idc):
        return self.capacity(Idc)\
                .mapWithTime(lambda capacity: capacity/self.C_rated * 100)\
                .to_signal(['Time', 'State of health'])

    def coulomb_efficiency_kpi(self, dischargeIdc, chargeIdc):
        return self.capacity(dischargeIdc)\
                .mergeWithTime(self.capacity(chargeIdc))\
                .mapWithTime(lambda d, c: -d/c)\
                .mapWithTime(self.cap)\
                .to_signal(['Time', 'Coulomb efficiency'])

    def round_trip_energy_efficiency_kpi(self, dischargeIV, chargeIV):
        return self.energy(dischargeIV)\
                .mergeWithTime(self.energy(chargeIV))\
                .mapWithTime(lambda d, c: -d/c)\
                .mapWithTime(self.cap)\
                .to_signal(['Time', 'Round trip energy efficiency'])

    def run(self, df):
        IV = proj(df, ['Time', s.BATT_SOC])
        return IV.to_signal(['Time', 'Batt_SOC'])

#        capacity = self.capacity_kpi(idcIV)
#        soh = self.soh_kpi(idcIV)
        #efficiency = self.coulomb_efficiency_kpi(idcIV)
#        return soh

from dateutil import parser
def compute_battery_kpis(client, start, end):
    '''
    Goes through the 'battery_charge' and 'battery_discharge' data and computes the KPIs, and puts it into the 'battery_kpis' measurement
    Should error if 'battery_charge' or 'battery_discharge' data is missing
    '''
    charge_query = 'SELECT * FROM "battery_charge" WHERE time >= \'%s\' AND time <= \'%s\'' % (format_time(start), format_time(end))
    discharge_query = 'SELECT * FROM "battery_discharge" WHERE time >= \'%s\' AND time <= \'%s\'' % (format_time(start), format_time(end))

    charge_result = client.query(charge_query)
    discharge_result = client.query(discharge_query)

    print('CHR', list(charge_result.get_points()))
    print('DIS', discharge_result.get_points())
    
    points = [] # TODO: process this in batches... right now this loads every point into memory
    i = 0
    for C, D in zip(charge_result.get_points(), discharge_result.get_points()):
        try:
            i+=1
            print('i ', i)
            print(C, D)
            time = C['time']
            BATT_RTEE = (abs(D['Voltage']) * D['Time'] * abs(D['Current'])) / (abs(C['Voltage']) * C['Time'] * abs(C['Current']))
            BATT_CE = abs(D['Current']) / abs(C['Current'])
            BATT_NOMCAP = abs(D['Current']) * D['Time']
            BATT_CAP = abs(D['Current']) * D['Voltage']            
            Crated = 400000
            BATT_SOH = BATT_CAP / Crated
            #t = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) # I guess strptime assumes it is a local timezone -- so i replaced the timezone with utc manually
            t = parser.parse(time).replace(tzinfo=timezone.utc)
            time = t.timestamp()
            points.append("%s BATT_RTEE=%s,BATT_CE=%s,BATT_NOMCAP=%s,BATT_CAP=%s,BATT_SOH=%s %s" % ('battery_kpi', BATT_RTEE, BATT_CE, BATT_NOMCAP, BATT_CAP, BATT_SOH, int(time)))
        except Exception as e:
            print(e)
    client.write_points(points, protocol='line', time_precision='s')
    
def proj(df, columnNames):
    return DataFrameStream(df[columnNames].values.tolist(), columnNames)
