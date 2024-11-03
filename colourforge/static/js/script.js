/**
 * This JavaScript file initializes Materialize components and custom functionalities for the website.
 *
 * Contents:
 * - **Materialize Initialization**: Sets up Sidenav, Carousel, Collapsible elements, Modals, and Dropdowns.
 * - **Auto-Resizing Textareas**: Automatically adjusts textarea height based on content.
 * - **Form Handling**:
 *   - Prevents form submission with Enter key in non-search forms.
 *   - Disables submit buttons after form submission to prevent multiple submissions.
 * - **Dynamic Recipe Stages**: Allows users to add or remove recipe stages dynamically.
 * - **Delete Account Button Control**: Enables or disables the delete account button based on password input.
 * - **Search Box Reset**: Clears the mobile search box content when it loses focus.
 * - **Awesomplete Tag Suggestions**: Implements tag suggestion and autocomplete functionality for input fields.
 * - **Admin Toggle Forms**: Submits forms when admin status checkboxes are changed.
 * - **Flash Messages**:
 *   - Allows manual dismissal of flash messages.
 *   - Automatically dismisses flash messages after a set timeout.
 * - **Image Deletion and Replacement**: Handles image deletion and replacement in forms.
 *
 * Note:
 * - The `onSubmit` function for reCAPTCHA submission is defined globally to be accessible by external scripts.
 */

// Ensure this script is loaded after all HTML elements are rendered, typically at the end of the body.
document.addEventListener("DOMContentLoaded", function() {
    // **Materialize Features Initialization**
    /**
     * Initializes the Materialize Sidenav component for responsive side navigation menus.
     */
    const sidenavElems = document.querySelectorAll(".sidenav");
    const sidenavInstances = M.Sidenav.init(sidenavElems, {
        draggable: true
    });

    /**
     * Initializes the Materialize Carousel component for image sliders or content carousels.
     */
    const carouselElems = document.querySelectorAll(".carousel");
    const carouselOptions = {
        fullWidth: false,
        indicators: false,
    };
    const carouselInstances = M.Carousel.init(carouselElems, carouselOptions);

    /**
     * Initializes the Materialize Collapsible component for expandable content sections.
     * Updates toggle icons based on collapse state.
     */
    const elems = document.querySelectorAll(".collapsible");
    const instances = M.Collapsible.init(elems, {
        /**
         * Event handler when a collapsible item is opening.
         * @param {Element} el - The collapsible item element that is opening.
         */
        onOpenStart: function(el) {
            const header = el.querySelector(".collapsible-header");
            if(header) {
                const icon = header.querySelector(".toggle-icon");
                if(icon) {
                    // Change icon to minus when opening
                    icon.classList.remove("fa-plus");
                    icon.classList.add("fa-minus");
                }
            }
        },
        /**
         * Event handler when a collapsible item is closing.
         * @param {Element} el - The collapsible item element that is closing.
         */
        onCloseStart: function(el) {
            const header = el.querySelector(".collapsible-header");
            if(header) {
                const icon = header.querySelector(".toggle-icon");
                if(icon) {
                    // Change icon to plus when closing
                    icon.classList.remove("fa-minus");
                    icon.classList.add("fa-plus");
                }
            }
        },
    });
    // Handle the first collapsible stage on page load
    const firstStageHeader = document.querySelector(".collapsible-header.first-stage");
    if(firstStageHeader) {
        const firstStageIcon = firstStageHeader.querySelector(".toggle-icon");
        if(firstStageIcon) {
            firstStageIcon.classList.remove("fa-plus");
            firstStageIcon.classList.add("fa-minus");
        }
    }

    /**
     * Initializes the Materialize Modal component for dialog windows.
     */
    const modalElems = document.querySelectorAll(".modal");
    const modalInstances = M.Modal.init(modalElems, {
        opacity: 0.6,
        inDuration: 300,
        outDuration: 200,
    });

    /**
     * Initializes the Materialize Dropdown component for dropdown menus.
     */
    const dropdownElems = document.querySelectorAll(".dropdown-trigger");
    M.Dropdown.init(dropdownElems, {
        constrainWidth: false,
        coverTrigger: false,
        closeOnClick: false,
    });

    // **Custom JavaScript Functions**
    /**
     * Automatically resizes custom textareas based on their content.
     */
    const autoResizeTextarea = () => {
        const textareas = document.querySelectorAll(".custom-textarea");
        textareas.forEach(function(textarea) {
            // Adjusts the height of a textarea to fit its content.
            function autoResize() {
                textarea.style.height = "auto";
                textarea.style.height = textarea.scrollHeight + "px";
            }
            // Auto-resize on input event
            textarea.addEventListener("input", autoResize);
            // Trigger initial resize in case there's pre-filled content
            autoResize();
        });
    };
    // Run auto-resize on initial load
    autoResizeTextarea();

    /**
     * Prevents the Enter key from submitting forms unless the form contains a search input.
     */
    const forms = document.querySelectorAll("form");
    forms.forEach(function(form) {
        // Skip the login and Register Forms
        if(form.id === "loginForm" || form.id === "registrationForm") {
            return;
        }
        form.addEventListener("keydown", function(event) {
            // Check if the form contains a search input element
            const containsSearchInput = form.querySelector("input[type='search']") !== null;
            // Allow Enter key for forms with a search input, block for others.
            if(!containsSearchInput && event.key === "Enter" && event.target.tagName !== "TEXTAREA") {
                event.preventDefault();
                return false;
            }
        });
    });

    /**
     * Initializes the dynamic addition and removal of recipe stages.
     */
    // Set stageCount based on existing stages or default to 1 if none present.
    let stageCount = document.querySelectorAll(".multi-stage").length || 1;
    const removeStageButton = document.querySelector(".remove_field");

    // Function to enable or disable the remove stage button
    function updateRemoveButtonState() {
        if (removeStageButton) {
            if (stageCount > 1) {
                // Enable the Remove Stage button
                removeStageButton.disabled = false;
                removeStageButton.classList.remove('disabled');

                // Access the tooltip container (parent of the button)
                const tooltipContainer = removeStageButton.parentElement;

                // Remove tooltip attributes
                tooltipContainer.removeAttribute('data-tooltip');
                tooltipContainer.removeAttribute('title');
            } else {
                // Disable the Remove Stage button
                removeStageButton.disabled = true;
                removeStageButton.classList.add('disabled');

                // Access the tooltip container (parent of the button)
                const tooltipContainer = removeStageButton.parentElement;

                // Add tooltip explanation
                tooltipContainer.setAttribute('data-tooltip', 'Cannot remove stage when only one stage exists.');
            }
        }	
    }
    updateRemoveButtonState();

    // Event listener for Add Stage button
    const addFieldButton = document.querySelector(".add_field");
    if (addFieldButton) {
        addFieldButton.addEventListener("click", function() {
            stageCount++; // Increment stage count
            // Logic to add a new stage...
            // After adding a stage, update the button state
            updateRemoveButtonState();
        });
    }

    // Event listener for Remove Stage button
    const removeFieldButton = document.querySelector(".remove_field");
    if (removeFieldButton) {
        removeFieldButton.addEventListener("click", function() {
            if(stageCount > 1) {
                // Logic to remove the last stage...
                stageCount--; // Decrement stage count
                // After removing a stage, update the button state
                updateRemoveButtonState();
            }
        });
    }


    /**
     * Generates the HTML for a new Recipe Stage
     */
    document.addEventListener("click", function(event) {
        if(event.target.closest(".add_field")) {
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
           <div class="row center-align">
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
              id="image_desc_${stageCount}"
              name="image_desc[]"
              type="text"
              class="validate">
            <label for="image_desc_${stageCount}">Image Description (Optional)</label>
          </div>
          <!-- Hidden input to track image deletion -->
          <input type="hidden" name="delete_image_${stageCount}" value="false" class="delete_image_flag">
        </div>
      </div>
      `;
            const stages = document.querySelectorAll(".multi-stage");
            const lastStage = stages[stages.length - 1];
            // Check if lastStage exists before inserting the new stage
            if(lastStage) {
                lastStage.insertAdjacentHTML("afterend", newStage);
            } else {
                // If no existing stages, append the new stage to a parent container
                const container = document.querySelector(".stages-container");
                container.insertAdjacentHTML("beforeend", newStage);
            }
            // Re-initialize Materialize Textareas and Labels for new elements when new stage added.
            setTimeout(function() {
                M.updateTextFields();
            }, 100);
            // Re-apply auto-resize to any new textareas that are added
            autoResizeTextarea();

            updateRemoveButtonState();
        }
    });
    // Remove the last added stage when remove stage button clicked.
    document.addEventListener("click", function(event) {
        if(event.target.closest(".remove_field")) {
            if(stageCount > 1) {
                const stages = document.querySelectorAll(".multi-stage");
                const lastStage = stages[stages.length - 1];
                lastStage.parentNode.removeChild(lastStage);
                stageCount--;
                updateRemoveButtonState();
            }
        }
    });

    /**
     * Disables the submit button after form submission to prevent multiple submissions.
     */
    document.querySelectorAll("form").forEach(function(form) {
        // Exclude the contact form since reCAPTCHA handles it differently
        if(form.id !== "contact-form") {
            form.addEventListener("submit", function(event) {
                const submitButton = form.querySelector("button[type='submit']");
                if(submitButton) {
                    submitButton.disabled = true;
                }
            });
        }
    });

    /**
     * Resets the content of search boxes when the user clicks away.
     */
    const mobileSearchBox = document.getElementById("mobile-search");
    if(mobileSearchBox) {
        mobileSearchBox.addEventListener("blur", function() {
            mobileSearchBox.value = "";
        });
    }

    /**
     * Handles the Awesomplete tag suggestion and autocomplete functionality.
     * Taken from https://elixirforum.com/t/how-to-use-a-js-library-like-awesomplete-within-a-liveview/32251/9
     */
    const inputField = document.getElementById("tags_input");
    if(inputField) {
        const tagsUrl = inputField.getAttribute("data-url");
        fetch(tagsUrl, {
            method: "GET"
        }).then((response) => {
            if(!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        }).then((tags) => {
            const awesompleteInstance = new Awesomplete(inputField, {
                list: tags,
                minChars: 1,
                maxItems: 10,
                autoFirst: true,
                filter: function(text, input) {
                    return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]);
                },
                replace: function(text) {
                    const before = this.input.value.match(/^.+,\s*|/)[0];
                    this.input.value = before + text + ", ";
                },
            });
        });
    }

    /**
     * Submits the admin toggle form when the admin checkbox is changed.
     */
    document.querySelectorAll("input[type='checkbox'][id^='is_admin_']").forEach(function(checkbox) {
        checkbox.addEventListener("change", function() {
            const userId = this.id.split("_").pop(); // Extract the user ID from the element ID
            const form = document.getElementById(`admin-toggle-form-${userId}`);
            if(form) {
                form.submit(); // Submit the form
            }
        });
    });

    /**
     * Allows alerts (flash messages) to be manually dismissed.
     */
    document.querySelectorAll(".close-flash").forEach(function(button) {
        button.addEventListener("click", function(event) {
            event.preventDefault();
            const flashMessage = button.closest(".flash-message");
            if(flashMessage) {
                flashMessage.style.transition = "opacity 0.6s ease";
                flashMessage.style.opacity = "0";
                setTimeout(function() {
                    flashMessage.remove();
                }, 600);
            }
        });
    });

    /**
     * Automatically dismisses alerts (flash messages) after a specified time.
     * @param {number} timeout - Time in milliseconds before auto-dismissal.
     */
    document.querySelectorAll(".flash-message").forEach(function(message) {
        setTimeout(function() {
            message.style.transition = "opacity 0.6s ease";
            message.style.opacity = "0";
            setTimeout(function() {
                message.remove();
            }, 600);
        }, 3000);
    });
});

/**
 * Function to enable or disable delete account buttons with tooltip management.
 */
function updateDeleteButtonsState() {
    const forms = document.querySelectorAll(".delete-account-form");
    forms.forEach(function(form, index) {
        const passwordInput = form.querySelector(".delete-password-input");
        const deleteButton = form.querySelector(".delete-account-button");
        if (passwordInput && deleteButton) {
            const shouldDisable = passwordInput.value.trim() === "";
            console.log(`Form ${index + 1}: Password is ${shouldDisable ? 'empty' : 'filled'}.`);

            // Enable or disable the button based on password input
            deleteButton.disabled = shouldDisable;
            deleteButton.classList.toggle('disabled', shouldDisable);
            console.log(`Form ${index + 1}: Delete button is now ${shouldDisable ? 'disabled' : 'enabled'}.`);

            // Access the tooltip container (parent of the button)
            const tooltipContainer = deleteButton.parentElement;
            if (shouldDisable) {
                // Add tooltip explanation
                tooltipContainer.setAttribute('data-tooltip', 'Please enter your password to delete your account.');
                deleteButton.setAttribute('aria-disabled', 'true');
                console.log(`Form ${index + 1}: Tooltip added.`);
                
                // Remove modal-trigger class to prevent modal from opening
                deleteButton.classList.remove('modal-trigger');
                console.log(`Form ${index + 1}: modal-trigger class removed.`);
            } else {
                // Remove tooltip explanation
                tooltipContainer.removeAttribute('data-tooltip');
                deleteButton.removeAttribute('aria-disabled');
                console.log(`Form ${index + 1}: Tooltip removed.`);
                
                // Add modal-trigger class to enable modal
                deleteButton.classList.add('modal-trigger');
                console.log(`Form ${index + 1}: modal-trigger class added.`);
            }
        } else {
            console.log(`Form ${index + 1}: Missing password input or delete button.`);
        }
    });
}

// Initial state check with delay for autofill
setTimeout(() => {
    console.log("Initial state check after delay.");
    updateDeleteButtonsState();
}, 1000);

// Event listeners for input and change events on password fields
document.body.addEventListener("input", function(event) {
    if (event.target.classList.contains("delete-password-input")) {
        console.log("Password input detected change (input event).");
        updateDeleteButtonsState();
    }
});

document.body.addEventListener("change", function(event) {
    if (event.target.classList.contains("delete-password-input")) {
        console.log("Password input detected change (change event).");
        updateDeleteButtonsState();
    }
});

// Initialize the state of all delete buttons on page load
updateDeleteButtonsState();

/**
 * Handles reCAPTCHA submission and disables the submit button.
 * @param {string} token - The reCAPTCHA token.
 */
function onSubmit(token) {
    const submitButton = document.getElementById("submitButton");
    if(submitButton) {
        submitButton.disabled = true;
    }
    document.getElementById("contact-form").submit();
}

/**
 * Marks images for deletion and shows the file input for uploading a new image.
 * @param {Event} event - The click event.
 */
document.addEventListener("click", function(event) {
    if(event.target.classList.contains("delete_image_button")) {
        const stageNum = event.target.getAttribute("data-stage-num");
        const imageContainer = document.getElementById("image_container_" + stageNum);
        const fileInputContainer = document.getElementById("file_input_container_" + stageNum);
        if(imageContainer) {
            imageContainer.style.display = "none";
        }
        if(fileInputContainer) {
            fileInputContainer.style.display = "block";
        }
        const deleteInput = document.querySelector('input[name="delete_image_' + stageNum + '"]');
        if(deleteInput) {
            deleteInput.value = "true";
        }
    }
});

/**
 * Shows existing image if the user cancels the deletion.
 * @param {Event} event - The click event.
 */
document.addEventListener("click", function(event) {
    if(event.target.classList.contains("cancel_replace_button")) {
        const stageNum = event.target.getAttribute("data-stage-num");
        const imageContainer = document.getElementById("image_container_" + stageNum);
        const fileInputContainer = document.getElementById("file_input_container_" + stageNum);
        if(imageContainer) {
            imageContainer.style.display = "block";
        }
        if(fileInputContainer) {
            fileInputContainer.style.display = "none";
        }
        const deleteInput = document.querySelector('input[name="delete_image_' + stageNum + '"]');
        if(deleteInput) {
            deleteInput.value = "false";
        }
    }
});
