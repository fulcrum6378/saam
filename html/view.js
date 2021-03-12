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
