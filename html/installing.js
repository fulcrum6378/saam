// Created by Mahdi Parastesh, February and March 2021
// Facebook: https://www.facebook.com/mpg973
// All rights reserved.

update();
setInterval(function() { update(); }, 5000);
function set_progress(data) {
    let percent = "0%";
    if (parseInt(data) != NaN) percent = parseInt(data) + "%";
    $("#installation_progress div")
        .css("display", "block")
        .animate({width: percent})
        .text(percent)
        .attr("aria-valuenow", percent.substring(0, percent.length - 1));
}
function update() {
    $.ajax({
        url: "/query?q=install_progress",
        context: document.body,
        timeout: 4900
    }).done(function(data) {
        if (data == "None") location.reload();
        set_progress(data);
    })
}
