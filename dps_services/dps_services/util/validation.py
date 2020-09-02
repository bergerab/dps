from .string import quoted

class RequestValidator:
    def __init__(self, request):
        self.requests = [request]
        self.errors = []
        self.prefixes = []

    def require(self, key, *args, default=None, **kwargs):
        '''Require a key to be in the request, along with regular validation'''
        value = self.requests[-1].get(key, default)
        return self.validate(value, key, *args, **kwargs)

    def validate(self, value, name, required_type=None, optional=False, one_of=None):
        '''Ensure the value has certain properties (if not, collect the issue in a list of validation errors)'''
        prefix = ''.join(self.prefixes)
        parameter_name = quoted(prefix + name)                
        skipped = optional and not value
        if not optional and not value:
            self.errors.append(f'Request is missing required parameter {parameter_name}.')
        elif not skipped and required_type is not None and not isinstance(value, required_type):
            self.errors.append(f'Expected {required_type.__name__} type, but received {type(value).__name__} type for parameter {parameter_name}.')
        elif not skipped and one_of is not None and value not in one_of:
            possibilities = quoted(one_of[0])
            if len(one_of) > 1:
                last = f' or {quoted(one_of[-1])}'
                possibilities = 'either ' + ', '.join(map(quoted, one_of[:-1])) + last
            self.errors.append(f'Expected parameter {parameter_name} to be {possibilities}, but was {quoted(value)}.')
        return value
 
    def scope(self, name):
        self.requests.append(self.requests[-1][name]) # TODO: handle case for when this doesn't exist
        self.prefixes.append(name + '.')
        return self

    def scope_list(self, name, i):
        request_list = self.requests[-1][name]
        self.requests.append(request_list[i]) # TODO: handle case for when this doesn't exist
        self.prefixes.append(f'{name}[{i}].')
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.prefixes:
            self.prefixes.pop()
        self.requests.pop()
        # if we have popped off all the scoped requests, and there are errors, throw a validation exception
        if not self.requests and self.errors:
            raise ValidationException(self.errors)

class ValidationException(Exception):
    def __init__(self, errors):
        self.errors = errors
        self.message = '\n'.join(self.errors)
        super().__init__(self.message)
