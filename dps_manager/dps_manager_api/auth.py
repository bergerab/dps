from datetime import datetime, timedelta
from django.utils import timezone

from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from .models import Object, AuthToken

def require_auth(f):
    @csrf_exempt
    def wrapped(request, *args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            raise PermissionDenied('Request was missing Authorization header.')        
        type, token = auth.split(' ')
        # Two types: 
        #            API means the token is an API key
        #            Anything else means the token is for a user
        if type == 'API':
            if Object.objects.filter(kind='APIKey', name=token).first():
                return f(request, *args, **kwargs)
            raise PermissionDenied('Invalid API token. (' + token + ')') 
        elif type == 'Bearer':
            token = AuthToken.objects.filter(uid=token).first()
            if not token:
                raise PermissionDenied('Invalid bearer token.')
            # Token has expired
            if timezone.now() >= token.expires_at:
                raise PermissionDenied('Bearer token expired.')
            # Update the expires at
            token.expires_at = timezone.now() + timedelta(hours=1)
            token.save()
        else:
            raise PermissionDenied('Invalid Authorization type (should have been either API or Bearer)')
        return f(request, *args, **kwargs)
    return wrapped
