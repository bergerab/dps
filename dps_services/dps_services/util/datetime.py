from datetime import datetime

DATETIME_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%f'

def parse_datetime(datetime_string, datetime_format_string):
    '''
    The datetime format used in JSON requests.

    Example: 2020-06-30 03:54:45.175489 means June 30th, 2020 at 3:54:45AM and 175489 microseconds.
    '''
    return datetime.strptime(datetime_string, datetime_format_string)

def validate_datetime(datetime_string, datetime_format_string=DATETIME_FORMAT_STRING):
    try:
        return parse_datetime(datetime_string, datetime_format_string)
    except ValueError:
        return None
