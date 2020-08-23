class ValidationException(Exception):
    def __init__(self, errors):
        self.errors = errors
        self.message = '\n'.join(self.errors)
        super().__init__(self.message)        
        
def quoted(x, n=200):
    '''Add quotation marks around `x`, and take only the first `n` letters.'''
    return f'"{str(x)[:n]}"'

def make_api_url(name, version=1):
    return f'/api/v{version}/{name}'

class RequestValidator:
    def __init__(self, request):
        self.requests = [request]
        self.errors = []
        self.prefixes = []

    def require(self, key, required_type=None, optional=False, one_of=None):
        value = self.requests[-1].get(key)
        prefix = ''.join(self.prefixes)
        parameter_name = quoted(prefix + key)
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

    def scope(self, request, name):
        self.requests.append(request)
        self.prefixes.append(name + '.')
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.prefixes:
            self.prefixes.pop()
        self.requests.pop()
        if self.errors:
            raise ValidationException(self.errors)
