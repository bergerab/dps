from .decorators import make_builtin_decorator

from .series import Series

BUILTINS = {}
builtin = make_builtin_decorator(BUILTINS)

@builtin()
def window(series, duration):
    return series.window(duration)

@builtin('avg')
def average(series):
    if isinstance(series, Series):
        if series.is_windowed(): return series.average()
        else: return series.average_aggregation()
    else: raise Exception('Unsupported type for average.')

@builtin()
def min(series):
    if isinstance(series, Series):
        if series.is_windowed(): return series.min()
        else: return series.min_aggregation()
    else: raise Exception('Unsupported type for min.')

@builtin()
def max(series):
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

@builtin()
def thd(series, base_harmonic, fs):
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
