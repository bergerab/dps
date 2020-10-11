import json

from rest_framework import serializers, viewsets

from .models import Object

from dplib import DPL

# System
class KPISerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    identifier = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    computation = serializers.CharField()
    hidden = serializers.BooleanField(required=False)

    def validate(self, data):
        # TODO: Make sure computation parses and is valid
        # TODO: Make sure it doesn't reference itself
        # TODO: Make sure identifier doesn't have spaces
        DPL().parse(data['computation'])
        return data

class ParameterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    identifier = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    hidden = serializers.BooleanField(required=False)
    default = serializers.CharField(max_length=200, required=False, allow_blank=True)

    def validate(self, data):
        # TODO: Make sure identifier doesn't have spaces
        return data
    
class SystemSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
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
        # TODO: Make sure times are in correct format
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
        # TODO: Validate time
        return data

# RequiredMappingsRequestSerializer
class RequiredMappingsRequestSerializer(serializers.Serializer):
    kpis = KPISerializer(many=True)
    parameters = ParameterSerializer(many=True, default=[])
