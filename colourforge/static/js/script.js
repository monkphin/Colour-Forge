$(document).ready(function(){
    // Initialize sidenav
    $('.sidenav').sidenav();

    // Initialize carousel
    $('.carousel').carousel();

    // Initialize Tags
    $('.chips-autocomplete').chips({
      placeholder: 'Enter a tag',
      secondaryPlaceholder: '+Tag',
      autocompleteOptions: {
        data: {
          'Apple': null,
          'Microsoft': null,
          'Google': null
        },
        limit: Infinity,
        minLength: 1
      }
    });

    // Dynamically add new input field after the last input
    $(document).on('click', '.add_field', function() {
        var stageCount = $('.input').length + 1;  // Get the current count of inputs and increment by 1
        var newStage = `
            <div class="input-field col s12 multi-stage">
              <textarea id="instructions" name="instructions[]" class="materialize-textarea input" required></textarea>
              <label for="instructions">Stage ${stageCount} Instructions</label>
              <div class="file-field input-field">
                <div class="btn">
                  <span>Add Images</span>
                  <input type="file" name="images[]" accept="image/*">
                </div>
                <div class="file-path-wrapper">
                  <input class="file-path validate" type="text" placeholder="Add an image for this stage: Stage ${stageCount}">
                  <div class="input-field">
                    <textarea id="image_desc" name="image_desc[]" class="materialize-textarea"></textarea>
                    <label for="image_desc">Image Description</label>
                  </div>
                </div>
            </div>
        `;
        $('.input:last').parent().after(newStage);  // Insert after the last input
    });
    $(document).on('click', '.remove_field', function() {
        $('.multi-stage:last').remove();
    });
});