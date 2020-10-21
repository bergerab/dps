def make_builtin_decorator(env):
    def builtin(name=None):
        def decorator(f):
            def wrapper(*args, **kwargs):
                if kwargs:
                    # kwargs aren't supported
                    raise Exception('Keyword arguments are not allowed in DPL.')
                return f(*args)

            # If a name is given, use that name, otherwise use the function name
            nonlocal name
            name = name if name is not None else f.__name__
            env[name] = wrapper
            
            return wrapper
        return decorator
    return builtin
