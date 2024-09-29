$(document).ready(function(){
    // Initialize sidenav
    $('.sidenav').sidenav();

    // Initialize carousel
    $('.carousel').carousel();

    // Dynamically add new input field after the last input
    $(document).on('click', '.add_field', function() {
        var stageCount = $('.input').length + 1;  // Get the current count of inputs and increment by 1
        var newStage = `
            <div class="input-field col s12">
                <textarea class="materialize-textarea input" name="instructions[]"></textarea>
                <label for="instructions">Stage ${stageCount} Instructions</label>
            </div>
        `;
        $('.input:last').parent().after(newStage);  // Insert after the last input
    });
    $(document).on('click', '.remove_field', function() {
        $('.input-field:last').remove();
    });
});




