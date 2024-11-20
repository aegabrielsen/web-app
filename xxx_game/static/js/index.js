function init(){
    add_avatar_event();

    btn = document.getElementsByClassName("chat-button")[0];
    btn.onclick = function(){
        username_h1 = document.getElementById("username-h1").innerText;
        if (username_h1 == "Welcome, Guest"){
            alert("Please login first!");
            return;
        }
        window.location.href = "/game/";
    }

    chat_btn = document.getElementById("go-chat")
    chat_btn.onclick = function(){
        window.location.href = "/chat";
    }

    setInterval(() => {
        show_info
    }, 1000);

    startWebsocket()
}

function startWebsocket(){
    socket = new WebSocket('ws://' + window.location.host + '/websocket')
    
    socket.onmessage = function(ws_message) {
        const message = JSON.parse(ws_message.data);
    }
}