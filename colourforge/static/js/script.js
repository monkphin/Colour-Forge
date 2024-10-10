$(document).ready(function() {
  // Set stageCount based on existing stages
  var stageCount = $('.multi-stage').length || 1;

  // Initialize sidenav
  $('.sidenav').sidenav();

  // Initialize carousel
  $('.carousel').carousel({
    fullWidth: false,  // Adjust this to your liking
    indicators: false
  });

  // Initialize Accordion
  $('.collapsible').collapsible();

  // Initialize Modal 
  $('.modal').modal();

  // Disable submit button on add_recipe form to prevent button spam
  $('#addRecipe').on('submit', function() {
    $('#addRecipeButton').prop('disabled', true);
  });

  // Dynamically add new input field after the last input
  $(document).on('click', '.add_field', function() {
    stageCount++;  // Increment stage count
    var newStage = `
      <div class="row multi-stage">
        <div class="input-field col s7">
          <textarea id="instructions_${stageCount}" name="instructions[]" class="materialize-textarea input" required></textarea>
          <label for="instructions_${stageCount}">Stage ${stageCount} Instructions (required)</label>
        </div>
        <div class="col s5">
          <div class="file-field input-field">
            <div class="btn">
              <span>Add Image</span>
              <input type="file" name="images[]" accept="image/*">
            </div>
            <div class="file-path-wrapper">
              <input class="file-path validate" type="text" placeholder="Stage ${stageCount} image">
            </div>
            <div class="input-field">
              <textarea id="image_desc_${stageCount}" name="image_desc[]" class="materialize-textarea"></textarea>
              <label for="image_desc_${stageCount}">Image Description</label>
            </div>
          </div>
        </div>
      </div>
    `;
    $('.multi-stage:last').after(newStage);  // Insert after the last multi-stage
  });

  // Remove the last added input field
  $(document).on('click', '.remove_field', function() {
    if (stageCount > 1) {
      $('.multi-stage:last').remove();
      stageCount--;
    }
  });

  // Initialize Materialize Chips
  var chipElem = document.querySelector('.chips-autocomplete');
  M.Chips.init(chipElem, {
    placeholder: 'Enter a tag',
    secondaryPlaceholder: '+Tag',
    autocompleteOptions: {
      data: tags,  // Ensure 'tags' is defined in your script
      limit: Infinity,
      minLength: 1
    },
    onChipAdd: function(e, chip) {
      // Replace the default close icon with your custom icon
      const closeIcon = chip.querySelector('.material-icons');
      if (closeIcon) {
        closeIcon.innerHTML = 'X';  // Change the icon to 'X'
      }
      updateTagsField();
    },
    onChipDelete: function(e, chip) {
      updateTagsField();
    }
  });

  // Function to update the hidden input with tags
  function updateTagsField() {
    const instance = M.Chips.getInstance(chipElem);
    const tagsData = instance.chipsData.map(chip => chip.tag).join(',');
    document.querySelector('#tags_input').value = tagsData;
  }

  // Function to hide images/show fields to replace images
  $(document).on('click', '.delete_image_button', function() {
    var stageNum = $(this).attr('data-stage-num');
    var imageContainer = $('#image_container_' + stageNum);
    var fileInputContainer = $('#file_input_container_' + stageNum);

    if (imageContainer.length) {
      imageContainer.hide();
    }
    if (fileInputContainer.length) {
      fileInputContainer.show();
    }
  });

  // Function to unhide image if user changes their mind
  $(document).on('click', '.cancel_replace_button', function() {
    var stageNum = $(this).attr('data-stage-num');
    var imageContainer = $('#image_container_' + stageNum);
    var fileInputContainer = $('#file_input_container_' + stageNum);

    if (imageContainer.length) {
      imageContainer.show();
    }
    if (fileInputContainer.length) {
      fileInputContainer.hide();
    }
  });
});
