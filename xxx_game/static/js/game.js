function init(){
    add_avatar_event();

    update_game_chat();
    setInterval(show_info, 1000);
    setInterval(update_game_chat,1000);
}

old_chat_text = "";
function update_game_chat(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;

    xhr.open("GET", "/game_chat_list/"+game_id, true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){

            let chat = document.getElementById("chat-box");
            if(old_chat_text != xhr.responseText){
                chat.innerHTML = "";
                JSON.parse(xhr.responseText).forEach(function(item){
                    chat.innerHTML += "<div>"+item["username"]+": "+item["message"]+"</div>";
                });
                old_chat_text = xhr.responseText;
            }
        }
    }
    xhr.send();
}

function leave_game(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;
    path = "/leave_game/"+game_id;

    xhr.open("GET", path , true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            result = JSON.parse(xhr.responseText);
            if(result['code'] == 0){
                window.location.href = "/game_lobby";
            }else if(result['code'] == 100){
                window.location.href = "/index";
            }else if(result['code'] == 101){
                window.location.href = "/game_lobby";
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