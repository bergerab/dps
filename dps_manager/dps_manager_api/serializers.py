import json
import numbers
from datetime import timedelta

from rest_framework import serializers, viewsets

from .models import Object

import dps_services.util as util

from dplib.exceptions import CyclicGraphException
from dplib import DPL, Component

# System
class KPISerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    identifier = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    computation = serializers.CharField()
    hidden = serializers.BooleanField(required=False)

    def validate(self, data):
        # TODO: Make sure it doesn't reference itself
        try:
            DPL().parse(data['computation'])
        except Exception as e:
            raise serializers.ValidationError({ 'computation': e })

        if data['identifier']:
            if not data['identifier'].isidentifier():
                raise serializers.ValidationError({
                    'identifier': 'Illegal identifier (must be a valid Python identifier).',
                })
        
        return data

class ParameterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    identifier = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    hidden = serializers.BooleanField(required=False)
    default = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate(self, data):
        if data['identifier']:
            if not data['identifier'].isidentifier():
                raise serializers.ValidationError({
                    'identifier': 'Illegal identifier (must be a valid Python identifier).',
                })
        else:
            if not data['name'].isidentifier():
                raise serializers.ValidationError({
                    'name': 'Illegal identifier (the name is used as an identifier when no identifier is given).\nMust be a valid Python identifier.',
                })
        return data
    
class SystemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)    
    kpis = KPISerializer(many=True, default=[])
    parameters = ParameterSerializer(many=True, default=[])
    
    def validate(self, data):
        parameter_names = []
        for parameter in data['parameters']:
            name = None
            if parameter['identifier']:
                name = parameter['identifier']
            else:
                name = parameter['name']
            parameter_names.append(name)

        c = Component('Temp', parameters=parameter_names)
        for kpi in data['kpis']:
            identifier = kpi.get('identifier')
            if identifier == '':
                identifier = None
            c.add(kpi['name'], kpi['computation'], id=identifier)

        try:
            bp = c.make_bp()            
            bp._get_topological_ordering()
        except CyclicGraphException as e:
            raise serializers.ValidationError('One or more KPIs create a recursive KPI computation.')

        identifiers = []

        kpi_names = []
        kpi_errors = []
        for i, kpi in enumerate(data['kpis']):
            if kpi['name'] in kpi_names:
                kpi_errors.append({'name': ['Name is not unique.']})
            else:
                kpi_errors.append({})

            identifier = kpi['identifier'] or kpi['name']
            if identifier in identifiers:
                if kpi['identifier']:
                    kpi_errors[i]['identifier'] = ['Identifier is not unique.']
                else:
                    kpi_errors[i]['name'] = ['Identifier is not unique (name was used as identifier).']
            if identifier == 'Nothing':
                kpi_errors[i]['identifier'] = ['"Nothing" is a reserved identifier.']                
            identifiers.append(identifier)
            kpi_names.append(kpi['name'])

        parameter_names = []
        parameter_errors = []
        for i, parameter in enumerate(data['parameters']):
            if parameter['name'] in parameter_names:
                parameter_errors.append({'name': ['Name is not unique.']})
            else:
                parameter_errors.append({})

            identifier = parameter['identifier'] or parameter['name']
            if identifier in identifiers:
                if parameter['identifier']:
                    parameter_errors[i]['identifier'] = ['Identifier is not unique.']
                else:
                    parameter_errors[i]['name'] = ['Identifier is not unique (name was used as identifier).']
            if identifier == 'Nothing':
                parameter_errors[i]['identifier'] = ['"Nothing" is a reserved identifier.']                
            identifiers.append(identifier)                    
            parameter_names.append(parameter['name'])

        for error in parameter_errors:
            if error != {}:
                raise serializers.ValidationError({ 'parameters': parameter_errors, 'kpis': kpi_errors })
        for error in kpi_errors:
            if error != {}:
                raise serializers.ValidationError({ 'parameters': parameter_errors, 'kpis': kpi_errors })                

        return data

# Batch Process
class MappingSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=200)
    # You can either send a string value or an object
    # If the value is a string, there will be a value in `value`
    # Otherwise if the value is an object it will be stored in `object_value`
    value = serializers.CharField(max_length=200, required=False)
    object_value = serializers.CharField(required=False)
    
    # Whether or not this item has a chart available
    # This is major "cross cutting concern" and bad programming.
    # It should be abstracted into some new object.
    no_chart = serializers.BooleanField(required=False)
    
class IntervalSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()    

    def validate(self, data):
        start = util.validate_datetime(data['start'])
        if not start:
            raise serializers.ValidationError({
                'start': f'Start time is not in the correct format ({util.DATETIME_FORMAT_STRING}).'
            })
        
        end = util.validate_datetime(data['end'])
        if not end:
            raise serializers.ValidationError({
                'end': f'End time is not in the correct format ({util.DATETIME_FORMAT_STRING}).'
            })

        if start > end:
            raise serializers.ValidationError({
                'start': f'Start time occurs after end time.'
            })

        if end < start:
            raise serializers.ValidationError({
                'end': f'End time occurs before end time.'
            })

        if start == end:
            raise serializers.ValidationError({
                'start': f'Start and end time cannot be the same time.',
                'end': f'Start and end time cannot be the same time.',
            })

        return data

class BatchProcessSerializer(serializers.Serializer):
    name = serializers.CharField()
    dataset = serializers.CharField(default='')
    system_id = serializers.IntegerField()
    system = SystemSerializer()
    mappings = MappingSerializer(many=True, required=False)
    kpis = serializers.ListField(child=serializers.CharField())
    interval = IntervalSerializer()

    def validate(self, data):
        if not data['mappings']:
            raise serializers.ValidationError('You must choose one or more KPIs to compute.')

        system = data['system']
        parameters = []
        for parameter in system['parameters']:
            identifier = parameter['identifier'] or parameter['name']
            # TODO: Make defaults work
            # if parameter['default']:
            #     data['mappings'][identifier] = parameter['default']
            parameters.append(identifier)

        errors = {}
        for i, mapping in enumerate(data['mappings']):
            key = mapping['key']
            value = mapping['value']
            if key not in parameters:
                continue
            try:
                r = DPL().compile(value).run()                
                if not isinstance(r, numbers.Number) and not isinstance(r, timedelta):
                    raise Exception('Parameter must either represent a number or a time window (such as "1s" -- with quotes included).')
            except Exception as e:
                errors[i] = {
                            'value': ['Invalid parameter value: ' + str(e)],
                }
        if errors:
            raise serializers.ValidationError({
                'mappings': errors,
            })
            
        return data

class RequiredMappingsRequestSerializer(serializers.Serializer):
    system = SystemSerializer()
    kpi_names = serializers.ListField(child=serializers.CharField())

class JobSerializer(serializers.Serializer):
    batch_process_id = serializers.IntegerField()
    batch_process = BatchProcessSerializer()

class ScheduleSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    dataset = serializers.CharField(default='')
    
    type = serializers.IntegerField()
    # Types:
    # 0 = daily 
    # 1 = monthly (on the 1st of the month)
    start = serializers.CharField()
    end = serializers.CharField()        

class ResultsSerializer(serializers.Serializer):
    batch_process_id = serializers.IntegerField()
    results = MappingSerializer(many=True)
    
    # Statuses:
    # 0 = error
    # 1 = running
    # 2 = complete
    # 3 = queued
    status = serializers.IntegerField()
    message = serializers.CharField(required=False)
    processed_samples = serializers.IntegerField(required=False)
    total_samples = serializers.IntegerField(required=False)

    def validate(self, data):
        # TODO: Make sure batch_process_id refers to a valid object
        return data

class KPIResultSerializer(serializers.Serializer):
    system_id = serializers.IntegerField()
    batch_process_id = serializers.IntegerField()    
    name = serializers.CharField()
    value = serializers.CharField()

class GetKPIsSerializer(serializers.Serializer):
    system_id = serializers.IntegerField() 

class RegisterDatabaseManagerSerializer(serializers.Serializer):
    url = serializers.CharField()

class BatchProcessRequestSerializer(serializers.Serializer):
    page_size = serializers.IntegerField()
    page_number = serializers.IntegerField()
    system_id = serializers.IntegerField()
    search = serializers.CharField(required=False, allow_blank=True)
    order_direction = serializers.CharField(required=False, allow_blank=True)
