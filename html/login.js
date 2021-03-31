// Saved values
if (localStorage.getItem('login') != null)
    $("#user").val(localStorage.getItem('login'));
if (localStorage.getItem('passw') != null)
    $("#pass").val(localStorage.getItem('passw'));

// Login
$("#go").click(function() {
    localStorage.setItem('login', $("#user").val());
    localStorage.setItem('passw', $("#pass").val());
    $.ajax({
        url: "/action?q=login&a1=" + $("#user").val() + "&a2=" + $("#pass").val(),
        context: document.body,
        timeout: 15000
    }).done(function(data) {
        if (data == "True") location.reload();
        else if (data == "False") alert("اتصال برقرار نشد!");
        else alert("ERROR: " + data);
    });
});
