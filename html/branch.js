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
function search() {
    location.assign(location.href + "search");
}
