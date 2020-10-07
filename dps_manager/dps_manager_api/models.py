from django.db import models

class Object(models.Model):
    object_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    ref = models.CharField(max_length=200, null=True)    
    kind = models.CharField(max_length=200)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
