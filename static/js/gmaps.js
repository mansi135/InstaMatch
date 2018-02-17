  var lat_lng = [];
  var geocoder;
  var map;
  var marker;
  

  function initMap() {

      map = new google.maps.Map(document.getElementById('map'), {
        zoom: 6,
       // center: mylocation
      });
      geocoder = new google.maps.Geocoder();

  }

  function get_geo_codes() {
      for (let i = 0; i < zips.length; i++) {
          let address = zips[i];
          geocoder.geocode( { 'address': address}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
              map.setCenter(results[0].geometry.location);
              if(marker)
                  marker.setMap(null);
               //let lat = results[0].geometry.location.lat();
               //let lng = results[0].geometry.location.lng();
               //lat_lng.push({lat: lat, lat: lng});
               var marker = new google.maps.Marker({
                      position: results[0].geometry.location,
                      map: map
              });
               markers.push(marker);  //dont push logged-in user, since its already green
           }
             else {
              alert("Geocode was not successful for the followingbbbb reason: " + status);
            }
          });    
      }

      // for the current_user location
      geocoder.geocode( { 'address': my_zip}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
              map.setCenter(results[0].geometry.location);
              if(marker)
                  marker.setMap(null);
               //let lat = results[0].geometry.location.lat();
               //let lng = results[0].geometry.location.lng();
               //lat_lng.push({lat: lat, lat: lng});
               var marker = new google.maps.Marker({
                      position: results[0].geometry.location,
                      map: map,
                      icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
              });
           }
             else {
              alert("Geocode was not successful for the following reason: " + status);
            }
          }); 

  }



  //let mylocation = {lat: lat_lng[0]['lat'] , lng: lat_lng[0]['lng']};
            
  // let mylocation = {lat: {{ lat_lng[-1]['lat'] }}, lng: {{ lat_lng[-1]['lng']}}};
  // let map = new google.maps.Map(document.getElementById('map'), {
  //   zoom: 6,
  //   center: mylocation
  // });

  

  // {% for l in lat_lng[:-1] %}
  //     var m = {lat: {{ l['lat'] }}, lng: {{ l['lng'] }} };
  //     var marker = new google.maps.Marker({
  //       position: m,
  //       map: map,
  //      // icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
  //     }); 
  // {% endfor %}
  //     var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png';
  //     var marker = new google.maps.Marker({
  //       position: mylocation,
  //       map: map,
  //       icon: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
  //     });    