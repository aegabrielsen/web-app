function init(){
    add_avatar_event();
    document.getElementById("start-game-btn").addEventListener("click", function(){
        game_id = document.getElementById("game-id").value;
        window.location.href = "/game/"+game_id;
    });

    chat_btn = document.getElementById("go-chat")
    chat_btn.onclick = function(){
        window.location.href = "/chat";
    }

    setInterval(show_info, 1000);
    update_players();
    setInterval(update_players,1000);
    setInterval(check_game_start,1000);

}

old_player_text = "";
function update_players(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;
    path = "/players/"+game_id;

    xhr.open("GET", path , true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            player_list = document.getElementById("player-list");
            if(old_player_text != xhr.responseText){
                player_list.innerHTML = "";
                JSON.parse(xhr.responseText).forEach(player => {
                    player_list.innerHTML += "<div class='player'><label>"+player['username']+"</label><img src='/static/"+player['avatar']+"'></div>";
                });
                old_player_text = xhr.responseText;
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
            window.location.href = "/game_lobby";
        }
    }
    xhr.send();
}

function check_game_start(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;
    path = "/check_game_start/"+game_id;

    xhr.open("GET", path , true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            if(xhr.responseText == "True"){
                window.location.href = "/game/"+game_id;
            }
        }
    }
    xhr.send();
}