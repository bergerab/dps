import json

from rest_framework import serializers, viewsets

from .models import Object

import dps_services.util as util
from dplib import DPL, Component, CyclicGraphException

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
        # Make sure topological ordering succeeds

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
    value = serializers.CharField(max_length=200)
    
class IntervalSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()    

    def validate(self, data):
        if not util.validate_datetime(data['start']):
            raise serializers.ValidationError({
                'start': f'Start time is not in the correct format ({util.DATETIME_FORMAT_STRING}).'
            })

        if not util.validate_datetime(data['end']):
            raise serializers.ValidationError({
                'end': f'End time is not in the correct format ({util.DATETIME_FORMAT_STRING}).'
            })

        return data

class BatchProcessSerializer(serializers.Serializer):
    mappings = MappingSerializer(many=True, required=False)
    kpis = KPISerializer(many=True, required=False)
    interval = IntervalSerializer()

# Batch Process Progress
class ProgressSerializer(serializers.Serializer):
    batch_process_id = serializers.IntegerField()
    state = serializers.CharField()
    time = serializers.CharField()

    def validate(self, data):
        # TODO: Make sure batch_process_id refers to a valid object
        if not util.validate_datetime(data['time']):
            raise serializers.ValidationError({
                'time': f'Time is not in the correct format ({util.DATETIME_FORMAT_STRING}).'
            })

        return data

# RequiredMappingsRequestSerializer
class RequiredMappingsRequestSerializer(serializers.Serializer):
    system = SystemSerializer()
    kpi_names = serializers.ListField(child=serializers.CharField())
