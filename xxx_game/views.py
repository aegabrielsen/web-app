from django.http import HttpResponse
from django.shortcuts import render
import os
import project1.settings as settings
from django.http import FileResponse
import html #HTML ESCAPE
from pymongo import MongoClient
mongo_client = MongoClient("mongo")
db = mongo_client["webapp"]
user_collection = db["users"]

# Create your views here.
def index(request):
    return render(request,"xxx_game/index.html")

def test(request):
    user_collection.insert_one({"username": "new", "message": html.escape("test"), "user_browser_id": "test"})
    users = list(user_collection.find())
    return HttpResponse(users)

# The middleware is skipped when using django.contrib.staticfiles, so here we do not use django.contrib.staticfiles, but customize the static file processing to set X-Content-Type-Options: nosniff.
def custom_static_view(request, path):
    file_path = os.path.join(settings.BASE_DIR,'xxx_game/static', path)
    response = FileResponse(open(file_path, 'rb'))
    response['Cache-Control'] = 'public, max-age=3600'
    response['X-Content-Type-Options'] = 'nosniff'
    return response

# This gets the login form request
def login(request):
    password = request.POST.get("password", None)
    return HttpResponse(password)

# This gets the registration form request
def register(request):
    print(request)
    password = request.POST.get("password", None)
    return HttpResponse(password)