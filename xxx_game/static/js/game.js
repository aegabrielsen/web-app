function init(){
    add_avatar_event();
    chat_btn = document.getElementById("go-chat")
    chat_btn.onclick = function(){
        window.location.href = "/chat";
    }

    // update_post()
    setInterval(show_info, 1000);
    // update_players()
    // setInterval(update_players,1000);
    // setInterval(update_game_chat,1000);
    // setInterval(update_post,1000);
}


// old_chat_text = "";
// function update_game_chat(){
//     let xhr = new XMLHttpRequest();
//     game_id = document.getElementById("game-id").value;

//     xhr.open("GET", "/game_chat_list/"+game_id, true);
//     xhr.onreadystatechange = function(){
//         if(xhr.readyState == 4 && xhr.status == 200){

//             let chat = document.getElementById("chat-box");
//             if(old_chat_text != xhr.responseText){
//                 chat.innerHTML = "";
//                 JSON.parse(xhr.responseText).forEach(function(item){
//                     chat.innerHTML += "<div>"+item["username"]+": "+item["message"]+"</div>";
//                 });
//                 old_chat_text = xhr.responseText;
//             }
//         }
//     }
//     xhr.send();
// }

function leave_game(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;
    console.log(game_id,document.getElementById("game-id").value);

    path = "/leave_game/";

    xhr.open("GET", path , true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            result = JSON.parse(xhr.responseText);
            if(result['code'] == 0){
                window.location.href = "/";
            }else if(result['code'] == 100){
                window.location.href = "/";
            }else if(result['code'] == 101){
                window.location.href = "/";
            }else if(result['code'] == 102){
                // window.location.href = "/game/"+game_id;
            }
        }
    }
    xhr.send();
}

function finish_game(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;
    path = "/finish_game/"+game_id;

    xhr.open("GET", path , true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            window.location.reload();
        }
    }
    xhr.send();
}

function send_post(){
    let xhr = new XMLHttpRequest();
    let content = document.getElementById("chatInput").value;
    let feeling = document.getElementById("feeling").value;

    csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    xhr.open("POST", "/game_chat", true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", csrf_token);

    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            document.getElementById("chatInput").value = "";
            document.getElementById("feeling").value = "";
        }
    }
    xhr.send(JSON.stringify({"content":content, "feeling":feeling}));
}

old_chat_text = "";
function update_post(){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/chat_list", true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){

            let chat = document.getElementById("chat-box");
            if(old_chat_text != xhr.responseText){
                chat.innerHTML = "";
                JSON.parse(xhr.responseText).forEach(function(item){
                    chat.innerHTML += 
                    `<div class="post">
                        <div class="message">
                            <p>User:${item.username}</p>
                            <p>${item.content}</p>
                            <p>Emotion:${item.feeling}</p>
                            <p>Likes: ${item.likes.length}</p>
                        </div>
                        <div class="like-button">
                            <button type="button" onclick="like_post('${'/like_post/'+item.post_id}')">Like</button>
                        </div>
                    </div>`;
                });
                old_chat_text = xhr.responseText;
            }
        }
    }
    xhr.send();
}

function like_post(path){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", path, true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            // update_post();
        }
    }
    xhr.send();
}

old_player_text = "";
function update_players(){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/get_players", true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            if (old_player_text != xhr.responseText){
                let players = document.getElementById("players");
                players.innerHTML = "";
                JSON.parse(xhr.responseText).forEach(function(item){
                    players.innerHTML += "<p><img src='/static/"+item['avatar']+"' class='avatar-small'>"+item['username']+"</p>"; 
                    // class='player'><label>"+player['username']+"</label><img src='/static/"+player['avatar']+"'></div>";
                    // "<p><img src="{% static avatar_url %}" class="avatar-small"> Player1</p>
                });
                old_player_text = xhr.responseText;
            }
        }
    }
    xhr.send();
}