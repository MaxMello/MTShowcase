//var regform = $('#register_form');

$('#myModal').on('hide.bs.modal', function (e) {
    console.log("modal closed");
    clear_form();
});

$('#register_form').on('submit', function (event) {
    event.preventDefault();
    register_process();
});

function register_process() {
    console.log("login fired") // sanity check
    var email = $('#id_signup-email').val();
    var pw = $('#id_signup-password1').val();
    var pw2 = $('#id_signup-password2').val();
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $.ajax({
        url: "/register/",
        type: "POST",
        data: {
            "signup-email": email,
            "signup-password1": pw,
            "signup-password2": pw2,
        },

        success: function (data) {
            console.log(data);
            console.log(data['form_html']);
            console.log(data['success'] + " account");
            if (!(data['success'])) {
                // Here we replace the form, for the
                $('#register_form').replaceWith(data['form_html']);
                $('#register_form').submit(function (event) {
                    event.preventDefault();
                    register_process();
                });
            } else {
                $('#register_form').replaceWith(data['message']);
            }
        },
        error: function (xhr, errmsg, err) {
            console.log(err);
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}


function clear_form() {
    console.log("ajax called");
    $.ajax({
        url: "/register/",
        type: "GET",
        success: function (data) {
            console.log("clear form success");
            // clear form html
            $('#register_form').replaceWith(data['form_html']);
            $('#register_form').submit(function (event) {
                event.preventDefault();
                register_process();
            });

        }
        ,
        error: function (xhr, errmsg, err) {
            console.log("error happe");
            //console.log(err);
            //console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}


