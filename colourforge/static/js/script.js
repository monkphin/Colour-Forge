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

  // Initialize Tooltips
  $('.tooltipped').tooltip({delay: 50});
  
  // Disable submit button on add_recipe form to prevent button spam
  $('#addRecipe').on('submit', function() {
    $('#addRecipeButton').prop('disabled', true);
  });

  // Reset contents of search boxes when user clicks away
  const searchInput = document.getElementById('search');
    
  // Add an event listener for the blur event
  searchInput.addEventListener('blur', function() {
    searchInput.value = ''; // Clear the input field when it loses focus
  });

  // Dynamically add new input field after the last input
  $(document).on('click', '.add_field', function() {
    stageCount++;  // Increment stage count
    var newStage = `
      <div class="row multi-stage" data-stage-id="">
        <!-- Hidden input for new stage (no ID) -->
        <input type="hidden" name="stage_ids[]" value="">
        <input type="hidden" name="stage_nums[]" value="${stageCount}">

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
          <!-- Hidden input to track image deletion -->
          <input type="hidden" name="delete_image_${stageCount}" value="false" class="delete_image_flag">
        </div>
      </div>
    `;
    $('.multi-stage:last').after(newStage);  // Insert after the last multi-stage

    // Initialize Materialize Textareas and Labels for new elements
    setTimeout(function() {
      M.textareaAutoResize(document.querySelectorAll('textarea'));
      M.updateTextFields();
    }, 100);
  });

  // Remove the last added input field
  $(document).on('click', '.remove_field', function() {
    if (stageCount > 1) {
      $('.multi-stage:last').remove();
      stageCount--;
    }
  });

  // Initialize Materialize Chips only if the element exists
  var chipElem = document.querySelector('.chips-autocomplete');
  if (chipElem) {
    var chipInstance = M.Chips.init(chipElem, {
      placeholder: 'Enter a tag',
      secondaryPlaceholder: '+Tag',
      autocompleteOptions: {
        data: tags, 
        limit: Infinity,
        minLength: 1
      },
      onChipAdd: function(e, chip) {
        // Replace the default close icon with fa-times icon
        const closeIcon = chip.querySelector('.material-icons');
        if (closeIcon) {
          closeIcon.classList.remove('material-icons');
          closeIcon.classList.add('fas', 'fa-times');
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

    // Populate 'tags_input' on page load
    updateTagsField();
  }

  // Function to mark images for deletion and show file input
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

    // Set the delete flag to true
    $('input[name="delete_image_' + stageNum + '"]').val('true');
  });

  // Function to unhide image if user cancels replacement
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

    // Reset the delete flag to false
    $('input[name="delete_image_' + stageNum + '"]').val('false');
  });

  // Handle manual dismissal of flash messages
  $('.close-flash').click(function(event) {
    event.preventDefault(); 
    $(this).closest('.flash-message').fadeOut('slow', function() {
      $(this).remove(); 
    });
  });

  // Handle auto-dismiss after 2 seconds (2000 milliseconds)
  $('.flash-message').each(function() {
    var $message = $(this);
    setTimeout(function() {
      $message.fadeOut('slow', function() {
        $message.remove(); 
      });
    }, 2000); // 2 second
  });

});
