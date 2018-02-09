
//Calculates age from given Birth Date in the form//
function calcAge() {

    var today = new Date();
    var birthDate = new Date($('#date-of-birth').val());
    var age = today.getFullYear() - birthDate.getFullYear();
    var m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age = age-1;
    }
    return age;
}

    
// In Ajax, form submission should always be prevented by Default. Here we will prevent only if we want
// Its always advisable to grab form id and not submit-button id 
// Since we grab form-id, event is 'submit', if it was 'submit-button', event would be 'click'
$(document).ready(function() {
    $("#register-form-submit").on('submit', function(evt) {
        let age = calcAge();
        if (age < 15 ) {
            evt.preventDefault();
            alert('Age cannot be less than 15');
        } 
    })
})