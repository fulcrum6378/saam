$("td").click(function() {
    let input = document.body.appendChild(document.createElement("input"));
    input.value = $(this).text();
    input.focus();
    input.select();
    document.execCommand('copy');
    input.parentNode.removeChild(input);

    if ($(this).hasClass("copied")) $(this).removeClass("copied");
    $(this).attr("title", "کپی شد!");
    let tt = new bootstrap.Tooltip(this, { boundary: 'window' });
    $(this).addClass("copied");
    $(this).tooltip('show');
    setTimeout(() => {
        $(this).removeClass("copied");
        $(this).tooltip("hide");
        $(this).removeAttr("title");
    }, 1000);
});

// Deletion
function z(d) {
    if (d < 10) return "0" + d; else return d;
}
function dateModel(cal) {
    let s = $("#dateSeparator").val(), t = $("#timeSeparator").val();
    return cal.Y+s+z(cal.M+1)+s+z(cal.D)+s+z(cal.H)+t+z(cal.I);
}
function omit() {
    let cal = new SolarHijri(new Date()), def = dateModel(cal) +" - "+ dateModel(cal);
    let board = prompt("لطفا بازه زمانی موردنظر را انتخاب کنید...", def);
    if (board == null || board == "") return;
    $.ajax({
        url: "/action?q=delete&a1=",
        context: document.body,
        timeout: 5000
    }).done(function(data) {
        //
    });
}
function truncate() {
    if (!confirm("آیا از خالی کردن تمام اطلاعات موجود برای تایم فریم " + 1 + " مطمئن هستید؟")) return;
    alert("");
    $.ajax({
        url: "/action?q=delete&a1=",
        context: document.body,
        timeout: 5000
    }).done(function(data) {
        //
    });
}
function destroy() {
    if (!confirm("آیا از خالی کردن تمام اطلاعات موجود برای نماد " + 1 + " مطمئن هستید؟")) return;
    alert("");
    $.ajax({
        url: "/action?q=delete&a1=",
        context: document.body,
        timeout: 5000
    }).done(function(data) {
        //
    });
}
