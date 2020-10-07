import json

from rest_framework import serializers, viewsets

from .models import Object

# System
class KPISerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    identifier = serializers.CharField(max_length=200)
    description = serializers.CharField()
    computation = serializers.CharField()
    hidden = serializers.BooleanField()

    def validate(self, data):
        # Make sure computation parses and is valid
        # Make sure it doesn't reference itself
        # Make sure identifier doesn't have spaces
        return data    

class ParameterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    identifier = serializers.CharField(max_length=200)
    description = serializers.CharField()
    hidden = serializers.BooleanField()
    default = serializers.CharField(max_length=200)

    def validate(self, data):
        # Make sure identifier doesn't have spaces
        return data
    
class SystemSerializer(serializers.Serializer):
    system_id = serializers.IntegerField(default=0)
    name = serializers.CharField(max_length=200)
    kpis = KPISerializer(many=True)
    parameters = ParameterSerializer(many=True)

    def create(self, data):
        return Object.objects.create(
            name=data['name'],
            kind='System',
            value=json.dumps(data),
        )

# Batch Process
class MappingSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=200)
    value = serializers.CharField(max_length=200)
    
class IntervalSerializer(serializers.Serializer):
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()    

class BatchProcessSerializer(serializers.Serializer):
    batch_process_id = serializers.IntegerField(default=0)
    mappings = MappingSerializer(many=True)
    kpis = KPISerializer(many=True)
    interval = IntervalSerializer()

# Batch Process Progress
class ProgressSerializer(serializers.Serializer):
    progress_id = serializers.IntegerField(default=0)
    batch_process_id = serializers.IntegerField()
    state = serializers.CharField()
    time = serializers.DateTimeField()
