document.addEventListener("DOMContentLoaded", function () {
  // Materialize features

  // init sidenav
  const sidenavElems = document.querySelectorAll(".sidenav");
  const sidenavInstances = M.Sidenav.init(sidenavElems, { draggable: true });

  // init carousel
  const carouselElems = document.querySelectorAll(".carousel");
  const carouselOptions = {
    fullWidth: false,
    indicators: false,
  };
  const carouselInstances = M.Carousel.init(carouselElems, carouselOptions);

 
  // Initialize Materialize Collapsible
  var elems = document.querySelectorAll('.collapsible');
  var instances = M.Collapsible.init(elems, {
    onOpenStart: function(el) {
      var header = el.querySelector('.collapsible-header');
      if (header) {
        var icon = header.querySelector('.toggle-icon');
        if (icon) {
          // Change icon to minus when opening
          icon.classList.remove('fa-plus');
          icon.classList.add('fa-minus');
        }
      }
    },
    onCloseStart: function(el) {
      var header = el.querySelector('.collapsible-header');
      if (header) {
        var icon = header.querySelector('.toggle-icon');
        if (icon) {
          // Change icon to plus when closing
          icon.classList.remove('fa-minus');
          icon.classList.add('fa-plus');
        }
      }
    }
  });

  // Handle the first stage on page load
  var firstStageHeader = document.querySelector('.collapsible-header.first-stage');
  if (firstStageHeader) {
    var firstStageIcon = firstStageHeader.querySelector('.toggle-icon');
    if (firstStageIcon) {
      firstStageIcon.classList.remove('fa-plus');
      firstStageIcon.classList.add('fa-minus'); // Ensure the first stage is open with minus icon
    }
  }

  

  // init Modal
  const modalElems = document.querySelectorAll(".modal");
  const modalInstances = M.Modal.init(modalElems, {
    opacity: 0.5,
    inDuration: 300,
    outDuration: 200,
  });

  // init dropdown
  var dropdownElems = document.querySelectorAll('.dropdown-trigger');
  M.Dropdown.init(dropdownElems, {
    constrainWidth: false,
    coverTrigger: false,
    closeOnClick: false
  });

  // Custom JS

  // Auto-resize custom textareas
  const autoResizeTextarea = () => {
    const textareas = document.querySelectorAll('.custom-textarea'); // Target all custom textareas

    textareas.forEach(function (textarea) {
      // Resize the textarea based on its content
      function autoResize() {
        textarea.style.height = 'auto'; // Reset height to auto to shrink if needed
        textarea.style.height = textarea.scrollHeight + 'px'; // Set height based on content
      }

      // Auto-resize on input event
      textarea.addEventListener('input', autoResize);
      
      // Trigger initial resize in case there's pre-filled content
      autoResize();
    });
  };

  autoResizeTextarea(); // Run auto-resize on initial load

// Prevent Enter key from submitting forms unless the form has a search input.
var forms = document.querySelectorAll('form');

forms.forEach(function(form) {
  form.addEventListener('keydown', function(event) {
    // Check if the form contains a search input element
    var containsSearchInput = form.querySelector('input[type="search"]') !== null;

    // Allow Enter key for forms with a search input, block for others.
    if (!containsSearchInput && event.key === 'Enter' && event.target.tagName !== 'TEXTAREA') {
      event.preventDefault();
      return false;
    }
  });
});


  // Set stageCount based on existing stages or default to 1 if none present.
  let stageCount = document.querySelectorAll(".multi-stage").length || 1;

  // Dynamically add new stage input field when add stage button clicked
  document.addEventListener("click", function (event) {
    if (event.target.closest(".add_field")) {
      stageCount++; // Increment stage count
      const newStage = `
      <div class="row multi-stage" data-stage-id="">
        <!-- Hidden input for new stage (no ID) -->
        <input type="hidden" name="stage_ids[]" value="">
        <input type="hidden" name="stage_nums[]" value="${stageCount}">

        <!-- Instructions Textarea -->
        <h6 class="center-align recipe-title">Recipe Stage ${stageCount}</h6>
        <div class="input-field custom-textarea-field col s12 m7">
          <textarea
            id="instructions_${stageCount}"
            class="custom-textarea"
            name="instructions[]"
            placeholder="Stage ${stageCount} Instructions (required)"
            rows="4"
            required></textarea>
          <label for="instructions_${stageCount}">Stage ${stageCount} Instructions (required)</label>
        </div>

        <!-- Image Upload Handling -->
        <div class="col s12 m5">
          <div class="file-field input-field">
           <div class="row">
            <div class="col s12 l6">
              <div class="btn teal darken-2">
                <span>Add Image</span>
                <input type="file" name="images[]" accept="image/*" >
              </div>
            </div> 
            <div class="col s12 l6">
              <div class="file-path-wrapper">
                <input
                  class="file-path validate"
                  type="text"
                  placeholder="Stage ${stageCount} image" >
              </div>
            </div>
          </div> 
          <!-- Alt Text Field -->
          <div class="input-field">
            <input
              id="image_desc_1"
              name="image_desc[]"
              type="text"
              class="validate">
            <label for="image_desc_1">Image Description</label>
          </div>
          <!-- Hidden input to track image deletion -->
          <input type="hidden" name="delete_image_${stageCount}" value="false" class="delete_image_flag">
        </div>
      </div>
      `;
      
      const stages = document.querySelectorAll(".multi-stage");
      const lastStage = stages[stages.length - 1];

      // Check if lastStage exists before inserting the new stage
      if (lastStage) {
        lastStage.insertAdjacentHTML("afterend", newStage);
      } else {
        // If no existing stages, append the new stage to a parent container
        const container = document.querySelector(".stages-container");
        container.insertAdjacentHTML("beforeend", newStage);
      }

      // Re-initialize Materialize Textareas and Labels for new elements when new stage added.
      setTimeout(function () {
        M.updateTextFields();
      }, 100);

      // Re-apply auto-resize to any new textareas that are added
      autoResizeTextarea();
    }
  });

  // Remove the last added stage when remove stage button clicked.
  document.addEventListener("click", function (event) {
    if (event.target.closest(".remove_field")) {
      if (stageCount > 1) {
        const stages = document.querySelectorAll(".multi-stage");
        const lastStage = stages[stages.length - 1];
        lastStage.parentNode.removeChild(lastStage);
        stageCount--;
      }
    }
  });

  // Select the form element by its ID.
  const form = document.getElementById("addRecipe");

  if (form) {
    form.addEventListener("submit", function (event) {
      const submitButton = document.getElementById("submitButton");
      if (submitButton) {
        submitButton.disabled = true;
      }
    });
  }

  // Reset contents of search boxes when user clicks away (using blur event)
  const mobileSearchBox = document.getElementById("mobile-search");

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
    const imageContainer = document.getElementById("image_container_" + stageNum);
    const fileInputContainer = document.getElementById("file_input_container_" + stageNum);

    if (imageContainer) {
      imageContainer.style.display = "none";
    }
    if (fileInputContainer) {
      fileInputContainer.style.display = "block";
    }

    const deleteInput = document.querySelector('input[name="delete_image_' + stageNum + '"]');
    if (deleteInput) {
      deleteInput.value = "true";
    }
  }
});

// Show existing image if user changes their mind about deletion.
document.addEventListener("click", function (event) {
  if (event.target.classList.contains("cancel_replace_button")) {
    const stageNum = event.target.getAttribute("data-stage-num");
    const imageContainer = document.getElementById("image_container_" + stageNum);
    const fileInputContainer = document.getElementById("file_input_container_" + stageNum);

    if (imageContainer) {
      imageContainer.style.display = "block";
    }
    if (fileInputContainer) {
      fileInputContainer.style.display = "none";
    }

    const deleteInput = document.querySelector('input[name="delete_image_' + stageNum + '"]');
    if (deleteInput) {
      deleteInput.value = "false";
    }
  }
});

// Allow alerts to be manually dismissed.
document.querySelectorAll(".close-flash").forEach(function (button) {
  button.addEventListener("click", function (event) {
    event.preventDefault();
    const flashMessage = button.closest(".flash-message");
    if (flashMessage) {
      flashMessage.style.transition = "opacity 0.6s ease";
      flashMessage.style.opacity = "0";
      setTimeout(function () {
        flashMessage.remove();
      }, 600);
    }
  });
});

// Auto-dismiss alerts after 2 seconds
document.querySelectorAll(".flash-message").forEach(function (message) {
  setTimeout(function () {
    message.style.transition = "opacity 0.6s ease";
    message.style.opacity = "0";
    setTimeout(function () {
      message.remove();
    }, 600);
  }, 2000);
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

// Ensure all admin toggles are captured
document.querySelectorAll("input[type='checkbox'][id^='is_admin_']").forEach(function (checkbox) {
  checkbox.addEventListener("change", function () {
    const userId = this.id.split('_').pop(); // Extract the user ID from the element ID
    const form = document.getElementById(`admin-toggle-form-${userId}`);
    if (form) {
      form.submit(); // Submit the form if it exists
    }
  });
});
