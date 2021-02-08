BATTERY = {
  "name": "Battery",
  "description": "",
  "kpis": [
    {
      "name": "Round Trip Efficiency",
      "identifier": "",
      "description": "",
      "computation": "abs(sum(DischargeVoltage * DischargeTimestep * DischargeCurrent) / sum(ChargeVoltage * ChargeTimestep * ChargeCurrent))",
      "hidden": False
    },
    {
      "name": "Coulomb Efficiency",
      "identifier": "",
      "description": "",
      "computation": "abs(sum(DischargeCurrent * DischargeTimestep)) / abs(sum(ChargeCurrent * ChargeTimestep))",
      "hidden": False
    },
    {
      "name": "Discharged Capacity (kWh)",
      "identifier": "DischargedCapacity",
      "description": "",
      "computation": "sum((abs(DischargeCurrent) * DischargeVoltage * DischargeTimestep) / 1000)",
      "hidden": False
    },
    {
      "name": "State of Health",
      "identifier": "",
      "description": "",
      "computation": "avg(StateOfCharge - 0.2)",
      "hidden": False
    },
    {
      "name": "State of Charge",
      "identifier": "",
      "description": "",
      "computation": "avg(StateOfCharge)",
      "hidden": False
    },
    {
      "name": "Charged Capacity (kWh)",
      "identifier": "ChargedCapacity",
      "description": "",
      "computation": "sum((abs(ChargeCurrent) * ChargeVoltage * ChargeTimestep) / 1000)",
      "hidden": False
    },
    {
      "name": "Capacity",
      "identifier": "",
      "description": "",
      "computation": "sum(DischargeCurrent * DischargeTimestep)",
      "hidden": False
    }
  ],
  "parameters": [
    {
      "name": "CRated (ah)",
      "identifier": "CRated",
      "description": "",
      "hidden": False,
      "default": "400000"
    },
    {
      "name": "Nominal Capacity (kWh)",
      "identifier": "NominalCapacity",
      "description": "",
      "hidden": False,
      "default": "100000"
    }
  ]
}

TRANSFORMER = {
  "name": "Transformer",
  "description": "",
  "kpis": [
    {
      "name": "PPrim",
      "identifier": "",
      "description": "",
      "computation": "VaPrim * IaPrim + VbPrim * IbPrim + VcPrim * IcPrim",
      "hidden": True
    },
    {
      "name": "PSec",
      "identifier": "",
      "description": "",
      "computation": "VaSec * IaSec + VbSec * IbSec + VcSec * IcSec",
      "hidden": True
    },
    {
      "name": "Efficiency",
      "identifier": "",
      "description": "",
      "computation": "avg((PSec / PPrim) * 100)",
      "hidden": False
    }
  ],
  "parameters": []
}

DIESEL_GENERATOR = {
  "name": "Diesel Generator",
  "description": "",
  "kpis": [
    {
      "name": "Fuel Consumption",
      "identifier": "",
      "description": "",
      "computation": "avg(FuelConsumption)",
      "hidden": False
    },
    {
      "name": "Pout",
      "identifier": "",
      "description": "",
      "computation": "(Va * Ia + Vb * Ib + Vc * Ic) / 1000",
      "hidden": True
    },
    {
      "name": "Pin",
      "identifier": "",
      "description": "",
      "computation": "0.293 * 139 * FuelConsumption",
      "hidden": True
    },
    {
      "name": "Generator Efficiency",
      "identifier": "Efficiency",
      "description": "<p>Ratio of the electrical output power to the fuel input power.</p>",
      "computation": "avg((Pout / Pin) * 100)",
      "hidden": False
    }
  ],
  "parameters": []
}

WIND_TURBINE = {
  "name": "Wind Turbine",
  "description": "",
  "kpis": [
    {
      "name": "THD Voltage (Phase A)",
      "identifier": "THD_Va",
      "description": "<p>Total harmonic distortion of the voltage (phase a).</p>",
      "computation": "avg(thd(window(Va, THDWindow), BaseHarmonic))",
      "hidden": False
    },
    {
      "name": "THD Voltage (Phase B)",
      "identifier": "THD_Vb",
      "description": "<p>Total harmonic distortion of the voltage (phase b).</p>",
      "computation": "avg(thd(window(Vb, THDWindow), BaseHarmonic))",
      "hidden": False
    },
    {
      "name": "THD Voltage (Phase C)",
      "identifier": "THD_Vc",
      "description": "<p>Total harmonic distortion of the voltage (phase c).</p>",
      "computation": "avg(thd(window(Vc, THDWindow), BaseHarmonic))",
      "hidden": False
    },
    {
      "name": "THD Current (Phase A)",
      "identifier": "THD_Ia",
      "description": "<p>Total harmonic distortion of the current (phase a).</p>",
      "computation": "avg(thd(window(Ia, THDWindow), BaseHarmonic))",
      "hidden": False
    },
    {
      "name": "THD Current (Phase B)",
      "identifier": "THD_Ib",
      "description": "<p>Total harmonic distortion of the current (phase b).</p>",
      "computation": "avg(thd(window(Ib, THDWindow), BaseHarmonic))",
      "hidden": False
    },
    {
      "name": "THD Current (Phase C)",
      "identifier": "THD_Ic",
      "description": "<p>Total harmonic distortion of the current (phase c).</p>",
      "computation": "avg(thd(window(Ic, THDWindow), BaseHarmonic))",
      "hidden": False
    },
    {
      "name": "Load",
      "identifier": "",
      "description": "",
      "computation": "PWind / MaxPWind",
      "hidden": False
    },
    {
      "name": "THD Voltage (Phase A) at Load Percentages",
      "identifier": "",
      "description": "<p>Total harmonic distortion of voltage (phase a) once at 25%, 50%, 75%, and 100%.</p>",
      "computation": "values(\"THD at 25% Load\",\n           avg(THD_Va if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Va if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Va if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Va if Load > 0.9 else Nothing))",
      "hidden": False
    },
    {
      "name": "THD Voltage (Phase B) at Load Percentages",
      "identifier": "",
      "description": "<p>Total harmonic distortion of voltage (phase b) once at 25%, 50%, 75%, and 100%.</p>",
      "computation": "values(\"THD at 25% Load\",\n           avg(THD_Vb if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Vb if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Vb if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Vb if Load > 0.9 else Nothing))",
      "hidden": False
    },
    {
      "name": "THD Voltage (Phase C) at Load Percentages",
      "identifier": "",
      "description": "<p>Total harmonic distortion of voltage (phase c) once at 25%, 50%, 75%, and 100%.</p>",
      "computation": "values(\"THD at 25% Load\",\n           avg(THD_Vc if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Vc if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Vc if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Vc if Load > 0.9 else Nothing))",
      "hidden": False
    },
    {
      "name": "THD Current (Phase A) at Load Percentages",
      "identifier": "",
      "description": "<p>Total harmonic distortion of current (phase a) once at 25%, 50%, 75%, and 100%.</p>",
      "computation": "values(\"THD at 25% Load\",\n           avg(THD_Ia if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Ia if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Ia if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Ia if Load > 0.9 else Nothing))",
      "hidden": False
    },
    {
      "name": "THD Current (Phase B) at Load Percentages",
      "identifier": "",
      "description": "<p>Total harmonic distortion of current (phase b) once at 25%, 50%, 75%, and 100%.</p>",
      "computation": "values(\"THD at 25% Load\",\n           avg(THD_Ib if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Ib if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Ib if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Ib if Load > 0.9 else Nothing))",
      "hidden": False
    },
    {
      "name": "THD Current (Phase C) at Load Percentages",
      "identifier": "",
      "description": "<p>Total harmonic distortion of current (phase c) once at 25%, 50%, 75%, and 100%.</p>",
      "computation": "values(\"THD at 25% Load\",\n           avg(THD_Ic if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Ic if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Ic if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Ic if Load > 0.9 else Nothing))",
      "hidden": False
    },
    {
      "name": "Weighted Efficiency",
      "identifier": "",
      "description": "",
      "computation": "(0.04 * avg(Efficiency if Load > 0.05 and Load < 0.1  else Nothing)) + \\\n(0.05 * avg(Efficiency if Load > 0.15 and Load < 0.2  else Nothing)) + \\\n(0.12 * avg(Efficiency if Load > 0.25 and Load < 0.35 else Nothing)) + \\\n(0.21 * avg(Efficiency if Load > 0.45 and Load < 0.55 else Nothing)) + \\\n(0.53 * avg(Efficiency if Load > 0.7  and Load < 0.8  else Nothing)) + \\\n(0.05 * avg(Efficiency if Load > 0.9 else Nothing))",
      "hidden": False
    },
    {
      "name": "Pout",
      "identifier": "",
      "description": "",
      "computation": "Va * Ia + Vb * Ib + Vc * Ic",
      "hidden": True
    },
    {
      "name": "PWind",
      "identifier": "",
      "description": "",
      "computation": "(8/27) * Density * Area * Velocity * Velocity * Velocity",
      "hidden": False
    },
    {
      "name": "Wind Turbine Efficiency",
      "identifier": "Efficiency",
      "description": "",
      "computation": "avg((Pout / PWind) * 100)",
      "hidden": False
    }
  ],
  "parameters": [
    {
      "name": "Base Harmonic",
      "identifier": "BaseHarmonic",
      "description": "",
      "hidden": False,
      "default": "60"
    },
    {
      "name": "MaxPWind",
      "identifier": "MaxPWind",
      "description": "",
      "hidden": False,
      "default": "50000"
    },
    {
      "name": "Area",
      "identifier": "",
      "description": "",
      "hidden": False,
      "default": "95.8"
    },
    {
      "name": "Density",
      "identifier": "",
      "description": "",
      "hidden": False,
      "default": "1.25"
    },
    {
      "name": "THD Window Size",
      "identifier": "THDWindow",
      "description": "",
      "hidden": False,
      "default": "\"1s\""
    }
  ]
}
    
PV_INVERTER = {
    "name": "PV Inverter",
    "description": "",
    "kpis": [
        {
            "name": "THD Voltage (Phase A)",
            "identifier": "THD_Va",
            "description": "<p>Total harmonic distortion of the voltage (phase a).</p>",
            "computation": "avg(thd(window(Va, THDWindow), BaseHarmonic))",
            "hidden": False
        },
        {
            "name": "THD Voltage (Phase B)",
            "identifier": "THD_Vb",
            "description": "<p>Total harmonic distortion of the voltage (phase b).</p>",
            "computation": "avg(thd(window(Vb, THDWindow), BaseHarmonic))",
            "hidden": False
        },
        {
            "name": "THD Voltage (Phase C)",
            "identifier": "THD_Vc",
            "description": "<p>Total harmonic distortion of the voltage (phase c).</p>",
            "computation": "avg(thd(window(Vc, THDWindow), BaseHarmonic))",
            "hidden": False
        },
        {
            "name": "THD Current (Phase A)",
            "identifier": "THD_Ia",
            "description": "<p>Total harmonic distortion of the current (phase a).</p>",
            "computation": "avg(thd(window(Ia, THDWindow), BaseHarmonic))",
            "hidden": False
        },
        {
            "name": "THD Current (Phase B)",
            "identifier": "THD_Ib",
            "description": "<p>Total harmonic distortion of the current (phase b).</p>",
            "computation": "avg(thd(window(Ib, THDWindow), BaseHarmonic))",
            "hidden": False
        },
        {
            "name": "THD Current (Phase C)",
            "identifier": "THD_Ic",
            "description": "<p>Total harmonic distortion of the current (phase c).</p>",
            "computation": "avg(thd(window(Ic, THDWindow), BaseHarmonic))",
            "hidden": False
        },
        {
            "name": "Load",
            "identifier": "",
            "description": "",
            "computation": "S / MaxS",
            "hidden": False
        },
        {
            "name": "THD Voltage (Phase A) at Load Percentages",
            "identifier": "",
            "description": "<p>Total harmonic distortion of voltage (phase a) once at 25%, 50%, 75%, and 100%.</p>",
            "computation": "values(\"THD at 25% Load\",\n           avg(THD_Va if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Va if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Va if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Va if Load > 0.9 else Nothing))",
            "hidden": False
        },
        {
            "name": "THD Voltage (Phase B) at Load Percentages",
            "identifier": "",
            "description": "<p>Total harmonic distortion of voltage (phase b) once at 25%, 50%, 75%, and 100%.</p>",
            "computation": "values(\"THD at 25% Load\",\n           avg(THD_Vb if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Vb if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Vb if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Vb if Load > 0.9 else Nothing))",
            "hidden": False
        },
        {
            "name": "THD Voltage (Phase C) at Load Percentages",
            "identifier": "",
            "description": "<p>Total harmonic distortion of voltage (phase c) once at 25%, 50%, 75%, and 100%.</p>",
            "computation": "values(\"THD at 25% Load\",\n           avg(THD_Vc if Load > 0.2 and Load < 0.3   else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Vc if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Vc if Load > 0.7 and Load < 0.8   else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Vc if Load > 0.9 else Nothing))",
            "hidden": False
        },
        {
            "name": "THD Current (Phase A) at Load Percentages",
            "identifier": "",
            "description": "<p>Total harmonic distortion of current (phase a) once at 25%, 50%, 75%, and 100%.</p>",
            "computation": "values(\"THD at 25% Load\",\n           avg(THD_Ia if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Ia if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Ia if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Ia if Load > 0.9 else Nothing))",
            "hidden": False
        },
        {
            "name": "THD Current (Phase B) at Load Percentages",
            "identifier": "",
            "description": "<p>Total harmonic distortion of current (phase b) once at 25%, 50%, 75%, and 100%.</p>",
            "computation": "values(\"THD at 25% Load\",\n           avg(THD_Ib if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Ib if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Ib if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Ib if Load > 0.9 else Nothing))",
            "hidden": False
        },
        {
            "name": "THD Current (Phase C) at Load Percentages",
            "identifier": "",
            "description": "<p>Total harmonic distortion of current (phase c) once at 25%, 50%, 75%, and 100%.</p>",
            "computation": "values(\"THD at 25% Load\",\n           avg(THD_Ic if Load > 0.2  and Load < 0.3  else Nothing),\n       \"THD at 50% Load\",\n           avg(THD_Ic if Load > 0.45 and Load < 0.55 else Nothing),\n       \"THD at 75% Load\",\n           avg(THD_Ic if Load > 0.7  and Load < 0.8  else Nothing),\n       \"THD at 100% Load\",\n           avg(THD_Ic if Load > 0.9 else Nothing))",
            "hidden": False
        },
        {
            "name": "Weighted Efficiency",
            "identifier": "",
            "description": "",
            "computation": "(0.04 * avg(Efficiency if Load > 0.05 and Load < 0.1  else Nothing)) + \\\n(0.05 * avg(Efficiency if Load > 0.15 and Load < 0.2  else Nothing)) + \\\n(0.12 * avg(Efficiency if Load > 0.25 and Load < 0.35 else Nothing)) + \\\n(0.21 * avg(Efficiency if Load > 0.45 and Load < 0.55 else Nothing)) + \\\n(0.53 * avg(Efficiency if Load > 0.7  and Load < 0.8  else Nothing)) + \\\n(0.05 * avg(Efficiency if Load > 0.9 else Nothing))",
            "hidden": False
        },
        {
            "name": "Pin",
            "identifier": "",
            "description": "",
            "computation": "Idc * Vdc",
            "hidden": False
        },
        {
            "name": "Pout",
            "identifier": "",
            "description": "",
            "computation": "Va * Ia + Vb * Ib + Vc * Ic",
            "hidden": False
        },
        {
            "name": "Efficiency",
            "identifier": "",
            "description": "<p>Ratio of the usable AC output power to the sum of the DC input power.</p>",
            "computation": "avg((Pout / Pin) * 100)",
            "hidden": False
        }
    ],
    "parameters": [
        {
            "name": "Base Harmonic",
            "identifier": "BaseHarmonic",
            "description": "",
            "hidden": False,
            "default": "60"
        },
        {
            "name": "SSTC",
            "identifier": "MaxS",
            "description": "Standard test condition",
            "hidden": False,
            "default": "1000"
        },
        {
            "name": "THD Window Size",
            "identifier": "THDWindow",
            "description": "",
            "hidden": False,
            "default": "\"1s\""
        }
    ]
}

PV_ARRAY = {
    "name": "PV Array",
    "description": "",
    "kpis": [
        {
            "name": "Efficiency",
            "identifier": None,
            "description": "<p>The ratio of the electrical power output (<em>Pout</em>), compared to the solar power input, <em>Pin</em>, into the PV cell.</p>",
            "computation": "avg(Pout / Pin)",
            "hidden": False
        },
        {
            "name": "Fill Factor",
            "identifier": "FF",
            "description": "<p>Measure of the quality of the solar cell, calculated at each data point.</p>",
            "computation": "avg(Pout / (Voc * Isc))",
            "hidden": False
        },
        {
            "name": "Pin",
            "identifier": "",
            "description": "",
            "computation": "Area * Irridiation",
            "hidden": True
        },
        {
            "name": "Pout",
            "identifier": "",
            "description": "",
            "computation": "Idc * Vdc",
            "hidden": True
        }
    ],
    "parameters": [
        {
            "name": "Voc",
            "identifier": "Voc",
            "description": "",
            "hidden": False,
            "default": "520"
        },
        {
            "name": "Isc",
            "identifier": "Isc",
            "description": "",
            "hidden": False,
            "default": "970"
        },
        {
            "name": "Area (m^2)",
            "identifier": "Area",
            "description": "",
            "hidden": False,
            "default": "1450"
        }
    ]
}

WATER_QUALITY = {
  "name": "Water Quality",
  "description": "",
  "kpis": [
    {
      "name": "pH",
      "identifier": "_pH",
      "description": "",
      "computation": "avg(pH)",
      "hidden": False
    },
    {
      "name": "Total Dissolved Solids",
      "identifier": "_TDS",
      "description": "",
      "computation": "avg(Conductivity * TDSFactor)",
      "hidden": False
    },
    {
      "name": "Free Chlorine",
      "identifier": "_FreeChlorine",
      "description": "",
      "computation": "avg(FreeChlorine)",
      "hidden": False
    },
    {
      "name": "Turbidity",
      "identifier": "_Turbidity",
      "description": "",
      "computation": "avg(Turbidity)",
      "hidden": False
    },
    {
      "name": "Total Organic Carbon",
      "identifier": "_TOC",
      "description": "",
      "computation": "avg(TOC)",
      "hidden": False
    },
    {
      "name": "Dissolved Organic Carbon",
      "identifier": "_DOC",
      "description": "",
      "computation": "avg(DOC)",
      "hidden": False
    },
    {
      "name": "Ultra-violet 254",
      "identifier": "_UV254",
      "description": "",
      "computation": "avg(UV254)",
      "hidden": False
    },
    {
      "name": "Conductivity",
      "identifier": "_Conductivity",
      "description": "",
      "computation": "avg(Conductivity)",
      "hidden": False
    },
    {
      "name": "Temperature",
      "identifier": "_Temperature",
      "description": "",
      "computation": "avg(Temperature)",
      "hidden": False
    },
    {
      "name": "Differential Pressure",
      "identifier": "_DifferentialPressure",
      "description": "",
      "computation": "avg(DifferentialPressure)",
      "hidden": False
    }
  ],
  "parameters": [
    {
      "name": "TDS Factor",
      "identifier": "TDSFactor",
      "description": "",
      "hidden": False,
      "default": "0.67"
    }
  ]
}

WATER_QUANTITY = {
  "name": "Water Quantity",
  "description": "",
  "kpis": [
    {
      "name": "Pump Efficiency",
      "identifier": "",
      "description": "",
      "computation": "avg(HydraulicPower / ElectricalPower)",
      "hidden": False
    },
    {
      "name": "HydraulicPower",
      "identifier": "",
      "description": "",
      "computation": "9.81 * Q * H",
      "hidden": True
    },
    {
      "name": "Q",
      "identifier": "",
      "description": "",
      "computation": "Flow * (0.003785 / 60)",
      "hidden": True
    },
    {
      "name": "H",
      "identifier": "",
      "description": "",
      "computation": "0.70283 * DifferentialPressure",
      "hidden": True
    },
    {
      "name": "Electrical Power (kW)",
      "identifier": "ElectricalPower",
      "description": "",
      "computation": "(Va * Ia + Vb * Ib + Vc * Ic) / 1000",
      "hidden": True
    }
  ],
  "parameters": []
}
