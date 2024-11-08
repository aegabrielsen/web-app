function init(){
    add_avatar_event();
    document.getElementById("start-game-btn").addEventListener("click", function(){
        window.location.href = "/game";
    });
}