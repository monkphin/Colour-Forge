$(document).ready(function(){
  var stageCount = 1;

  // Initialize sidenav
  $('.sidenav').sidenav();

  // Initialize carousel
  $('.carousel').carousel({
    fullWidth: false,  // Adjust this to your liking
    indicators: false
  });
  // Initialize Accordion
  $(document).ready(function(){
    $('.collapsible').collapsible();
  });

  // Dynamically add new input field after the last input
  $(document).on('click', '.add_field', function() {
      stageCount ++;  // Get the current count of inputs and increment by 1
      var newStage = `
          <div class="input-field col s12 multi-stage">
            <textarea id="instructions" name="instructions[]" class="materialize-textarea input" required></textarea>
            <label for="instructions">Stage ${stageCount} Instructions (required)</label>
            <div class="file-field input-field">
              <div class="btn">
                <span>Add Images</span>
                <input type="file" name="images[]" accept="image/*">
              </div>
              <div class="file-path-wrapper">
                <input class="file-path validate" type="text" placeholder="Add an optional image for stage ${stageCount}">
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
      if (stageCount > 1) {
        stageCount --;
      }
  });
});  

document.addEventListener('DOMContentLoaded', function() {
  const chipElem = document.querySelector('.chips-autocomplete');
  
  // Initialize Materialize Chips
  M.Chips.init(chipElem, {
      placeholder: 'Enter a tag',
      secondaryPlaceholder: '+Tag',
      autocompleteOptions: {
          data: tags,  
          limit: Infinity,
          minLength: 1
      },
      onChipAdd: function(e, chip) {
          // Replace the default close icon with your custom icon
          const closeIcon = chip.querySelector('.material-icons');
          if (closeIcon) {
              closeIcon.innerHTML = 'X';  // Change the icon to 'clear'
          }
          updateTagsField();
      },
      onChipDelete: function(e, chip) {
          // Explicitly remove the chip when it's deleted
          chip.remove();  
          updateTagsField();
      }
  });

  // Function to update the hidden input with tags
  function updateTagsField() {
      const instance = M.Chips.getInstance(chipElem);
      const tagsData = instance.chipsData.map(chip => chip.tag).join(',');
      document.querySelector('#tags_input').value = tagsData;
  }
});
