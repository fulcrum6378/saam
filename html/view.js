$(".container > div:not(:first-child) > div").click(function() {
    let input = document.body.appendChild(document.createElement("input"));
    input.value = $(this).text();
    input.focus();
    input.select();
    document.execCommand('copy');
    input.parentNode.removeChild(input);

    if ($(this).hasClass("copied")) $(this).removeClass("copied");
    $(this).addClass("copied");
    setTimeout(() => { $(this).removeClass("copied"); }, 1000);
});
