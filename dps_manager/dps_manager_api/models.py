from django.db import models
from rest_framework import serializers, viewsets

from enum import IntEnum
import json

from .util import Diff

class Object(models.Model):
    object_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    kind = models.CharField(max_length=200)
    value = models.TextField()        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)








class System(models.Model):
    '''
    A collection of KPI computations and parameters which can be ran as a batch process.
    '''
    system_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class KPI(models.Model):
    '''
    A computation that can be selected and run in a dashboard.

    KPIs are defined for system originally, then batch processes can be run on systems.
    Batch processes copy the KPIs from the system to store them for later
    '''
    kpi_id = models.AutoField(primary_key=True, null=True)
    batch_process_id = models.AutoField(primary_key=True, null=True)    
    name = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200, null=True)
    system = models.ForeignKey(System, related_name='kpis', on_delete=models.CASCADE)
    batch_process = models.ForeignKey(BatchProcess, related_name='kpis', on_delete=models.CASCADE)
    computation = models.TextField()
    description = models.TextField(null=True, blank=True)
    
    # Allow for KPIs to be hidden from the end user, so that KPIs can be defined
    # and used for their intermidiate results.
    hidden = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Parameter(models.Model):
    '''
    A parameter name definition.

    Indicates that a system takes a constant value as input with some parameter name.
    '''
    parameter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True, blank=True)    
    default = models.CharField(max_length=200, null=True)
    system = models.ForeignKey(System, related_name='parameters', on_delete=models.CASCADE)
    hidden = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BatchProcess(models.Model):
    batch_process_id = models.AutoField(primary_key=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class KPIAssignment(models.Model):
    '''
    Assigns a KPI to be run in a BatchProcess.
    '''
    batch_process = models.ForeignKey(BatchProcess, on_delete=models.CASCADE)
    kpi = models.ForeignKey(KPI, on_delete=models.CASCADE)

class MappingTypes(IntEnum):
  SIGNAL = 1
  PARAMETER = 2
  
  @classmethod
  def choices(cls):
    return [(key.value, key.name) for key in cls]

class Mapping(models.Model):
    '''
    A mapping from key to value (for parameters and signals).
    '''
    batch_process = models.ForeignKey(BatchProcess, on_delete=models.CASCADE)
    type = models.IntegerField(choices=MappingTypes.choices())
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

class BatchProcessProgress(models.Model):
    '''
    The latest state of a Batch Process stores time and aggregation information.
    '''
    batch_process = models.ForeignKey(BatchProcess, on_delete=models.CASCADE)
    state = models.TextField()
    time = models.DateTimeField()

class KPISerializer(serializers.ModelSerializer):
    queryset=KPI.objects.filter(removed=False).all()    
    class Meta:
        model = KPI
        fields = ['name', 'identifier', 'computation',
                  'description', 'hidden', 'removed',
                  'created_at', 'updated_at']

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['name', 'hidden', 'default', 'removed']

class SystemSerializer(serializers.ModelSerializer):
    kpis = KPISerializer(many=True, required=False)
    parameters = ParameterSerializer(many=True, required=False)

    class Meta:
        model = System
        fields = ['system_id', 'name', 'kpis',
                  'parameters', 'created_at', 'updated_at']
    
    def create(self, data):
        kpis = data.pop('kpis', [])
        parameters = data.pop('parameters', [])
        system = System.objects.create(**data)
        for kpi in kpis:
            KPI.objects.create(system=system, **kpi)
        for parameter in parameters:
            Parameter.objects.create(system=system, name=parameter['name'])
        return system

    def update(self, instance, data):
        kpis = {}
        for kpi in data.pop('kpis', []):
            kpis[kpi['name']] = kpi
            
        existing_kpis = KPI.objects.filter(system=instance).all()
        kpi_diff = Diff(map(lambda x: x.name, existing_kpis),
                        kpis.keys())
        deletions = kpi_diff.get_deletions()
        unchanged = kpi_diff.get_unchanged()
        for kpi in existing_kpis:
            if kpi.name in deletions:
                kpi.removed = True
                kpi.save()                
            elif kpi.name in unchanged:
                d = kpis[kpi.name]
                kpi.identifier = d.get('identifier', kpi.identifier)
                kpi.computation = d.get('computation', kpi.computation)
                kpi.description = d.get('description', kpi.description)                       
                kpi.hidden = d.get('hidden', kpi.hidden)                
                kpi.removed = False
                kpi.save()
                
        additions = kpi_diff.get_additions()
        for name, kpi in kpis.items():
            if name in additions:
                KPI.objects.create(system=instance, **kpi)
        
        parameters = {}
        for parmeter in data.pop('parameters', []):
            parameters[parameter['name']] = parameter

        existing_parameters = Parameter.objects.filter(system=instance).all()        
        parameter_diff = Diff(map(lambda x: x.name, existing_parameters),
                              map(lambda d: d['name'], parameters))

        deletions = parameter_diff.get_deletions()
        unchanged = parameter_diff.get_unchanged()
        for parameter in existing_parameters:
            if parameter.name in deletions:
                parameter.removed = True
                parameter.save()                
            elif parameter.name in unchanged:
                d = parameters[kpi.name]
                parameter.identifier = d.get('identifier', kpi.identifier)  
                parameter.default = d.get('default', kpi.default)
                parameter.hidden = d.get('hidden', kpi.hidden)
                parameter.description = d.get('description', kpi.description)                       
                parameter.removed = False
                parameter.save()
                
        additions = parameter_diff.get_additions()
        for name, kpi in kpis.items():
            if name in additions:
                Parameter.objects.create(system=instance, **kpi)
        
        return instance

class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer

# class BatchProcessSerializer(serializers.ModelSerializer):
#     parameters = serializers.SlugRelatedField(
#         many=True,
#         slug_field='name',
#         read_only=True,
#         required=False,
#     )
    
#     class Meta:
#         model = BatchProcess
#         fields = ['kpis', 'start_time', 'end_time']

# class MappingSerializer(serializers.ModelSerializer):
#     kpis = KPISerializer(many=True, required=False)
#     class Meta:
#         model = System
#         fields = ['name', 'kpis', 'parameters', 'created_at', 'updated_at']    

# class ParameterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Parameter
#         fields = ['name']

# class SystemViewSet(viewsets.ModelViewSet):
#     queryset = System.objects.all()
#     serializer_class = SystemSerializer


