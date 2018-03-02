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
            to_id = $('#begin').children('div').first().find('a').data('id');
            fname = $('#begin').children('div').first().find('a').data('fname');
            retrieveMessages();

            //Attaching event-handler 
            $(".messages").click(function(evt) {
                    $('.top-div').css("background-color", "transparent");
                    link = $(this);     //probably not needed remove it...
                    to_id = $(this).data("id");
                    fname = $(this).data("fname");
                    $(this).closest('div').parent().css("background-color", "#eee");
                    retrieveMessages();
                        
             });
});

function retrieveMessages() {
    $.get("/retrieve-messages.json", { "uid": to_id, "fname": fname }, showChat);
}

// This should be displayed in ascending order
function showChat(history) {
    
    $('#chat-window').empty();
    // $('#chat-window').append("<h3>Message history with " + link.data('fname') + "</h3>");
    $('#chat-window').append("<h3>Message history with " + fname + "</h3>");

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

    $('<footer><div class="input-group"><input type="text" class="form-control" placeholder="Message" id="message-text"><span class="input-group-btn"><button class="btn btn-primary send" type="button">Send</button></span></div></footer>').appendTo('#chat-window');

    // Attach this event listener here - it wont be attached inside document.ready
    $('.send').on('click', recordMessage);
   
}

function recordMessage(evt) {
    
    let payload = {'text': $('#message-text').val(), 'to_id': to_id, 'timestamp': new Date()};
    $.post("/send-message", payload, function(response) {
        retrieveMessages();
    });
 }
