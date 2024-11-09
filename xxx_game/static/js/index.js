function init(){
    add_avatar_event();

    btn = document.getElementsByClassName("chat-button")[0];
    btn.onclick = function(){
        window.location.href = "/game_lobby";
    }

    chat_btn = document.getElementById("go-chat")
    chat_btn.onclick = function(){
        window.location.href = "/chat";
    }

    setInterval(() => {
        show_info();
    }, 1000);
    
}

