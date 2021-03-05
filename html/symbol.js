// Initial Animations
var all = $("#main > div.symbol");
for (i = 0; i < all.length; i++) {
    let dist = parseInt($(window).innerWidth() / 7);
    $(all[i])
        .css("margin-right", dist + "px")
        .animate({opacity: 1, marginRight: 0}, dist + (60 * i));
}

// Checkboxes
$(".indeterminate").prop("indeterminate", true);
$(".chk_sym").click(function(e) {
    let t = $(this)[0];
    if (t.indeterminate) {
        cbChange(t, false); // will become true immediately.
        return false;
    } else {
        e.stopPropagation();
        cbChange(t);
    }
});
$(".chk_sym ~ label").click(function(e) {
    let t = $(this).prev()[0];
    if (t.indeterminate) cbChange(t, true);
    else cbChange(t, !t.checked);
    return false;
});
function cbChange(t, b = t.checked) {
    t.checked = b;
    let tf = $(t).attr("data-frame");
    if (tf == undefined) tf = "-1";
    let boo = "0";
    if (b) boo = "1";
    $.ajax({
        url: "/action?q=check&a1=" + $(t).attr("data-symbol") + "&a2=" + tf + "&a3=" + boo,
        context: document.body,
        timeout: 5000
    }).done(function(data) {
        if (data == "not found") { alert(data); return; }
        if ($(t).attr("data-frame") === undefined)
            updateCheckboxes(data, t, $(t).parent().next());
        else
            updateCheckboxes(data, $(t).parent().parent().prev().children().first()[0], $(t).parent().parent());
    });
}
function updateCheckboxes(data, boss, overflow) {
    let binary = data.split("");
    if (data.indexOf("0") == -1) boss.checked = true;
    else if (data.indexOf("1") == -1) boss.checked = false;
    else boss.indeterminate = true;
    for (i = 0; i < overflow.children().length; i++)
        overflow.children().eq(i).children().first()[0].checked = binary[i] == "1";
}




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
