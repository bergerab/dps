'''
Implementation of the DPLang builtin functions/operators.
'''

def add(args):
    x, y = args
    return x + y

def sub(args):
    x, y = args
    return x - y

def mul(args):
    x, y = args
    return x * y

def div(args):
    x, y = args
    return x / y

def floordiv(args):
    x, y = args
    return x // y

def average(args):
    data_series = args[0]
    return data_series.average()

def window(args):
    print('IN WINDOW')    
    data_series, duration = args
    if len(args) > 2:
        return data_series.time_window(duration, args[2])        
    else:
        return data_series.time_window(duration)
