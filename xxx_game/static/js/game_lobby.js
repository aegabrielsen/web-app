function init(){
    add_avatar_event();

    create_game_close_btn = document.getElementsByClassName("create-game-close")[0];
    create_game_close_btn.addEventListener("click", function(){
        document.getElementsByClassName("create-game")[0].style.display = "none";
    });

    
    show_info()
    
    update_games();
    setInterval(update_games,1000);

}

function show_create_game(){
    document.getElementsByClassName("create-game")[0].style.display = "flex";
}

function generate_random_join_code(){
    document.getElementById("join-code").value = Math.random().toString(36).substring(2, 8);
}

function update_games(){
    let xhr = new XMLHttpRequest();
    xhr.open("GET", "/games", true);
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4 && xhr.status == 200){

            document.getElementById("game-list").innerHTML = "";

            JSON.parse(xhr.responseText).forEach(game => {
                let game_div = document.createElement("div");
                game_div.className = "game-item";
                game_div.onclick = function(){
                    window.location.href = "/game_room/" + game["id"];
                };

                game_div.innerHTML = `
                <label>${game["name"]}</label>
                <img src="static/images/start.png">
                `;
                document.getElementById("game-list").appendChild(game_div);
                });
        }
    }
    xhr.send();
}