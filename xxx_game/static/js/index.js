function init(){
    menu_button = document.getElementById("menu-button");
    menu_button.onclick = function(){
        menu = document.getElementById("menu");
        menu.style.display = "block";
        menu_button.style.display = "none";
    };
    menu = document.getElementById("menu");
    menu.onclick = function(){
        menu.style.display = "none";
        menu_button.style.display = "block";
    };
}

