from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed



class ApiKeyAuthentication(BaseAuthentication):
    keyword = 'Token'  

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise AuthenticationFailed('Authorization header mavjud emas.')

        
        try:
            keyword, api_key = auth_header.split(' ')
        except ValueError:
            raise AuthenticationFailed('Authorization header noto‘g‘ri formatda.')

        if keyword != self.keyword or api_key != settings.API_KEY:
            raise AuthenticationFailed('API key noto‘g‘ri yoki yuborilmagan.')

    
        user = None

        return (user, None)







