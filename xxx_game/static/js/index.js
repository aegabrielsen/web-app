function init(){
    add_avatar_event();

    btn = document.getElementsByClassName("chat-button")[0];
    console.log(btn);
    btn.onclick = function(){
        window.location.href = "/game_lobby";
    }
}

