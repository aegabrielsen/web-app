function init(){
    add_avatar_event();
    document.getElementById("start-game-btn").addEventListener("click", function(){
        game_id = document.getElementById("game-id").value;
        window.location.href = "/game/"+game_id;
    });

    update_players();
    setInterval(update_players,1000);

}

function update_players(){
    let xhr = new XMLHttpRequest();
    game_id = document.getElementById("game-id").value;
    path = "/players/"+game_id;

    xhr.open("GET", path , true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){
            player_list = document.getElementById("player-list");
            player_list.ininerHTML = "";

            JSON.parse(xhr.responseText).forEach(player => {
                player_list.innerHTML += "<div class='player'><label>"+player['username']+"</label><img src='/static/"+player['avatar']+"'></div>";
            });
        }
    }
    xhr.send();
}