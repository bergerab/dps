import json

from rest_framework import serializers, viewsets

from .models import Object

import dps_services.util as util
from dplib import DPL

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
