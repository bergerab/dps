from .series import Series

def make_builtin_decorator(env):
    def builtin(name=None, aggregate=False):
        def decorator(f):
            def wrapper(*args, **kwargs):
                if kwargs:
                    # kwargs aren't supported
                    raise Exception('Keyword arguments are not allowed in DPL.')
                if args and aggregate:
                    if isinstance(args[0], Series):
                        def perform_f(series):
                            return f(series, *args[1:])
                        return args[0].aggregate(perform_f)
                    else:
                        raise Exception('Builtin asked to aggregate, but was given non-series argument.')
                return f(*args)

            # If a name is given, use that name, otherwise use the function name
            nonlocal name
            name = name if name is not None else f.__name__
            env[name] = wrapper
            
            return wrapper
        return decorator
    return builtin
