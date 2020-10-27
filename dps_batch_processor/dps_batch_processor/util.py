import re

def url_is_valid(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def make_component(system):
    '''
    Creates a `dplib.Component` from a system description.
    '''
    component = dplib.Component('Temp')
    for kpi in system['kpis']:
        identifier = kpi['identifier']
        if identifier == '':
            identifier = None
        component.add(kpi['name'], kpi['computation'], id=identifier)
    return component

def get_parameter_identifiers(system):
    '''
    Returns all parameter identifiers for the `system`.
    '''
    parameters = []
    for parameter in system['parameters']:
        identifier = parameter['identifier'] or parameter['name']                        
        if parameter['default']:
            mappings[identifier] = parameter['default']
        parameters.append(identifier)
    return parameters

def get_signal_identifiers(component, batch_proces, parameters):
    '''
    Returns the identifier names of each signal required for the `batch_process`.
    '''
    signals = []
    for name in component.get_required_inputs(batch_process['kpis']):
        if name not in parameters:
            signals.append(name)
    return signals

def get_mappings(batch_process):
    '''
    Retrieves the mappings from a `batch_process` as a dictionary.
    '''
    return { mapping['key']: mapping['value']
             for mapping in batch_process['mappings']}

def evaluate_parameters(mappings, parameters):
    '''
    The text of each parameter must be evaluated to yield a Python value.

    Updates `mappings` with the values yielded by evaulation.

    For example, a parameter might have the string value of "1.23", but we need the
    Python value which is `1.23`.
    '''
    for key in mappings:
        if key in parameters:
            value = mappings[key]
            mappings[key] = dplib.DPL().compile(value).run(mappings)

def dict_to_mappings(d):
    '''
    Converts a Python dictionary to a mapping object (list of dictionaries) 
    that is expected by the DPS Manager's API.
    '''
    results = []
    for key in d:
        results.append({
            'key': key,
            'value': aggregations[key],
        })
    return results
    
