$(document).ready(function() {         
            

            checkNotifications();
            
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

            $("#search-form").on('submit', function(evt) {
                console.log('here');
                evt.preventDefault();
                let dist = $('#distance').val();
                console.log(dist);
                let filter = {'distance': parseInt(dist)};
                console.log(filter);
                $.get('/potential-matches.json', filter, function(response) {
                    console.log(response);
                })
            })

        });