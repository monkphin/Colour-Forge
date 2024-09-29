$(document).ready(function(){
    // Initialize sidenav
    $('.sidenav').sidenav();

    // Initialize carousel
    $('.carousel').carousel();

    // Dynamically add new input field after the last input
    $(document).on('click', '.add_field', function() {
        $('<input type="text" class="input" name="field[]" value="">').insertAfter('.input:last');
    });
});