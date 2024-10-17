document.addEventListener("DOMContentLoaded", function () {
  // Materialise features

  // init sidenav
  var elems = document.querySelectorAll(".sidenav");
  var instances = M.Sidenav.init(elems);

  // init carousel
  var elems = document.querySelectorAll(".carousel");
  var options = {
    fullWidth: false,
    indicators: false,
  };
  var instances = M.Carousel.init(elems, options);

  //init collapsible for accordion
  var elems = document.querySelectorAll(".collapsible");
  var instances = M.Collapsible.init(elems);

  // init Modal
  var elems = document.querySelectorAll(".modal");
  var instances = M.Modal.init(elems);

  //init dropdown
  var elems = document.querySelectorAll(".dropdown-trigger");
  var instances = M.Dropdown.init(elems);

  // Custom JS

  // Set stageCount based on existing stages or default to 1 if none present.
  // Set stageCount based on existing stages or default to 1 if none present.
  var stageCount = document.querySelectorAll(".multi-stage").length || 1;

  // Set stageCount based on existing stages or default to 1 if none present.
  var stageCount = document.querySelectorAll(".multi-stage").length || 1;

  // Dynamically add new stage input field when add stage button clicked
  document.addEventListener("click", function (event) {
    if (event.target.closest(".add_field")) {
      stageCount++; // Increment stage count
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
      // Insert after the previous stage.
      var stages = document.querySelectorAll(".multi-stage");
      var lastStage = stages[stages.length - 1];

      // Check if lastStage exists before inserting the new stage
      if (lastStage) {
        lastStage.insertAdjacentHTML("afterend", newStage);
      } else {
        // If no existing stages, append the new stage to a parent container
        var container = document.querySelector(".stages-container"); // Ensure you have a parent container
        container.insertAdjacentHTML("beforeend", newStage);
      }

      // Re-initialize Materialize Textareas and Labels for new elements when new stage added.
      setTimeout(function () {
        // Select all textareas
        var textareas = document.querySelectorAll("textarea");
        textareas.forEach(function (textarea) {
          M.textareaAutoResize(textarea);
        });

        // Update text fields
        M.updateTextFields();
      }, 100);
    }
  });

  // Remove the last added stage when remove stage button clicked.
  document.addEventListener("click", function (event) {
    if (event.target.closest(".remove_field")) {
      if (stageCount > 1) {
        var stages = document.querySelectorAll(".multi-stage");
        var lastStage = stages[stages.length - 1];
        lastStage.parentNode.removeChild(lastStage);
        stageCount--;
      }
    }
  });

  // Select the form element by its ID.
  var form = document.getElementById("addRecipe");

  if (form) {
    // Add an event listener to the form for the 'submit' event.
    form.addEventListener("submit", function (event) {
      // Select the submit button by its ID.
      var submitButton = document.getElementById("addRecipeButton");
      // Disable the submit button to prevent multiple submissions.
      if (submitButton) {
        submitButton.disabled = true;
      }
    });
  }

  // Reset contents of search boxes when user clicks away (using blur event)
  // Select the input element by its ID.
  var desktopSearchBox = document.getElementById("desktop-search");
  var mobileSearchBox = document.getElementById("mobile-search");

  // Add a blur event listener to the input field.
  // for desktop
  if (desktopSearchBox) {
    desktopSearchBox.addEventListener("blur", function () {
      desktopSearchBox.value = "";
    });
  }
  // for mobile
  if (mobileSearchBox) {
    mobileSearchBox.addEventListener("blur", function () {
      mobileSearchBox.value = "";
    });
  }
});

// Function to mark images for deletion and show file input.
document.addEventListener("click", function (event) {
  if (event.target.classList.contains("delete_image_button")) {
    const stageNum = event.target.getAttribute("data-stage-num");
    const imageContainer = document.getElementById(
      "image_container_" + stageNum
    );
    const fileInputContainer = document.getElementById(
      "file_input_container_" + stageNum
    );

    // Hide existing image and show input fields/buttons for new image selection.
    if (imageContainer) {
      imageContainer.style.display = "none";
    }
    if (fileInputContainer) {
      fileInputContainer.style.display = "block";
    }

    // Set the hidden delete flag to true
    const deleteInput = document.querySelector(
      'input[name="delete_image_' + stageNum + '"]'
    );
    if (deleteInput) {
      deleteInput.value = "true";
    }
  }
});

// Show existing image if user changes their mind about deletion.
document.addEventListener("click", function (event) {
  if (event.target.classList.contains("cancel_replace_button")) {
    const stageNum = event.target.getAttribute("data-stage-num");
    const imageContainer = document.getElementById(
      "image_container_" + stageNum
    );
    const fileInputContainer = document.getElementById(
      "file_input_container_" + stageNum
    );

    if (imageContainer) {
      imageContainer.style.display = "block";
    }
    if (fileInputContainer) {
      fileInputContainer.style.display = "none";
    }

    // Reset the hidden delete flag to false
    const deleteInput = document.querySelector(
      'input[name="delete_image_' + stageNum + '"]'
    );
    if (deleteInput) {
      deleteInput.value = "false";
    }
  }
});

// Allow alerts to be manually dismissed.
document.querySelectorAll(".close-flash").forEach(function (button) {
  button.addEventListener("click", function (event) {
    event.preventDefault();
    let flashMessage = button.closest(".flash-message");
    if (flashMessage) {
      flashMessage.style.transition = "opacity 0.6s ease";
      flashMessage.style.opacity = "0";
      setTimeout(function () {
        flashMessage.remove();
      }, 600); // Match the 'slow' fade duration (600ms)
    }
  });
});

// Auto-dismiss alerts after 2 seconds (2000 milliseconds)
document.querySelectorAll(".flash-message").forEach(function (message) {
  setTimeout(function () {
    message.style.transition = "opacity 0.6s ease";
    message.style.opacity = "0";
    setTimeout(function () {
      message.remove();
    }, 600); // Match the 'slow' fade duration (600ms)
  }, 2000); // 2 seconds
});

// Awesomeplete Tag handling
document.addEventListener("DOMContentLoaded", function () {
  const inputField = document.getElementById("tags_input");

  if (inputField) {
    const tagsUrl = inputField.getAttribute("data-url");

    fetch(tagsUrl, { method: "GET" })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then((tags) => {
        new Awesomplete(inputField, {
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
          },
        });
      })
      .catch((error) => {
        console.error("Error fetching tags:", error);
      });
  }
});
