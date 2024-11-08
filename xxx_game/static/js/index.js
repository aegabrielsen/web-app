function init(){
    add_avatar_event();

    btn = document.getElementsByClassName("chat-button")[0];
    btn.onclick = function(){
        window.location.href = "/game_lobby";
    }

    setInterval(() => {
        show_info();
    }, 1000);
    
}

