$(document).ready(function() {         
        

            checkNotifications();
            
            $("#show-ethnicities, #show-religions").hide()

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

            ////////////////////////////////////////////////////////////
            

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

            ////////////////////////////////////////////////////////////

           getNewMatches();

            $('#slider-range-age, #slider-range-height, #slider-distance').on('mouseup', function(){
                getNewMatches();
            });

            $('input[name=gender]').on('change', function() {
                getNewMatches();
            });


});



function showUsers(users){

  $('#render-users').empty();

    // var sorted = Object.keys(users).sort(function(a,b){return users[a].age-users[b].age});
    
    // for (var i = 0; i < sorted.length; i++) {
    //     console.log(users[sorted[i]].age);
    // }

  for (let user_id in users) {
    let user = users[user_id];
    // $('<div class="image-container"><img src=/' + user.pic_url + ' width="150" height="150" data-toggle="modal" data-target=".bs-example-modal-lg" class="image" id=' + user_id + '> \
    //   <div class="addbutton btn btn-default" data-toggle="modal" data-target="#myModal" data-backdrop="static" data-keyboard="false" id=button_' + user_id + '> \
    //   <span class="glyphicon glyphicon-eye-open" aria-hidden="true"></span></div></div>').appendTo('#users-summary');


    $('<div class="col-lg-3 user-summary"><div style="text-align: center" class="well"><h4>' + user.fname + '</h4><img src=/' + user.pic_url + ' width="150" height="150"> \
        <div>' + user.age + ', ' + user.contact.city + '</div><button class="btn btn-primary" id='+ user_id +' onclick="sendRequest(' + user_id + ')">Send Request</button> \
         <i class="heart fa fa-heart-o"></i></div></div>').appendTo('#render-users');

  }

    // Its important to attach thie event listener here, not in document.ready, otheriwse it wont dbe attached
    $(".heart.fa").click(function() {
        $(this).toggleClass("fa-heart fa-heart-o");
    });

  $("body").removeClass("loading");

}


function sendRequest(user_id) {
    console.log(user_id);
    payload = {'target_userid': user_id, 'timestamp': new Date()};
    $.post("/send-request.json", payload, showSentRequest);
}

function showSentRequest(result) {
    $('#' + result.uid).html(result.response).attr("disabled", true);
}

function makeFilter() {

    let age = $('#age').val();   
    let height = $('#height').val();
    let distance = parseInt($('#distance').val());
    let gender = $('input[name="gender"]:checked').val();       //Get the value of checked radio-button
    let ethnicity = $('input[name="eth"]:checked').val();
    let religion = $('input[name="rel"]:checked').val();

    let filter = {'age': age,
                  'height': height,
                  'distance': distance,
                  'gender': gender,
                  'ethnicity': ethnicity,
                  'religion': religion};

    return filter;
}

function getNewMatches() {
    $("body").addClass("loading");
    let new_filters = makeFilter();
    $.get('/potential-matches.json',new_filters, showUsers);
}
