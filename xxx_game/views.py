from django.http import HttpResponse
from django.shortcuts import render
import os
import project1.settings as settings
from django.http import FileResponse
import html #HTML ESCAPE
from pymongo import MongoClient
import bcrypt
mongo_client = MongoClient("mongo")
db = mongo_client["webapp"]
user_collection = db["users"]

# Create your views here.
def index(request):
    return render(request,"xxx_game/index.html")

def test(request):
    user_collection.insert_one({"username": "new", "message": html.escape("test")})
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

    # Get form fields
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)

    # If the user does not exist or there are duplicates, do nothing
    if user_collection.count_documents({"username" : username}) != 1:
        return render(request,"xxx_game/index.html")
    
    user = user_collection.find_one({"username" : username})

    # If the password, salted and hashed, matches the hashed password in the DB, do something...
    if bcrypt.hashpw(password.encode(), user["salt"]) == user["hash"]:
        return render(request,"xxx_game/index.html", {"username" : username})

    return render(request,"xxx_game/index.html")

# This gets the registration form request
def register(request):

    # Get form fields
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    retype_password = request.POST.get("retype_password", None)
    
    # If the passwords do not match, do nothing
    if password != retype_password:
        return render(request,"xxx_game/index.html")

    # If the user is already registered, do nothing
    if user_collection.count_documents({"username" : username}) != 0:
        return render(request,"xxx_game/index.html")

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode(), salt)

    user = {"username" : username, "salt" : salt, "hash" : hash}

    user_collection.insert_one(user)

    return render(request,"xxx_game/index.html")

# Logout route
def logout(request):
    auth_token = request.COOKIES.get('auth_token')
    # user_collection.insert_one({"username": "asdf", "message": html.escape("qwerty")})
    # user_collection.update_one({ "username": "new"}, {"$unset": {"message": ""}}) # working update
    if auth_token is None: # User is not logged in to begin with
        return render(request,"xxx_game/index.html")
    # Hash token and check for it in the database
    auth_token_hash = bcrypt.hashpw(auth_token.encode(), b'')
    # user_collection.findOneAndUpdate({ auth_token: auth_token_hash}, {"$unset:" "auth_token"}) # Delete auth token field from DB
    user_collection.update_one({ "auth_token": auth_token_hash}, {"$unset": {"auth_token": ""}}) # Delete auth token field from DB
    return render(request,"xxx_game/index.html")