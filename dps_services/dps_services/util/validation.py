from .string import quoted
from .datetime import validate_datetime

class RequestValidator:
    def __init__(self, request):
        self.requests = [request]
        self.errors = []
        self.prefixes = []

    def require(self, key, *args, default=None, **kwargs):
        '''Require a key to be in the request, along with regular validation'''
        value = self.requests[-1].get(key, default)
        return self.validate(value, key, *args, **kwargs)

    def validate(self, value, name, required_type=None, optional=False, one_of=None, datetime_format_string=None):
        '''Ensure the value has certain properties (if not, collect the issue in a list of validation errors)'''
        prefix = ''.join(self.prefixes)
        parameter_name = quoted(prefix + name)                
        skipped = optional and not value
        if not optional and not value:
            self.errors.append(f'Request is missing required parameter {parameter_name}.')
        if not skipped:
            if required_type is not None and not isinstance(value, required_type):
                self.errors.append(f'Expected {required_type.__name__} type, but received {type(value).__name__} type for parameter {parameter_name}.')
            if datetime_format_string is not None:
                if isinstance(value, list): # Map a list of strings to a list of datetimes in the `datetime_format_string` format.
                    values = []
                    for i, item in enumerate(value):
                        datetime = validate_datetime(item, datetime_format_string)
                        if not value:
                            self.errors.append(f'Expected datetime string in format {quoted(datetime_format_string)} at index {i} for list {parameter_name}, but received {quoted(value)}.')
                        values.append(datetime)
                    value = values
                else:
                    datetime = validate_datetime(value, datetime_format_string)
                    if not value:
                        self.errors.append(f'Expected datetime string in format {quoted(datetime_format_string)}, but received {quoted(value)}.')
                    value = datetime
            if one_of is not None and value not in one_of:
                possibilities = quoted(one_of[0])
                if len(one_of) > 1:
                    last = f' or {quoted(one_of[-1])}'
                    possibilities = 'either ' + ', '.join(map(quoted, one_of[:-1])) + last
                self.errors.append(f'Expected parameter {parameter_name} to be {possibilities}, but was {quoted(value)}.')
        return value
 
    def scope(self, name):
        self.requests.append(self.requests[-1][name]) # TODO: Handle case for when this doesn't exist
        self.prefixes.append(name + '.')
        return self

    def scope_list(self, name, i):
        request_list = self.requests[-1][name]
        self.requests.append(request_list[i]) # TODO: Handle case for when this doesn't exist
        self.prefixes.append(f'{name}[{i}].')
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.prefixes:
            self.prefixes.pop()
        self.requests.pop()
        # If we have popped off all the scoped requests, and there are errors, throw a validation exception
        if not self.requests and self.errors:
            raise ValidationException(self.errors)

class ValidationException(Exception):
    def __init__(self, errors):
        self.errors = errors
        self.message = '\n'.join(self.errors)
        super().__init__(self.message)
