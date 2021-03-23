// Created by Mahdi Parastesh, February and March 2021
// Github: https://github.com/fulcrum1378
// All rights reserved.

// Initial Animations
var all = $("#main p");
for (i = 0; i < all.length; i++) {
    let dist = parseInt($(window).innerWidth() / 7);
    $(all[i])
        .css("margin-right", dist + "px")
        .animate({opacity: 1, marginRight: 0}, dist + (60 * i));
}
function branch(i) {
    location.assign(location.href + "branch?i=" + i);
}


// Floating Menu
function updateAll() {
    $.ajax({
        url: "/action?q=update_all",
        context: document.body,
        timeout: 60 * 60000  // 1 hour
    }).done(function(data) {
        switch (data) {
            case "already":
                alert("شما قبلا این دستور را داده اید و هنوز تمام نشده است...");
                break;
            case "saved":
                alert("دستوری که دادید بزودی انجام داده خواهد شد!");
                break;
            default:
                alert(data);
        }
    });
}
function reset() {
    if (!confirm("آیا از این کار مطمئن هستید؟")) return;
    $.ajax({
        url: "/action?q=reset",
        context: document.body,
        timeout: 10000
    }).done(function(data) {
        if (data == "done")
            location.reload();
        else alert(data);
    });
}
var onOff = (request, status, error) => { location.reload(); }
function shutdown() {
    $.ajax({
        url: "/action?q=shutdown",
        context: document.body,
        timeout: 10000,
        error: onOff
    })
}
function search() {
    location.assign(location.href + "search");
}
