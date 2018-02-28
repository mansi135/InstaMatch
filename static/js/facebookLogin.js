// This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      console.log(response.authResponse.accessToken);
      token = response.authResponse.accessToken;
      user_id = response.authResponse.userID;
      //testAPI();

      console.log("userid  "  + user_id);

      FB.api('/me?fields=id,name,email', function(response) {

        console.log("Response id : " + response.id);
        console.log("Email : " + response.email);
        console.log("Name :" + response.name);

        let new_user = false;
       
        $.post('/fb-login', {'token': token, 'fb_id': response.id, 'email': response.email}, function(response) {
          if (response === 'Existing_User') {
           window.location.assign("/my-homepage");
          } else {
            new_user = true;
            console.log(new_user);
            // if we dont do this- nested ajax is going to an infinite loop . Must use promises/done/then here
            if (new_user) {
                  $.post('/fb-register', {}, function(response){
                      console.log(response);
                      window.location.assign("/continue-register");
                      console.log(response);
                    });

                  // FB.api('/me/picture?type=normal', function(response) {
                  //   console.log(response);
                  //   $('#my-pic').attr('src', response.picture.data.url);
                  // })
            }
          }
        });

         
        // FB.api('/me?fields=picture', function(response) {
        //   console.log(response.picture);
        //   $('#my-pic').attr('src', response.picture.data.url);
        // })

      })

    } else {
      // The person is not logged into your app or we are unable to tell.
      document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
    }
  }

  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }

  window.fbAsyncInit = function() {
    FB.init({
      appId      : '{1616471035080729}',
      cookie     : true,  // enable cookies to allow the server to access 
                          // the session
      xfbml      : true,  // parse social plugins on this page
      version    : 'v2.11' // use graph api version 2.8
    });

    // Now that we've initialized the JavaScript SDK, we call 
    // FB.getLoginStatus().  This function gets the state of the
    // person visiting this page and can return one of three states to
    // the callback you provide.  They can be:
    //
    // 1. Logged into your app ('connected')
    // 2. Logged into Facebook, but not your app ('not_authorized')
    // 3. Not logged into Facebook and can't tell if they are logged into
    //    your app or not.
    //
    // These three cases are handled in the callback function.

    // FB.getLoginStatus(function(response) {
    //   statusChangeCallback(response);
    // });

  };

  // Load the SDK asynchronously
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "https://connect.facebook.net/en_US/sdk.js";
    // js.src="https://connect.facebook.net/en_GB/sdk.js#xfbml=1&version=v2.11&appId=1616471035080729&autoLogAppEvents=1";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
      console.log('Successful login for: ' + response.name);
      document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
    });
  }


// This can happen on main page only
$(document).ready(function() {
  $("#fb-logout").on('click', function () {
    FB.getLoginStatus(function(response) {
      if (response.status === 'connected') {
        FB.logout(function() {
          //window.location.assign('/logout');
          alert('fb-logged-out');
        });
      } 
    })
  })
});
