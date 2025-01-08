from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTOrGuestAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if len(token) > 6:
            jwt = JWTAuthentication()
            return jwt.authenticate(request)
        else:
            return None