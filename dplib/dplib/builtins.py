from .dpl_util import make_builtin_decorator

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
def thd(series, base_harmonic, fs=None):
    pass
