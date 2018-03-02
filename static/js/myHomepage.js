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

    else if (criteria === 'favorited') {
        // sorted = unsorted.filter(function(id) {
        //     return users[id].fav === true;
        // })
        sorted = unsorted.sort(function(a, b) {
            if (users[a].fav === true) {
                return -1;
            } else {
                return +1;
            }
        })
    }

    return sorted;
} 


function showUsers(users){

  $('#render-users').empty();

  currentlyRenderedUsers = users;

  let sorted = sortCriterias($('#sort').val(), users);
    
  for (let i = 0; i < sorted.length; i++) {
    
    let user = users[sorted[i]];
    let fav;
    if (user.fav === true){         // jsonify converted python True to JS true
        favClass = "fa-heart";      // if the user is already favorited , then initial with this class
    } else {
        favClass = "fa-heart-o";
    }

    let noon = "new"; //this was giving a funny error when i put it directly into string ..hence i gave it funny name

    $('<div class="col-lg-3 user-summary"><div style="border-radius: 10%; text-align: center" class="well"><h4>' + user.fname + '</h4><a href="/users/' + sorted[i] + '?status=' + noon + '"> \
         <img src=/' + user.pic_url + ' width="150" height="150"></a><div>' + user.age + ', ' + user.contact.city + '-' + user.contact.state + '</div> \
         <button class="btn btn-primary" id='+ sorted[i] +' onclick="sendRequest(' + sorted[i] + ')">Send Request</button> \
          <i class="heart fa ' + favClass + '"></i></div></div>').appendTo('#render-users');

  }


    // Its important to attach this event listener here, not in document.ready, otheriwse it wont be attached
    $(".heart.fa").click(function() {
        
        $(this).toggleClass("fa-heart fa-heart-o");
        let fav_person_id = $(this).closest('div').find('button').attr('id');
        let action;


        if($(this).hasClass("fa-heart")) {
            console.log("hasit");
            action = "fav";
            // we need this because if user makes somebody fav and we sort-by-fav then currentlyRenderedUsers still have old fav property
            currentlyRenderedUsers[fav_person_id].fav = true;   
        }
        else {
            console.log("not-hasit");
            action = "un-fav";
            currentlyRenderedUsers[fav_person_id].fav = false;
        }

        $.post('/mark-fav', {'target_id': fav_person_id, 'action': action}, function(response){
            console.log(response);
        })
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
