// Created by Mahdi Parastesh, February and March 2021
// Github: https://github.com/fulcrum1378
// All rights reserved.

$("#search").on('input propertychange', () => {
    let all = $("#main").children();
    for (i = 0; i < all.length; i++)
        all.eq(i).css("display", all.eq(i).text().includes($("#search").val()) ? "block" : "none");
});
