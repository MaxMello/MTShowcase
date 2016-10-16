$('#login_submit').on('submit', function (event) {
    console.log("form submitted")
    event.preventDefault();
    login_process();
});

function login_process() {
    console.log("login fired") // sanity check
    var email = $('#id_login-email').val();
    var pw = $('#id_login-password').val();
    var remember_me = $('#id_login-remember_me:checked').val()
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $.ajax({
        url: "/login/",
        type: "POST",
        data: {
            "login-email": email,
            "login-password": pw,
            "login-remember_me": remember_me
        },

        success: function (data) {
            console.log(data);
            console.log(data['form_html']);
            console.log(data['success'])
            if (!(data['success'])) {
                // update form with errors rendered
                $('#login_submit').replaceWith(data['form_html']);
                $('#login_submit').submit(function (event) {
                    event.preventDefault();
                    login_process();
                });
            } else {
                //location.reload(true);
                window.location.href = window.location.href;
            }
        },
        error: function (xhr, errmsg, err) {
            console.log(err);
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });

}



