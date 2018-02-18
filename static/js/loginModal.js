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
    });