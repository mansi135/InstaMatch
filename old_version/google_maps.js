
let lat_lng = [];
function initMap() {

  geocoder = new google.maps.Geocoder();
  for (let i = 0; i < zips.length; i++) {
        let address = zips[i];
        
        geocoder.geocode( { 'address': address}, function(results, status) {
          if (status == google.maps.GeocoderStatus.OK) {
             let lat = results[0].geometry.location.lat();
             let lng = results[0].geometry.location.lng();
             lat_lng.push({'lat': lat, 'lng': lng});
             console.log("here", lat_lng);
            }
           else {
            alert("Geocode was not successful for the following reason: " + status);
          }
        });    
    }

    console.log(lat_lng);
    let x = lat_lng[0].lat;

    let mylocation = {'lat': lat_lng[0].lat , 'lng': lat_lng[0]['lng']};
    let map = new google.maps.Map(document.getElementById('map'), {
      zoom: 6,
      center: mylocation
    });
    for (var i=0; i < lat_lng.length; i++) {
      var m = {lat: lat_lng[i]['lat'], lng: lat_lng[i]['lng'] };
        var marker = new google.maps.Marker({
          position: m,
          map: map,
         // icon: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
        }); 
    }
        
        
}



// function initMap() {
//     let mylocation = {lat: lat_lng[-1]['lat'], lng: lat_lng[-1]['lng']};
//     let map = new google.maps.Map(document.getElementById('map'), {
//       zoom: 5,
//       center: mylocation
//     });

//     {% for l in lat_lng %}
//         var icon = {
//             url: "/static/images/me.png", // url
//             scaledSize: new google.maps.Size(25, 25), // scaled size
//             origin: new google.maps.Point(0,0), // origin
//             anchor: new google.maps.Point(0, 0) // anchor
//         };
        
//           var goldStar = {
//               path: 'M 125,5 155,90 245,90 175,145 200,230 125,180 50,230 75,145 5,90 95,90 z',
//               fillColor: 'yellow',
//               fillOpacity: 0.8,
//               scale: 1,
//               strokeColor: 'gold',
//               strokeWeight: 5
//             };
//         var m = {lat: {{ l['lat'] }}, lng: {{ l['lng'] }} };
//         var marker = new google.maps.Marker({
//           position: m,
//           map: map,
//           //icon: goldStar
//         }); 
//     {% endfor %}
//         var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png';
//         var marker = new google.maps.Marker({
//           position: mylocation,
//           map: map,
//           icon: image
//         });
// }

