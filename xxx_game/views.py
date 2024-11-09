from django.http import HttpResponse
from django.shortcuts import render, redirect
import os
import project1.settings as settings
from django.http import FileResponse,JsonResponse
from django import forms
import html #HTML ESCAPE
from pymongo import MongoClient
import bcrypt
import uuid
import filetype
import random
import string
mongo_client = MongoClient("mongo")
from bson.objectid import ObjectId
from django.shortcuts import redirect

# databases
db = mongo_client["webapp"]
user_collection = db["users"]
game_collection = db["games"]
game_post_collection = db["game_posts"]


global_salt = b'$2b$12$ldSsU24BK6EPANRbUpvXRu'

def get_user_from_auth(request):
    # Pass request into this function and it will attempt to retrieve a user from the auth_token cookie.
    # If no auth_token exists or if the search turns up empty, returns None.
    # Can be used anywhere like this: user = get_user_from_auth(request).
    # Can then get fields from it like this: user.get('username')
    # Make sure to do a None check in case either the user isn't logged in or the auth token isn't in the database.
    # Check the index function to see an example of how to use this.
    auth_token = request.COOKIES.get("auth_token")
    if auth_token is None:
        return None

    auth_token = request.COOKIES.get("auth_token")
    auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt)

    user = user_collection.find_one({"auth_token_hash" : auth_token_hash})
    if user is None:
        return None
    return user

# Create your views here.
def index(request):
    user = get_user_from_auth(request)
    posts = list(db['posts'].find())


    context = { 
        "username":user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
        'avatar_url': user.get('avatar') if user and user.get('avatar') else 'avatar/default.png',
    }
    
    response = render(request,"xxx_game/index.html", context=context)
    return response

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
        response = redirect("index")
        response.set_cookie("alert-info", "login failed")
        return response
    
    user = user_collection.find_one({"username" : username})

    # If the password, salted and hashed, matches the hashed password in the DB, set the auth_token cookie and store its hash in the DB
    if bcrypt.hashpw(password.encode(), user["salt"]) == user["hash"]:

        auth_token = str(uuid.uuid4())
        auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt)

        # Find user and set a new auth token
        user_collection.update_one({"username" : username}, {"$set" : {"auth_token_hash" : auth_token_hash}})

        response = redirect("/", {"username" : username})
        response.set_cookie("auth_token", auth_token, max_age=60*60*24, httponly=True)

        response.set_cookie("alert-info", "login success")
        return response

    response = redirect("index")
    response.set_cookie("alert-info", "login failed")
    return response
# This gets the registration form request
def register(request):

    # Get form fields
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    retype_password = request.POST.get("retype_password", None)
    
    # If the passwords do not match, do nothing
    if password != retype_password:
        response = redirect("index")
        response.set_cookie("alert-info", "Passwords do not match")
        return response

    # If the user is already registered, do nothing
    if user_collection.count_documents({"username" : username}) != 0:
        response = redirect("index")
        response.set_cookie("alert-info", "User already exists")
        return response

    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode(), salt)
    
    user = {"username" : username, "salt" : salt, "hash" : hash}

    user_collection.insert_one(user)

    response = redirect("/", {"username" : 'Guest'})
    response.set_cookie("alert-info", "register success")
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

#createpost
## function to create post object
def create_post(request):
    user = get_user_from_auth(request)

    content = request.POST.get('content')    
    escaped_content = escape_HTML(content)
    feeling = request.POST.get('feeling')
    if user:
        post = { 
        'username': user['username'],
        'content':escaped_content,
        'feeling': feeling,
        'likes': []
       
     }
    if not user:
        post = { 
        'username': "Guest",
        'content':content,
        'feeling': feeling,
        'likes': []
     }
    
    db['posts'].insert_one(post)
    return redirect ("/chat")
    
def chat(request):
    user = get_user_from_auth(request)
    if not user:
        response = redirect('/')
        
    posts = list(db['posts'].find())
    for post in posts:
        post['post_id'] = str(post['_id'])


    context = { 
        'posts':posts
    }
    return render(request, 'xxx_game/chat.html',context)

def escape_HTML(message):
    return message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def like_posts(request,post_id):
    user = get_user_from_auth(request)
    if user is None: 
        return redirect('/chat')
    
    post = db['posts'].find_one({'_id': ObjectId(post_id)})
    if not post:
        return redirect("/chat")
    if user['username'] not in post.get('likes', []):
        db['posts'].update_one(
            {'_id': ObjectId(post_id)},
            {'$push':{'likes': user['username']}}
        )
        return redirect ('/chat')
    db['posts'].update_one(
        {'_id':ObjectId(post_id)},
        {'$pull':{'likes': user['username']}}
    )
    return redirect('/chat')

# path /game_lobby
def game_lobby(request):
    user = get_user_from_auth(request)

    context = { 
        "username":user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
        'avatar_url': user.get('avatar') if user and user.get('avatar') else 'avatar/default.png',
    }

    return render(request, 'xxx_game/game_lobby.html',context)   

# path /game_room/<game_id>
def game_room(request,id):
    user = get_user_from_auth(request)

    import logging
    logging.warning('id'+id)

    game = game_collection.find_one({'_id': ObjectId(id)})
    if game is None:
        return redirect('game_lobby')
    
    if game['status'] != 'waiting':
        response = redirect('game_lobby')
        response.set_cookie('alert-info', 'Game already started')
        return response

    context = { 
        "username":user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
        'avatar_url': user.get('avatar') if user and user.get('avatar') else 'avatar/default.png',
        'game_name': game['name'],
        'join_code': game['join-code'],
        'game_id': str(game['_id'])
    }

    return render(request, 'xxx_game/game_room.html',context)

# path /game
def game(request,id):
    user = get_user_from_auth(request)
    context = { 
        "username":user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
        'avatar_url': user.get('avatar') if user and user.get('avatar') else 'avatar/default.png',
    }

    game = game_collection.find_one({'_id': ObjectId(id)})
    if game is None:
        response = redirect('game_lobby')
        response.set_cookie('alert-info', 'Game not found')
        return response

    game['status'] = 'playing'
    game_collection.update_one({'_id': ObjectId(id)}, {'$set': {'status': 'playing'}})

    context['game_id'] = str(game['_id'])

    return render(request, 'xxx_game/game.html',context)

# path /upload-avatar
def upload_avatar(request):
    user = get_user_from_auth(request)
    
    # only logged in users can upload avatars
    if user is None:
        return redirect('index')

    content = {
        "username": user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
    }
    
    if request.method == 'POST':
        form = forms.Form(request.POST, request.FILES)


        if form.is_valid():
            file = request.FILES['avatar']

            # create the avatar directory if it doesn't exist
            os.makedirs('xxx_game/static/avatar', exist_ok=True)
            file_data = file.read()

            # guess the file type
            file_type = filetype.guess(file_data)

            if file_type is None:
                # if the file type cannot be guessed, return to the index
                return redirect('index')
            
            elif file_type.MIME == 'image/jpeg' or file_type.MIME == 'image/png':
                # save the file, avatar name : avatar_<username>_<random_end>.<file_extension>

                rand_end = ''.join(random.choice(string.ascii_letters) for _ in range(10))
                file_name = 'avatar_'+user['username'] +'_'+ rand_end + '.' + file_type.extension
                file_path = os.path.join('xxx_game/static/avatar', file_name)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                user_collection.update_one({'_id': user['_id']}, {'$set': {'avatar': os.path.join('avatar', file_name)}})

            return redirect('index')
    return redirect('index')

# path /create_game
def create_game(request):
    user = get_user_from_auth(request)
    if user is None:
        return redirect('index')
    
    name = request.POST.get('name', None)
    join_code = request.POST.get('join_code', None)
    is_public = request.POST.get('is_public', None)

    # join code must be unique
    if game_collection.count_documents({'join-code': join_code}) != 0:
        response = redirect('game_lobby')
        response.set_cookie('alert-info', 'Join code already exists')
        return response
    
    # game name must be unique
    if game_collection.count_documents({'name': name}) != 0:
        response = redirect('game_lobby')
        response.set_cookie('alert-info', 'Game name already exists')
        return response
    
    import logging
    logging.warning('public'+is_public)
    logging.warning('name'+name)
    logging.warning('join_code' + join_code)

    game = {
        'created_by': user['username'],
        'players': [user['username']],
        'status': 'waiting', # waiting, playing, finished
        'name': name,
        'join-code': join_code,
        'is_public': is_public
    }
    game_collection.insert_one(game)

    response = redirect('game_lobby')
    response.set_cookie('alert-info', 'Game created')
    return response

# path /games
def get_game(request):
    user = get_user_from_auth(request)

    game_list = list(game_collection.find({'is_public': 'true'}))

    game_list = [{'name': game['name'], 'join_code': game['join-code'],'id':str(game['_id'])} for game in game_list]
    response = JsonResponse(game_list, safe=False)
    return response

# path /players/<game_id>
def get_game_player(request,id):
    user = get_user_from_auth(request)
    game = game_collection.find_one({'_id': ObjectId(id)})
    if game is None:
        return redirect('game_lobby')
    
    players = game['players']
    player_list = []
    for player in players:
        player = user_collection.find_one({'username': player})
        player_list.append({'avatar':player.get('avatar') if player.get('avatar') else 'avatar/default.png', 'username': player['username']})

    response = JsonResponse(player_list, safe=False)
    return response

# path /game_chat
def game_chat(request):
    user = get_user_from_auth(request)

    if not user:
        response = redirect('/')
        
    posts = list(db['game_posts'].find())
    for post in posts:
        post['post_id'] = str(post['_id'])

    if request.POST.get('message') is None:
        return JsonResponse({'status': 'no message'})
    
    if request.POST.get('message') == '':
        return JsonResponse({'status': 'empty message'})
    
    message = escape_HTML(request.POST.get('message'))

    post = {
        'game_id': request.POST.get('game_id'),
        'username': user['username'],
        'message': message,
    }    

    game_post_collection.insert_one(post)

    return redirect('/game/'+request.POST.get('game_id'))

# path /game_chat_list/<game_id>
def game_chat_list(request,id):
    user = get_user_from_auth(request)
    if not user:
        response = redirect('/')
    
    posts = game_post_collection.find({'game_id': id})
    posts = list(posts)
    import logging
    logging.warning('post'+str(list(posts)))
    for post in posts:
        post['_id'] = str(post['_id'])
    
    
    return JsonResponse(posts,safe=False)