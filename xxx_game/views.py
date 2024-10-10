from django.http import HttpResponse
from django.shortcuts import render
import os
import project1.settings as settings
from django.http import FileResponse

# Create your views here.
def index(request):
    return render(request,"xxx_game/index.html")

# The middleware is skipped when using django.contrib.staticfiles, so here we do not use django.contrib.staticfiles, but customize the static file processing to set X-Content-Type-Options: nosniff.
def custom_static_view(request, path):
    file_path = os.path.join(settings.BASE_DIR,'xxx_game/static', path)
    response = FileResponse(open(file_path, 'rb'))
    response['Cache-Control'] = 'public, max-age=3600'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

# This gets the login form request
def login(request):
    return HttpResponse(request)

# This gets the registration form request
def register(request):
    print(request)
    return HttpResponse(request)