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
