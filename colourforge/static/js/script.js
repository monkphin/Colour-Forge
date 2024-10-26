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
	var elems = document.querySelectorAll(".collapsible");
	var instances = M.Collapsible.init(elems, {
		/**
		 * Event handler when a collapsible item is opening.
		 * @param {Element} el - The collapsible item element that is opening.
		 */
		onOpenStart: function(el) {
			var header = el.querySelector(".collapsible-header");
			if(header) {
				var icon = header.querySelector(".toggle-icon");
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
			var header = el.querySelector(".collapsible-header");
			if(header) {
				var icon = header.querySelector(".toggle-icon");
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
		var firstStageIcon = firstStageHeader.querySelector(".toggle-icon");
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
		opacity: 0.5,
		inDuration: 300,
		outDuration: 200,
	});
	/**
	 * Initializes the Materialize Dropdown component for dropdown menus.
	 */
	var dropdownElems = document.querySelectorAll(".dropdown-trigger");
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
	var forms = document.querySelectorAll("form");
	forms.forEach(function(form) {
		// Skip the login and Register Forms
		if(form.id === "loginForm" || form.id === "registrationForm") {
			return;
		}
		form.addEventListener("keydown", function(event) {
			// Check if the form contains a search input element
			var containsSearchInput = form.querySelector("input[type='search']") !== null;
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
				var submitButton = form.querySelector("button[type='submit']");
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
});
/**
 * Handles reCAPTCHA submission and disables the submit button.
 * @param {string} token - The reCAPTCHA token.
 */
function onSubmit(token) {
	var submitButton = document.getElementById("submitButton");
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
/**
 * Handles the Awesomplete tag suggestion and autocomplete functionality.
 */
document.addEventListener("DOMContentLoaded", function() {
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
		})
	}
});
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