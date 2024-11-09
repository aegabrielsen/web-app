function init(){
    add_avatar_event();

    update_game_chat();
    setInterval(update_game_chat,1000);
}

function update_game_chat(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;

    xhr.open("GET", "/game_chat_list/"+game_id, true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            
            let chat = document.getElementById("chat-box");
            chat.innerHTML = "";
            JSON.parse(xhr.responseText).forEach(function(item){
                chat.innerHTML += "<div>"+item["username"]+": "+item["message"]+"</div>";
            });
        }
    }
    xhr.send();
}