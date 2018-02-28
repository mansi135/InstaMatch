var currentlyRenderedUsers;


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

            $('input[name="gender"]').on('change', function() {
                getNewMatches();
            });

            $('#sort').on('change', function() {
                console.log(currentlyRenderedUsers);
                showUsers(currentlyRenderedUsers);
            })


});


function sortCriterias(criteria, users) {
    
    let unsorted = Object.keys(users);
    console.log("unsorted=", unsorted);
    let sorted;

    if (criteria === 'age-asc') {
        sorted = unsorted.sort(function(a, b) {
            if (users[a].age > users[b].age) {
                return 1;
            } else if (users[a].age < users[b].age) {
                return -1;
            } else {
                return 0;
            }
        });
    }

    else if (criteria === 'age-desc') {
        sorted = unsorted.sort(function(a, b) {
            if (users[a].age < users[b].age) {
                return 1;
            } else if (users[a].age > users[b].age) {
                return -1;
            } else {
                return 0;
            }
        });
    }

    else if (criteria === 'height-tallest') {
        sorted = unsorted.sort(function(a, b) {
            if (users[a].height > users[b].height) {
                return 1;
            } else if (users[a].height < users[b].height) {
                return -1;
            } else {
                return 0;
            }
        });
    }

    else if (criteria === 'height-shortest') {
        sorted = unsorted.sort(function(a, b) {
            if (users[a].height < users[b].height) {
                return 1;
            } else if (users[a].height > users[b].height) {
                return -1;
            } else {
                return 0;
            }
        });
    }

    else if (criteria === 'relevance') {
        sorted = unsorted;
    }

    return sorted;
} 


function showUsers(users){

  $('#render-users').empty();

  currentlyRenderedUsers = users;
  console.log(currentlyRenderedUsers);

  let sorted = sortCriterias($('#sort').val(), users);
  // originallyRenderedUsers = users;

    // let unsorted = Object.keys(users);

    // console.log(unsorted);

    // let sorted = unsorted.sort(function(a, b) {
    //     if (users[a].age > users[b].age) {
    //         return 1;
    //     } else if (users[a].age < users[b].age) {
    //         return -1;
    //     } else {
    //         return 0;
    //     }
    // });

    // console.log(sorted);
    
  for (let i = 0; i < sorted.length; i++) {
    let user = users[sorted[i]];

    $('<div class="col-lg-3 user-summary"><div style="border-radius: 10%; text-align: center" class="well"><h4>' + user.fname + '</h4><a href="/users/' + sorted[i] + '?status="new"> \
         <img src=/' + user.pic_url + ' width="150" height="150"></a><div>' + user.age + ', ' + user.contact.city + '-' + user.contact.state + '</div> \
         <button class="btn btn-primary" id='+ sorted[i] +' onclick="sendRequest(' + sorted[i] + ')">Send Request</button> \
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
