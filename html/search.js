function goTo(branchId, symId) {
    let adr = location.href;
    adr = adr.substring(0, adr.indexOf("search"));
    adr += "branch?i=" + branchId + "&found=" + symId;
    location.assign(adr);
}
$("#search").on('input propertychange', () => {
    let all = $("#main").children();
    for (i = 0; i < all.length; i++)
        all.eq(i).css("display", all.eq(i).text().includes($("#search").val()) ? "block" : "none");
});
