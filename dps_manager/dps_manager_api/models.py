from django.db import models
from django.contrib.auth import get_user_model

class Object(models.Model):
    object_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True)
    ref = models.CharField(max_length=200, null=True)    
    kind = models.CharField(max_length=200)
    value = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

User = get_user_model()
class AuthToken(models.Model):
    uid = models.CharField(max_length=2000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
