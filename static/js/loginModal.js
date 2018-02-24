$(document).ready(function() {
    
        $("#login").on("submit", function(evt) {
            evt.preventDefault();
            let email = $("#email").val();
            let password = $("#password").val();
            $.post("/login", {"email": email, "password": password},
                function(response) {
                    if (response.status === 'OK') {
                        window.location.assign("/my-homepage");
                    } else {
                        alert(response.msg);
                        window.location.assign("/");    // equivalent of redirect in flask is window.location
                    }  
                });
            });


        $("#register").on("submit", function(evt) {
            evt.preventDefault();

            data = $('#register').serialize();
            console.log(data);

            $.post("/register", data,
                function(response) {
                    if (response.status === 'OK') {
                        //alert(response.msg);
                        window.location.assign('/continue-register');
                    } else {
                        alert(response.msg);
                        window.location.assign("/");    // equivalent of redirect in flask is window.location
                    }  
                });
        });
    });