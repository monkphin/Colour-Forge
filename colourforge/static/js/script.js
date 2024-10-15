$(document).ready(function() {

  // Set stageCount based on existing stages or default to 1 if none present. 
  var stageCount = $('.multi-stage').length || 1;

  // Initialize sidenav for mobile navigation.
  $('.sidenav').sidenav();

  // Initialize carousel for home page.
  $('.carousel').carousel({
    fullWidth: false,
    indicators: false
  });

  // Initialize Accordion for recipes.
  $('.collapsible').collapsible();

  // Initialize Modal dialogues for image pop outs and defensive deletion.
  $('.modal').modal();
 
  // Disable submit button on add_recipe form to prevent button spamming.
  $('#addRecipe').on('submit', function() {
    $('#addRecipeButton').prop('disabled', true);
  });

  // Materialize dropdown activator for admin menu.
  $('.dropdown-trigger').dropdown();

  // Reset contents of search boxes when user clicks away (using blur event)
  $('#search').on('blur', function() {
    $(this).val(''); // Clear the input field when it loses focus
  });

  // Dynamically add new stage input field when add stage button clicked
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
    $('.multi-stage:last').after(newStage);  // Insert after the previous stage.

    // Re-initialize Materialize Textareas and Labels for new elements when new stage added.
    setTimeout(function() {
      M.textareaAutoResize(document.querySelectorAll('textarea'));
      M.updateTextFields();
    }, 100);
  });

  // Remove the last added stage when remove stage button clicked.
  $(document).on('click', '.remove_field', function() {
    if (stageCount > 1) {
      $('.multi-stage:last').remove();
      stageCount--;
    }
  });

  // Function to mark images for deletion and show file input.
  $(document).on('click', '.delete_image_button', function() {
    var stageNum = $(this).attr('data-stage-num');
    var imageContainer = $('#image_container_' + stageNum);
    var fileInputContainer = $('#file_input_container_' + stageNum);

    // Hide existing image and show input fields/buttons for new image selection. 
    if (imageContainer.length) {
      imageContainer.hide();
    }
    if (fileInputContainer.length) {
      fileInputContainer.show();
    }

    // Set the hidden delete flag to true
    $('input[name="delete_image_' + stageNum + '"]').val('true');
  });

  // Show existing image if user changes their mind about deletion. 
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

    // Reset the hidden delete flag to false
    $('input[name="delete_image_' + stageNum + '"]').val('false');
  });

  // Allow alerts to be manually dismissed. 
  $('.close-flash').click(function(event) {
    event.preventDefault(); 
    $(this).closest('.flash-message').fadeOut('slow', function() {
      $(this).remove(); 
    });
  });

  // Auto-dismiss alerts after 2 seconds (2000 milliseconds)
  $('.flash-message').each(function() {
    var $message = $(this);
    setTimeout(function() {
      $message.fadeOut('slow', function() {
        $message.remove(); 
      });
    }, 2000); // 2 seconds
  });

  // Fetch existing tags for autocomplete
  const inputField = $('#tags_input');
  const tagsUrl = inputField.data('url');

  if (inputField.length) {
    $.ajax({
      url: tagsUrl,
      method: 'GET',
      success: function(tags) {
        new Awesomplete(inputField[0], {
          list: tags,
          minChars: 1,
          maxItems: 10,
          autoFirst: true,
          filter: function (text, input) {
            return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]);
          },
          replace: function (text) {
            const before = this.input.value.match(/^.+,\s*|/)[0];
            this.input.value = before + text + ", ";
          }
        });
      },
      error: function(error) {
        console.error('Error fetching tags:', error);
      }
    });
  }

});
