$("input[type='checkbox']").click(function(e) {
    cbChange($(this));
    return false;
});
$("label").click(function(e) {
    cbChange($(this).children().first().children().first());
    return false;
});
function cbChange(cb) {
    if (!confirm("آیا از این تغییر مطمئن هستید؟ این تغییر ممکن است باعث به هم ریختن دیتابیس شود.")) return;
    $.ajax({
        url: "/action?q=change_timeframe&a1=" + cb.attr("id").split("_")[1],
        context: document.body,
        timeout: 5000
    }).done(function(data) {
        if (data == "True") cb[0].checked = true;
        if (data == "False") cb[0].checked = false;
    });
}
