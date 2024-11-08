function add_avatar_event(){

    avatar_box = document.getElementsByClassName("upload-avatar")[0];

    // default: hide
    avatar_box.style.display = "none";

    avatar = document.getElementsByClassName("avatar")[0];
    avatar.addEventListener("click", function(){
        avatar_box.style.display = "flex";
    });

    btn = document.getElementsByClassName("upload-avatar-close")[0];
    btn.addEventListener("click", function(){
        avatar_box.style.display = "none";
    });
}