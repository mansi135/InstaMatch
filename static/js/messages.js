var link, to_id, fname;

$(document).ready(function() {

            // Pop-over method not using it any more , but this logic was very hard to get working
            // $(".messages").click(function(evt){
            //         $(".messages").popover('hide');
            //         var link = $(this);
            //         console.log(link);
            //         $.get("/retrieve-messages.json", 
            //               {"uid": $(this).data("id"),
            //                "fname": $(this).data("fname")}, 
            //               function(results){
            //                    // results.data = results.data.replace("\n","<br />\n");
            //                    //we cannot use 'this' here because its lost..hence we save it in a var
            //                     link.popover({content: results.data, html: true});
            //                     link.popover('show');
            //               });
            //     });

            //This is just to render initial messages
            let first_message = $('#begin > div').children('div').first()

            if (first_message.length !== 0) {
                to_id = first_message.find('a').data('id');
                fname = first_message.find('a').data('fname');
                first_message.css("background-color", "#eee");
                retrieveMessages();
            }
            

            //Attaching event-handler 
            $(".messages").click(function(evt) {
                    $('.top-div').css("background-color", "transparent");
                    link = $(this);     //probably not needed remove it...
                    to_id = $(this).data("id");
                    fname = $(this).data("fname");
                    $(this).closest('div').parent().css("background-color", "#eee");
                    //retrieveMessages();   
                   // setInterval(function(){console.log('aha');}, 3000);
                    setInterval(retrieveMessages, 2000);    //this will render periodically , but on click of somebody
                        
             });

            $('.send').on('click', recordMessage);


});

function retrieveMessages() {
    $.get("/retrieve-messages.json", { "uid": to_id, "fname": fname }, showChat);
}

// This should be displayed in ascending order
function showChat(history) {
    
    $('#chat-window').empty();
    // $('#chat-window').append("<h3>Message history with " + link.data('fname') + "</h3>");
    $('#chat-window').append("<h3>Chat history with " + fname + "</h3>");

    for (let i = 0; i < history.length; i += 3) {

        if (history[i] === 'You') {
            $('<div class="chat-box"><p style="float: right;"><b style="color: red">' + history[i] + '</b> ' + history[i+1] + '</p><p class="stamp">' + history[i+2] + '</p><p style="clear: right; float: right;"><span class="time-ago"></span></p></div>').appendTo('#chat-window');
        }
        else {
            $('<div class="chat-box darker"><p><b style="color: red">' + history[i] + '</b> ' + history[i+1] + '</p><p class="stamp">' + history[i+2] + '</p><p><span class="time-ago"></span></p></div>').appendTo('#chat-window');
        }                   
        
    }

    $('.stamp').hide();
    checkTimeAgo();

  //ver-1  $('<footer><div class="input-group"><input type="text" class="form-control" placeholder="Message" id="message-text"><span class="input-group-btn"><button class="btn btn-primary send" type="button">Send</button></span></div></footer>').appendTo('#chat-window');

    // Attach this event listener here - it wont be attached inside document.ready
  //ver-1  $('.send').on('click', recordMessage);
  $('#chat-window').scrollTop = $('#chat-window').scrollHeight ;
   
}

function recordMessage(evt) {
    
    let payload = {'text': $('#message-text').val(), 'to_id': to_id, 'timestamp': new Date()};
    $.post("/send-message", payload, function(response) {
    //ver-1    retrieveMessages();
       let myMessage = $('<div class="chat-box"><p style="float: right;"><b style="color: red">You</b> ' + $('#message-text').val() + '</p><p style="clear: right; float: right;"><span class="time-ago">' + jQuery.timeago(new Date()) + '</span></p></div>');     
       $('#chat-window').append(myMessage);
       $('#message-text').val('');
    });
 }
