from datetime import datetime

DATETIME_FORMAT_STRING = '%Y-%m-%d %H:%M:%S.%f'
'''
The datetime format used in JSON requests.

Example: 2020-06-30 03:54:45.175489 means June 30th, 2020 at 3:54:45AM and 175489 microseconds.
'''

def parse_datetime(datetime_string):
    return datetime.strptime(datetime_string, DATETIME_FORMAT_STRING)

def format_datetime(datetime_object):
    return datetime.strftime(datetime_object, DATETIME_FORMAT_STRING)

def validate_datetime(datetime_string, datetime_format_string=DATETIME_FORMAT_STRING):
    try:
        return datetime.strptime(datetime_string, datetime_format_string)
    except ValueError:
        return None
