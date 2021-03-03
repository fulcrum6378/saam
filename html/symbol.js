// Initial Animations
var all = $("#main > div.symbol");
for (i = 0; i < all.length; i++) {
    let dist = parseInt($(window).innerWidth() / 7);
    $(all[i])
        .css("margin-right", dist + "px")
        .animate({opacity: 1, marginRight: 0}, dist + (60 * i));
}

// Checkboxes
$(".chk_sym").click(function(e) {
    let t = $(this)[0];
    if (t.indeterminate) {
        t.checked = false; // will become true immediately.
        return false;
    }
    else e.stopPropagation();
});
$(".chk_sym ~ label").click(function(e) {
    let t = $(this).prev()[0];
    if (t.indeterminate) t.checked = true;
    else t.checked = !t.checked;
    return false;
});




function symbol_toggle(that) {
    if (that.css("display") == "block") that.slideUp(200);
    else that.slideDown(200);
}
function tfClick(v, sym) {
    let cal = new SolarHijri(new Date()), def = dateModel(cal) +" - "+ dateModel(cal);
    let board = prompt("لطفا بازه زمانی موردنظر را انتخاب کنید...", def);
    if (board == null || board == "") return;
    $.ajax({
        url: "/action?q=analyze&a1=" + sym + "&a2=" + v + "&a3=" + board,
        context: document.body,
        timeout: 10 * 60 * 60000 // 10 hours
    }).done(function(data) {
        alert(data);
    });
}
function z(d) {
    if (d < 10) return "0" + d; else return d;
}
function dateModel(cal) {
    let s = CONFIG.dateSeparator, t = CONFIG.timeSeparator;
    return cal.Y+s+z(cal.M+1)+s+z(cal.D)+s+z(cal.H)+t+z(cal.I);
}
