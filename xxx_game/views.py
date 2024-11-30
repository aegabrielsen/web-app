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
import logging
from bson.objectid import ObjectId
from django.shortcuts import redirect
import json
import time
import threading

from datetime import timedelta
from django_ratelimit.decorators import ratelimit

# databases
mongo_client = MongoClient("mongo")
db = mongo_client["webapp"]
user_collection = db["users"]
game_collection = db["games"]
game_user_collection = db["game_users"]

# game_post_collection = db["game_posts"]

# guest_collection = db["guests"]

global_salt = b'$2b$12$ldSsU24BK6EPANRbUpvXRu'

blocked = set()

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

    return user

# Create your views here. ####

def block(ip):
    blocked.add(ip)
    time.sleep(30)
    blocked.remove(ip)

def ratelimited(request, error):
    ip = request.META['REMOTE_ADDR'] #### TODO maybe change this?
    threading.Thread(target=block, args=(ip,)).start()
    return render(request, 'xxx_game/429.html', status=429)

def is_blocked(request):
    if request.META['REMOTE_ADDR'] in blocked: #### TODO maybe change this?
        return True

@ratelimit(key='ip', rate='50/10s')
def index(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

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
@ratelimit(key='ip', rate='50/10s')
def login(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

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
        if request.COOKIES.get('guest'):
            response.delete_cookie('guest')
        return response

    response = redirect("index")
    response.set_cookie("alert-info", "login failed")
    return response

# This gets the registration form request
@ratelimit(key='ip', rate='50/10s')
def register(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

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
@ratelimit(key='ip', rate='50/10s')
def logout(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    auth_token = request.COOKIES.get('auth_token')
    if auth_token is None: # User is not logged in to begin with
        return render(request,"xxx_game/index.html")
    # Hash token and check for it in the database
    auth_token_hash = bcrypt.hashpw(auth_token.encode(), global_salt) # Hash the unhashed cookie auth token so we can check for it in the DB
    user_collection.update_one({ "auth_token_hash": auth_token_hash}, {"$unset": {"auth_token_hash": ""}}) # Delete auth token field from DB
    response = redirect("/",{"username" : 'Guest'})
    response.delete_cookie("auth_token") # Delete the cookie
    return response

#createpost
## function to create post object
@ratelimit(key='ip', rate='50/10s')
def create_post(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    user = get_user_from_auth(request)

    content = request.POST.get('content')
    # When replacing the Django template, a function similar to escape_html will be used for its value, so there is no need to use ? ???  
    # escaped_content = escape_HTML(content)
    escaped_content = content
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
        'content':escaped_content,
        'feeling': feeling,
        'likes': []
     }
    
    db['posts'].insert_one(post)
    # return HttpResponse("Successful chat")
    return redirect ("/chat")

@ratelimit(key='ip', rate='50/10s')
def chat_list(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    user = get_user_from_auth(request)
  
    posts = list(db['posts'].find())
    for post in posts:
        post['_id'] = str(post['_id'])
        post['post_id'] = post['_id']

    return JsonResponse(posts,safe=False)

def like_posts_ajax(request,post_id):
    user = get_user_from_auth(request)
    if user is None:
        response = JsonResponse({'code':100,'status': 'not logged in'})
        response.set_cookie('alert-info', 'You are not logged in')
        return response
    
    post = db['posts'].find_one({'_id': ObjectId(post_id)})
    if not post:
        response = JsonResponse({'code':101,'status': 'post not found'})
        response.set_cookie('alert-info', 'Post not found')
        return response

    if user['username'] not in post.get('likes', []):
        db['posts'].update_one(
            {'_id': ObjectId(post_id)},
            {'$push':{'likes': user['username']}}
        )
        return JsonResponse({'code':0,'status': 'success'})
    
    db['posts'].update_one(
        {'_id':ObjectId(post_id)},
        {'$pull':{'likes': user['username']}}
    )
    return JsonResponse({'code':0,'status': 'success'})

@ratelimit(key='ip', rate='50/10s')
def chat(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    user = get_user_from_auth(request)
    if user:
        username = user.get('username')
    else:
        username = "Guest"
        
    posts = list(db['posts'].find())
    for post in posts:
        post['post_id'] = str(post['_id'])


    context = { 
        'posts':posts,
        'username':username
    }
    return render(request, 'xxx_game/chat.html',context)

def escape_HTML(message):
    return message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

@ratelimit(key='ip', rate='50/10s')
def like_posts(request,post_id):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

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
# url

def game_lobby(request):
    user = get_user_from_auth(request)
    create_guest_id = False

    context = { 
        "username":user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
        'avatar_url': user.get('avatar') if user and user.get('avatar') else 'avatar/default.png',
    }
    logging.warning('user:'+str(user))

    if user is None:
        guest_id = generate_guest_id()
        create_guest_id = True
        
    # if user is not None:
    #     # check if user is already in a game, if so, redirect to the game room
    #     user_game = game_user_collection.find_one({'username': user['username']})
    #     if user_game is not None:
    #         game = game_collection.find_one({'_id': ObjectId(user_game['game_id'])})
    #         if game is not None:
    #             return redirect('game_room/'+str(game['_id']))
    # else:
    #     guest_id = request.COOKIES.get('guest')
        
    #     if guest_id is None:
    #         guest_id = generate_guest_id()
    #         create_guest_id = True

    #     user_game = game_user_collection.find_one({'guest_id': guest_id})
    #     logging.warning(user_game)
    #     if user_game is not None:
    #         game = game_collection.find_one({'_id': ObjectId(user_game['game_id'])})
    #         if game is not None:
    #             return redirect('game_room/'+str(game['_id']))
            
    response = render(request, 'xxx_game/game_lobby.html',context)
    if create_guest_id:
        response.set_cookie('guest', guest_id)
    return response

def generate_guest_id():
    guest_id = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    guest_id = 'guest_'+guest_id
    return guest_id

# path /game_room/<game_id> 
# User join the game, and one user can only join one game at a time.
def game_room(request,id):
    user = get_user_from_auth(request)
    if user is None:
        guest = request.COOKIES.get('guest',generate_guest_id())


    game = game_collection.find_one({'_id': ObjectId(id)})
    if game is None:
        return redirect('game_lobby')
    
        # if user is not None:
        #     game_user_collection.delete_one({'username': user['username']})
        #     return redirect('game_lobby')
        # else:
        #     game_user_collection.delete_one({'guest_id': guest})
        #     return redirect('game_lobby')

    # if user is not None:
    #     game_user = game_user_collection.find_one({'game_id':id, 'username': user['username']})
    # else:
    #     game_user = game_user_collection.find_one({'game_id':id, 'guest_id': guest})

    # if game_user is not None and ( game['status'] == 'playing' or game['status'] == 'finished'):
    #     # user is already in the game, redirect to the game
    #     return redirect('/game/'+str(game['_id']))

    # if game['status'] != 'waiting':
    #     response = redirect('game_lobby')
    #     response.set_cookie('alert-info', 'Game already started')
    #     return response
    
    if user and user['username'] not in game['players']:
        # add user to the game
        game['players'].append(user['username'])
        game_collection.update_one({'_id': ObjectId(id)}, {'$set': {'players': game['players']}})
    
    if user is None and guest not in game['players']:
        # add guest to the game
        game['players'].append(guest)
        game_collection.update_one({'_id': ObjectId(id)}, {'$set': {'players': game['players']}})

    # if user and game_user_collection.find_one({'username': user['username']}) is None:
    #     # add user to the game_user collection
    #     game_user_collection.insert_one({'game_id': id, 'username': user['username']})
    
    # if user is None and game_user_collection.find_one({'guest_id': guest}) is None:
    #     # add guest to the game_user collection
    #     game_user_collection.insert_one({'game_id': id, 'guest_id': guest})
    

    context = { 
        "username":user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
        'avatar_url': user.get('avatar') if user and user.get('avatar') else 'avatar/default.png',
        'game_name': game['name'],
        'join_code': game['join-code'],
        'game_id': str(game['_id'])
    }

    return render(request, 'xxx_game/game_room.html',context)

# path /join_game/
# to start game
@ratelimit(key='ip', rate='50/10s')
def game(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    user = get_user_from_auth(request)
    context = { 
        "username":user.get('username') if user else "Guest",
        "logged_in": user is not None, # used to determine if the user is logged in or not
        'avatar_url': user.get('avatar') if user and user.get('avatar') else 'avatar/default.png',
    }
    if user is not None and game_user_collection.count_documents({'username':user['username']}) == 0:
        game_user_collection.insert_one({'username': user['username']})

    # game = game_collection.find_one({'_id': ObjectId(id)})
    # if game is None:
    #     response = redirect('game_lobby')
    #     response.set_cookie('alert-info', 'Game not found')
    #     return response
    
    # if game['status'] == 'waiting':
    #     game['status'] = 'playing'
    #     game_collection.update_one({'_id': ObjectId(id)}, {'$set': {'status': 'playing'}})

    # context['game_id'] = str(game['_id'])

    return render(request, 'xxx_game/game.html',context)

# path /upload-avatar
@ratelimit(key='ip', rate='50/10s')
def upload_avatar(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    
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
# create new game. after creating the game, the user will be redirected to the game room
# ajax call;
def create_game(request):
    user = get_user_from_auth(request)
    if user is None:
        return redirect('index')
    
    name = escape_HTML(request.POST.get('name', None))
    join_code = escape_HTML(request.POST.get('join_code', None))
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

    game = {
        'created_by': user['username'],
        'players': [],
        'status': 'waiting', # waiting, playing, finished
        'name': name,
        'join-code': join_code,
        'is_public': is_public
    }
    game = game_collection.insert_one(game)


    response = redirect('game_lobby')
    response.set_cookie('alert-info', 'Game created')
    return response

# path /games
# ajax call to get all public games
def get_game(request):
    user = get_user_from_auth(request)

    game_list = list(game_collection.find({'is_public': 'true'}))
    game_list = [{'name': game['name'], 'join_code': game['join-code'],'id':str(game['_id'])} for game in game_list]
    response = JsonResponse(game_list, safe=False)
    return response

# path /get_players/
@ratelimit(key='ip', rate='50/10s')
def get_game_player(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    user = get_user_from_auth(request)
    # game = game_collection.find_one({'_id': ObjectId(id)})
    # if game is None:
    #     return redirect('game_lobby')
    
    players = game_user_collection.find({})
    player_list = []
    for player in players:
        player = user_collection.find_one({'username': player['username']})
        if player:
            player_list.append({'avatar':player.get('avatar') if player.get('avatar') else 'avatar/default.png', 'username': player['username']})
        else:
            player_list.append({'avatar':'avatar/default.png', 'username': 'Guest'})

    response = JsonResponse(player_list, safe=False)
    return response

# path /game_chat
def game_chat(request):
    user = get_user_from_auth(request)

    payload = json.loads(request.body)
    content = payload.get('content')    
    escaped_content = escape_HTML(content)
    feeling = payload.get('feeling')
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
        'content':escaped_content,
        'feeling': feeling,
        'likes': []
     }
    
    db['posts'].insert_one(post)
    return JsonResponse({'code':0,'status': 'success'})

# path /game_chat_list/<game_id>
def game_chat_list(request,id):
    user = get_user_from_auth(request)
    if not user:
        response = redirect('/')
    
    posts = game_post_collection.find({'game_id': id})
    posts = list(posts)
    for post in posts:
        post['_id'] = str(post['_id'])
    
    
    return JsonResponse(posts,safe=False)

# path /leave_game/<game_id>
# ajax call to leave the game
# code 0: success
# code 100: not logged in
# code 101: not in the game
# code 102: game already started
@ratelimit(key='ip', rate='50/10s')
def leave_game(request):

    if is_blocked(request):
        return render(request, 'xxx_game/429.html', status=429)

    user = get_user_from_auth(request)

    # if not user:
    #     response = JsonResponse({'code':100,'status': 'not logged in'})
    #     response.set_cookie('alert-info', 'You are not logged in')
    #     return response
    
    # game_user = game_user_collection.find_one({'game_id':id, 'username': user['username']})

    # if game_user is None:
    #     response = JsonResponse({'code':101,'status': 'not in the game'})
    #     response.set_cookie('alert-info', 'You are not in the game')
    #     return response

    # game = game_collection.find_one({'_id': ObjectId(id)})
    # if game is not None:
    #     # if game['status'] != 'waiting' and game['status'] != 'finished':
    #     #     response = JsonResponse({'code':102,'status': 'game already started'})
    #     #     response.set_cookie('alert-info', 'Game already started , only waiting and finished game can be left')
    #     #     return response
    #     if user is not None:
    #         if user['username'] in game['players']:
    #             game['players'].remove(user['username'])
    #             game_collection.update_one({'_id': ObjectId(id)}, {'$set': {'players': game['players']}})

    #     else:
    #         guest = request.COOKIES.get('guest',None)
    #         if guest is not None and guest in game['players']:
    #             game['players'].remove(guest)
    #             game_collection.update_one({'_id': ObjectId(id)}, {'$set': {'players': game['players']}})
    
    # game_user_collection.delete_one({'game_id': id, 'username': user['username']})

    if game_user_collection.count_documents({'username':user['username']}) > 0:
        game_user_collection.delete_one({'username':user['username']})

    response = JsonResponse({'code':0,'status': 'success'})
    return response

# path /finish_game/<game_id>
# def finish_game(request,id):
#     game = game_collection.find_one({'_id': ObjectId(id)})
#     if game is None:
        
#         response = redirect('game_lobby')
#         response.set_cookie('alert-info', 'Game not found')
#         return response

#     logging.warning('game'+str(game))
#     game['status'] = 'finished'
#     logging.warning(game_collection.update_one({'_id': ObjectId(id)}, {'$set': {'status': 'finished'}}))
#     logging.warning('game'+str(game_collection.find_one({'_id': ObjectId(id)})))

#     response = redirect('/game/'+str(game['_id']))
#     response.set_cookie('alert-info', 'Game finished')
#     return response

# path /join_game/<join_code>
def join_game(request,join_code):
    user = get_user_from_auth(request)

    # if not user:
    #     response = redirect('game_lobby')
    #     response.set_cookie('alert-info', 'You are not logged in')
    #     return response
    
    game = game_collection.find_one({'join-code': join_code})
    if game is None:
        logging.warning('game not found')
        response = JsonResponse({'code':100,'status': 'Game not found'})
        response.set_cookie('alert-info', 'Game not found')
        return response
    
    # if game['status'] != 'waiting':
    #     logging.warning('game already started')
    #     response = redirect('game_lobby')
    #     response.set_cookie('alert-info', 'Game already started')
    #     return response
    
    response = JsonResponse({'code':0,'status': 'success','game_id': str(game['_id'])})
    return response

# path /check_game_start/<game_id>
def check_game_start(request,id):
    game = game_collection.find_one({'_id': ObjectId(id)})
    if game is None:
        response = HttpResponse('Game not found')
        response.set_cookie('alert-info', 'Game not found')
        return response

    if game['status'] == 'playing':
        response = HttpResponse('True')
        return response

    response = HttpResponse('False')
    return response