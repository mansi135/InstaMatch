$(document).ready(function() {         
        

            checkNotifications();
            
            let age = $('#age').val()    
            let height = $('#height').val();
            let distance = parseInt($('#distance').val());
            let gender = $('input[name="gender"]:checked').val();       //Get the value of checked radio-button
            let ethnicity = $('input[name="eth"]:checked').val();
            let religion = $('input[name="rel"]:checked').val();

            //console.log(distance, height, age, gender, ethnicity, religion);
            let filter = {'age': age,
                          'height': height,
                          'distance': distance,
                          'gender': gender,
                          'ethnicity': ethnicity,
                          'religion': religion}

            //Add event-listeners to various links
            $('.received').on('click', function() {
                $('#received').html('');
            })

            $('.sent').on('click', function() {
                $('#sent').html('');
            })

            $('.msg').on('click', function() {
                $('#msg').html('');
            })


            $("#show-ethnicities, #show-religions").hide()

            $('#eth_d_matter').on('click', function() {
                $("#show-ethnicities").hide();
            })
            $('#eth_matter').on('click', function() {
                $("#show-ethnicities").show();
            })

            $('#rel_d_matter').on('click', function() {
                $("#show-religions").hide();
            })

            $('#rel_matter').on('click', function() {
                $("#show-religions").show();
            })

            //Do this at the end
            $.get('/potential-matches.json',filter, showUsers);

        });



function showUsers(users){

    console.log(users);
  $('#render-users').empty();

  for (let user_id in users) {
    let user = users[user_id];
    // $('<div class="image-container"><img src=/' + user.pic_url + ' width="150" height="150" data-toggle="modal" data-target=".bs-example-modal-lg" class="image" id=' + user_id + '> \
    //   <div class="addbutton btn btn-default" data-toggle="modal" data-target="#myModal" data-backdrop="static" data-keyboard="false" id=button_' + user_id + '> \
    //   <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></div></div>').appendTo('#users-summary');


    $('<div class="col-sm-6 col-md-6 col-lg-4 user-summary"><div class="well"><h6>' + user.fname + '</h6><img src=/' + user.pic_url + ' width="150" height="150"> \
        <a class="btn btn-primary">SendRequest</a></div></div>').appendTo('#render-users');

  }
//  $('.image').on('click',showDetails);
  //$('.image-container').on('mouseover',showbuttons).on('mouseout',hidebuttons);
  //$('.addbutton').on('click',addMovieToWatchList);

}
