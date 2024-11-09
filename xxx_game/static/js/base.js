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

// get cookie by name
function getCookie(name) {
    // get cookie by name
    let cookieArr = document.cookie.split(";");
    for (let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if (name == cookiePair[0].trim()) {
            return cookiePair[1];
        }
    }
    return null;
}

// delete cookie by name
function deleteCookie(name) {
    document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

function show_info(){
    if(getCookie("alert-info")==null){
        return;
    }
    
    alert_info = getCookie("alert-info");
    alert(alert_info);
    // document.getElementById("show-info").style.display = "block";
    // document.getElementById("info-content").innerText = alert_info;
    // document.getElementById("info-close").addEventListener("click", function(){
    //     document.getElementById("show-info").style.display = "none";
    // });  

    deleteCookie("alert-info");
}
