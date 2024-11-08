function init(){
    add_avatar_event();

    create_game_close_btn = document.getElementsByClassName("create-game-close")[0];
    create_game_close_btn.addEventListener("click", function(){
        document.getElementsByClassName("create-game")[0].style.display = "none";
    });
}

function show_create_game(){
    document.getElementsByClassName("create-game")[0].style.display = "flex";
}

function generate_random_join_code(){
    document.getElementById("join-code").value = Math.random().toString(36).substring(2, 8);
}