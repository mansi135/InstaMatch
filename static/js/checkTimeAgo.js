$(document).ready(function() { 
    $('.stamp').hide();        
    checkTimeAgo();
});

function checkTimeAgo() {
            
    let all_time_stamps = $('.stamp');
    let all_time_ago = $('.time-ago');

    for (let i = 0; i < all_time_stamps.length; i++) {
        time = jQuery.timeago($(all_time_stamps[i]).text());
        $(all_time_ago[i]).html('<i>' + time + '</i>');
    }
}

        