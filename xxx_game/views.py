from django.http import HttpResponse
from django.shortcuts import render, redirect
import os
import project1.settings as settings
from django.http import FileResponse
import html #HTML ESCAPE
from pymongo import MongoClient
import bcrypt
import uuid
mongo_client = MongoClient("mongo")
db = mongo_client["webapp"]
user_collection = db["users"]
global_salt = b'$2b$12$ldSsU24BK6EPANRbUpvXRu'

<<<<<<< Updated upstream
def get_db_field_from_auth(request, field):
    # Pass request into this function and it will attempt to retrieve a user from the auth_token cookie.
    # If no auth_token exists, returns None.
    # Pass the field you want to get with field as a string. So for username pass "username"
    auth_token = request.COOKIES.get("auth_token")
    if auth_token is None:
        return None

    auth_token = request.COOKIES.get("auth_token")
    auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt)

    user = user_collection.find_one({"auth_token_hash" : auth_token_hash})
    if user is None:
        return None
    return user.get(field)

=======
>>>>>>> Stashed changes
# Create your views here.
def index(request):
    
    auth_token = request.COOKIES.get("auth_token")
    if auth_token is None:
        return render(request,"xxx_game/index.html")
    auth_token = request.COOKIES.get("auth_token")
    auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt)
    user = user_collection.find_one({"auth_token_hash" : auth_token_hash})
    # Above code is working but replaced with a function for cleaner code. Revert to this if function doesn't work
    
    # test_user = user_collection.find_one({"username" : "testuser"})
    # return HttpResponse(f"{test_user} <--- user \n {user.get('username')} <--- db username \n {auth_token_hash} <--- the hashed auth token on the server")

    if get_db_field_from_auth(request, "username") is None:
        return render(request,"xxx_game/index.html")

    response = render(request,"xxx_game/index.html", {"username" : get_db_field_from_auth(request, "username")})
    return response

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

    # If the password, salted and hashed, matches the hashed password in the DB, set the auth_token cookie and store its hash in the DB
    if bcrypt.hashpw(password.encode(), user["salt"]) == user["hash"]:

        auth_token = str(uuid.uuid4())
        auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt)

        # Find user and set a new auth token
        user_collection.update_one({"username" : username}, {"$set" : {"auth_token_hash" : auth_token_hash}})

        # response = render(request,"xxx_game/index.html", {"username" : username})
        response = redirect("/", {"username" : username})
        response.set_cookie("auth_token", auth_token, max_age=60*60*24, httponly=True)
        return response

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
    
    auth_token = str(uuid.uuid4())
    auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt)

    user = {"username" : username, "salt" : salt, "hash" : hash, "auth_token_hash" : auth_token_hash}

    user_collection.insert_one(user)

    # response = render(request,"xxx_game/index.html", {"username" : username})
    response = redirect("/", {"username" : username})
    response.set_cookie("auth_token", auth_token, max_age=60*60*24, httponly=True)
    return response

# Logout route
def logout(request):
    auth_token = request.COOKIES.get('auth_token')
    if auth_token is None: # User is not logged in to begin with
        return render(request,"xxx_game/index.html")
    # Hash token and check for it in the database
    auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt) # Hash the unhashed cookie auth token so we can check for it in the DB
    user_collection.update_one({ "auth_token_hash": auth_token_hash}, {"$unset": {"auth_token_hash": ""}}) # Delete auth token field from DB
    return redirect("/")