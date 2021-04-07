// Setup
$.ajaxSetup({ cache: false });

// Installation
function set_progress(data) {
    let percent = "0%";
    if (parseInt(data) != NaN) percent = parseInt(data) + "%";
    $("#installation_progress div")
        .css("display", "block")
        .animate({width: percent})
        .text(percent)
        .attr("aria-valuenow", percent.substring(0, percent.length - 1));
}
function update_install() {
    $.ajax({
        url: "/query?q=install_progress",
        context: document.body,
        timeout: 4900
    }).done(function(data) {
        if (data == "None") location.reload();
        set_progress(data);
    })
}

// Date & Time
function z(d) {
    if (d < 10) return "0" + d; else return d;
}
function dateModel(cal) {
    let s = $("#dateSeparator").val(), t = $("#timeSeparator").val();
    return cal.Y+s+z(cal.M+1)+s+z(cal.D)+s+z(cal.H)+t+z(cal.I);
}

// Navigation
function goTo(branchId, symId) {
    let adr = location.href;
    adr = adr.substring(0, adr.indexOf("search"));
    adr += "branch?i=" + branchId + "&found=" + symId;
    location.assign(adr);
}
function branch(i) {
    location.assign(location.href + "branch?i=" + i);
}
function search() {
    location.assign(location.href + "search");
}
function settings() {
    location.assign(location.href + "settings");
}
