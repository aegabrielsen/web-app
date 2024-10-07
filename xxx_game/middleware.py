from django.utils.deprecation import MiddlewareMixin

class X_Content_Type_Nosniff_Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        return response