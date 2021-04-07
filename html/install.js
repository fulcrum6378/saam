// Created by Mahdi Parastesh, Winter 2021
// Github: https://github.com/fulcrum1378
// All rights reserved.

$("#installer").fadeOut(1, function() { $(this).removeClass("invisible"); });
$("#installer").fadeIn(600);
$("#start").click(function() { classify(); });
function classify() {
    $("#installer :nth-child(1)").slideUp(200);
    $("#installer :nth-child(2)").slideUp(200);
    $("#start").fadeOut(200, function() { $(this).remove(); });
    $.ajax({
        url: "/action?q=classify",
        context: document.body,
        timeout: 5000
    }).done(function(data) {
        if (data != "started") alert("FAILED: " + data);
    });
    $("#installation_progress").fadeOut(1, function() { $(this).removeClass("invisible"); });
    $("#installation_progress").fadeIn(500);
    update_install();
    setInterval(function() { update_install(); }, 5000);
}
