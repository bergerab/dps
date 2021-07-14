from .decorators import make_builtin_decorator

from .series import Series
from .aggregation import Aggregation, ValuesAggregation, AbsAggregation, CumSumAggregation

import numpy as np
import math

BUILTINS = {}
builtin = make_builtin_decorator(BUILTINS)

@builtin('avg')
def average(series):
    if isinstance(series, Series):
        if series.is_windowed(): return series.average()
        else: return series.average_aggregation()
    else: raise Exception('Unsupported type for average.')

@builtin('cumsum')
def cumsum(x):
    if isinstance(x, Series):
        cumsum = np.cumsum(x.series)
        return CumSumAggregation(Series(cumsum), cumsum[-1])
    else:
        raise Exception('Unexpected input datatype for cumsum.')

@builtin('values')
def values_agg(*args):
    for i, arg in enumerate(args):
        if i % 2 == 1 and not isinstance(arg, Aggregation):
            raise Exception('Invalid type passed to values aggregation. Values aggregation takes a list of strings and aggregations.')
        elif i % 2 == 0 and not isinstance(arg, str):
            raise Exception('Invalid type passed to values aggregation. Values aggregation takes a list of strings and aggregations.')            
    # ValuesAggregation doesn't have any `series` to propagate, so we pass an empty list
    # This is because storing a list of results in a single database column is not supported
    # in most databases. This means we cannot plot the result of a ValuesAggregation.
    d = {}
    for i in range(0, len(args), 2):
        key = args[i]
        value = args[i + 1]
        d[key] = value
    return ValuesAggregation(Series([]), d)

@builtin()
def window(series, duration):
    return series.window(duration)

@builtin()
def abs(obj):
    if isinstance(obj, Series):
        obj.series = np.abs(obj.series)
    else: # Assume its an aggregation
        return AbsAggregation(obj.series, obj)
    return obj

@builtin('sum')
def _sum(series):
    if isinstance(series, Series):
        if series.is_windowed(): return series.sum()
        else: return series.sum_aggregation()
    else: raise Exception('Unsupported type for sum.')

@builtin('avg')
def average(series):
    if isinstance(series, Series):
        if series.is_windowed(): return series.average()
        else: return series.average_aggregation()
    else: raise Exception('Unsupported type for average.')

@builtin('min')
def _min(series):
    if isinstance(series, Series):
        if series.is_windowed(): return series.min()
        else: return series.min_aggregation()
    else: raise Exception('Unsupported type for min.')

@builtin('max')
def _max(series):
    if isinstance(series, Series):
        if series.is_windowed(): return series.max()
        else: return series.max_aggregation()
    else: raise Exception('Unsupported type for max.')

@builtin('if')
def _if(test, body, orelse, env):
    '''
    Code called when an expression of the form:
        `body` if `test` else `orelse`
    is found in the source.

    The `compile` function is used here to preserve Python's semantics where
    `body` is only evaluated when `test` is true and `orelse` is only evaluated whe
    `test` is false.
    '''
    test_value = test.compile().run(env)
    # If using series, the if expression behaves as a call to `Series.when`.
    if isinstance(test_value, Series):
        return test_value.when(body.compile().run(env), orelse.compile().run(env))
    # Otherwise, it is the same as a normal if expression.
    if test_value:
        return body.compile().run(env)
    return orelse.compile().run(env)

@builtin('and')
def _and(series1, series2):
    if isinstance(series1, Series):
        return series1._and(series2)
    elif isinstance(series2, Series):
        return series2._and(series1)
    else:
        return series1 and series2

@builtin('or')
def _or(series1, series2):
    if isinstance(series1, Series):
        return series1._or(series2)
    elif isinstance(series2, Series):
        return series2._or(series1)
    else:
        return series1 or series2

@builtin(aggregate=True)
def thd(series, base_harmonic=None):
    # At least two values are needed to determine sampling rate.
    # Even more than this are needed to do an FFT as well, but
    # that will return 0 as well, just not error like have under 2 datapoints would.
    if len(series) < 2:
        return None
        #raise Exception(f'Insufficient number of samples (was given {len(series)}) to compute THD.')
    
    fft_vals = np.abs(np.fft.fft(series))

    # If provided a base harmonic, use it
    if base_harmonic:
        sample_rate = 1 / (series.index[1] - series.index[0]).total_seconds()
        # How many seconds of data `series` contains
        # This determines where the base harmonic exists in fft_vals
        seconds_of_data = len(series)/sample_rate
        if seconds_of_data > 0:
            base_harmonic = int(seconds_of_data*base_harmonic)
        fund_freq = fft_vals[base_harmonic]
    else:
        # Otherwise, derive the base harmonic by finding the first peak
        fund_freq = 0
        base_harmonic = 0
        for frequency, value in enumerate(fft_vals[:int(len(fft_vals)/2)]):
            if value > fund_freq:
                fund_freq = value
                base_harmonic = frequency

    if fund_freq == 0:
        return None
        #raise Exception(f'Insufficient number of samples (was given {len(series)}) to derive fundamental frequency for THD.')

    sum = 0 
    harmonic = 2*base_harmonic
    offset = int(base_harmonic/2)

    while harmonic < len(fft_vals)/2:
        peak = np.max(fft_vals[harmonic - offset : harmonic + offset])
        sum += peak * peak
        harmonic += base_harmonic
    square_sum = np.sqrt(sum)
    return 100 * (square_sum / fund_freq)

@builtin('thd2', aggregate=True)
def thd2(series, base_harmonic, fs):
    L = len(series)

    # Next power of 2, for increased resolution
    n = int(2 ** (np.ceil(np.log2(L)) + 1))
    vf = np.abs(np.fft.fft(series, n))
    f = fs * np.arange(0, (n / 2) + 1) / n
    vf = vf[:n // 2 + 1]
    fund_ind = np.argmax(vf[1:])
    fund_ind = fund_ind + 1
    f_fund = f[fund_ind]
    p_fund = vf[fund_ind]
    f_hrm = base_harmonic + f_fund

    # look for harmonic bin around  the true harmonic
    f_hrm = f_fund + base_harmonic
    v_rms_harmonics = 0
    while f_hrm < f[-1] - base_harmonic:
        harm_ind = ((f <= f_hrm + 1.3 * fs / n) & (f >= f_hrm - 1.3 * fs / n)).nonzero()[0]
        hrm = np.argmax(vf[harm_ind])
        hrm = harm_ind[hrm]
        hrm_frq = f[hrm]
        hrm_pwr = vf[hrm]
        f_hrm = f_hrm + base_harmonic
        v_rms_harmonics = v_rms_harmonics + (hrm_pwr ** 2)

    return 100 * np.sqrt(v_rms_harmonics) / p_fund


@builtin('rms', aggregate=True)
def rms(series):
    data = series.array
    ret = 0
    i = 0
    size = len(data)

    while(i < size):
        x = data[i]
        ret = ret + x * x
        i = i + 1

    return math.sqrt(ret/size)

