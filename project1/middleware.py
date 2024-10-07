
from django.utils.deprecation import MiddlewareMixin

class X_Content_Type_Nosniff_Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/static/'):
            response['X-Content-Type-Options'] = 'nosniff'
        return response