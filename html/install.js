// Created by Mahdi Parastesh, Winter 2021
// Github: https://github.com/fulcrum1378
// All rights reserved.

$("#installer").fadeOut(1, function() { $(this).removeClass("invisible"); });
$("#installer").fadeIn(600);
$("#start").click(function() { classify(); });
function classify() {
    $.ajax({
        url: "/action?q=classify",
        context: document.body,
        timeout: 5000
    }).done(function(data) {
        if (data != "started") alert("FAILED: " + data);
    });
    $("#loading").slideUp(200);
    $("#installation_progress").fadeOut(1, function() { $(this).removeClass("invisible"); });
    $("#installation_progress").fadeIn(500);
    update();
    setInterval(function() { update(); }, 5000);
}
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
