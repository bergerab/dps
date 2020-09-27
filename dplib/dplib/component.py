from dplib import KPI


# TODO: error if name contains spaces
# 
class Component:
    def __init__(self, name, parameters=[], kpis={}, display_name=None):
        self.name = d['name']

        errors = []
        for required_parameter in required_parameters:
            if required_parameter not in parameters:
                errors.append(f'Required parameter "{required_parameter}" not given in parameter dictionary for "{self.name}" component.')
        if errors:
            raise Exception('\n'.join(errors))

        self.mappings = mappings
        self.parameters = parameters

    
