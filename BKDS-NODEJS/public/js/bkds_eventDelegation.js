/*********************************
 * Event Initialization and Handlers
 *********************************/

// Initialize event handlers when the DOM content is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing event handlers");
  initializeEventHandlers();
  updateToolBar(globalClasses.mainFeedToolbarContainer, globalClasses.desktopSearchSpeechResult);
  fadeInContainers();

    // Attach scroll listeners to middleColumn and imageGrid
  const middleColumn = document.getElementById('middle-column');
  const imageGrid = document.querySelector('.image-grid');

  attachScrollListener(middleColumn);
  attachScrollListener(imageGrid);
});


/**
 * Sets up initial event listeners for click and scroll events.
 */
function initializeEventHandlers() {
  console.log("initializeEventHandlers()");

  document.addEventListener("click", handleDelegatedClick);
}


function attachScrollListener(element) {
  if (element) {
    element.addEventListener('scroll', () => handleScroll(element));
  }
}



/**
 * Sets up initial event listeners for click and scroll events.
 */
/**
 * Handles keyboard navigation for scrolling and gallery controls.
 */
// JavaScript code to attach keyboard event listeners to the document
document.addEventListener('keydown', function (event) {
  switch (event.key) {
    case "ArrowUp":
      scrollActiveElement(-100);
      break;
    case "ArrowDown":
      scrollActiveElement(100);
      break;
    default:
      // Handle other keys like ArrowLeft, ArrowRight, or 'f'
      handleNavigationKeys(event);
      break;
  }
});

function handleNavigationKeys(event) {
  const prevButton = document.getElementById("prev");
  const nextButton = document.getElementById("next");
  const fullscreenButton = document.getElementById("expand");

  switch (event.key) {
    case "ArrowLeft":
      if (prevButton) prevButton.click();
      break;
    case "ArrowRight":
      if (nextButton) nextButton.click();
      break;
    case "f":
    case "F":
      if (fullscreenButton) fullscreenButton.click();
      break;
  }
}
function scrollActiveElement(scrollAmount) {
  // Determine which element to scroll
  const imageGrid = document.querySelector('.image-grid');
  const insightLeft = document.querySelector('.insight-left');
  const middleColumn = document.getElementById('middle-column');

  let elementToScroll = null;

  if (isElementVisible(imageGrid)) {
    elementToScroll = imageGrid;
    
  } else if (isElementVisible(insightLeft)) {
    // Target the specific element within .insight-left
    const insightText = insightLeft.querySelector('.insight-extract-text');
    if (insightText && isElementScrollable(insightText)) {
      elementToScroll = insightText;
    } else {
      elementToScroll = insightLeft;
    }
  } else if (isElementVisible(middleColumn)) {
    elementToScroll = middleColumn;
  }

  if (elementToScroll) {
    elementToScroll.scrollBy({
      top: scrollAmount,
      behavior: 'smooth',
    });
  }
}

// Helper function to check if an element is scrollable
function isElementScrollable(el) {
  return el.scrollHeight > el.clientHeight;
}

// Helper function to check if an element is visible
function isElementVisible(el) {
  return el && el.offsetParent !== null;
}



// Function to check if the Photos category is active
function isPhotoCategoryActive() {
  // Select the element with id="photo-gallery-filters"
  const photoGalleryFilters = document.querySelector('.photo-gallery-filters');
  
  // Determine if the element exists and has the 'active' class
  const isActive = photoGalleryFilters !== null && photoGalleryFilters.classList.contains('active');
  
  return isActive;
}


function isSpeechActive() {
  console.log("isSpeechActive");

  // Check for active speech recognition instance
  const activeInstance = window.recognitionInstance;

  // Check for the presence of the 'photo-search-body' element in the DOM
  const photoSearchBody = document.querySelector('.photo-search-body');

  // Speech is active if there is an active recognition instance or the element exists
  return !!activeInstance || !!photoSearchBody;
}




/*********************************
 * Event Delegation and Processing
 *********************************/

/**
 * Filter changes should end any active speech synth or recognition
 *
 */
function stopAllSpeechServices() {
  // Stop speech recognition
  if (typeof stopSpeechRecognitionService === 'function') {
    stopSpeechRecognitionService();
    console.log("Speech recognition stopped.");

    const iconsContainer = document.querySelector(".toolbar-icon-grid-container")
    const icons = iconsContainer.querySelectorAll(".desktop_search_speech_result")
  
    icons.forEach((icon) => {
      icon.classList.remove("seach_result_pulsate");
    })
    console.log("Speech recognition animations stopped.");

  }

  // Stop speech synthesis
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
    console.log("Speech synthesis canceled.");
  }
}

function scrollActiveElement(scrollAmount) {
  const focusedElement = document.querySelector('[data-focus="true"]');

  if (focusedElement && isElementScrollable(focusedElement)) {
    focusedElement.scrollBy({
      top: scrollAmount,
      behavior: 'smooth',
    });
  }
}

// Helper function to check if an element is scrollable
function isElementScrollable(el) {
  return el.scrollHeight > el.clientHeight;
}

/**
 * Handles delegated click events and dispatches actions based on the clicked element.
 *
 * @param {Event} event - The click event object.
 */
function handleDelegatedClick(event) {
  console.log("handleDelegatedClick()");

  // Stop any ongoing speech recognition service
  stopAllSpeechServices();

  const target = event.target;

  // Retrieve the filter category from the target or its ancestors
  const filterCategory = getFilterCategory(target);
  console.log("handleDelegatedClick() filterCategory", filterCategory);

  // Reset focus for all scrollable elements
  resetScrollableFocus();

  // Update scrollable element based on filter category
  if (filterCategory) {
    if (filterCategory.toLowerCase() === "photos") {
      const imageGrid = document.querySelector('.middle-column');
      if (imageGrid) {
        imageGrid.setAttribute('data-focus', 'true');
      }
    } else {
      const insightLeft = document.querySelector('.insight-left');
      if (insightLeft) {
        insightLeft.setAttribute('data-focus', 'true');
      }
    }
  } else {
    const middleColumn = document.getElementById('middle-column');
    if (middleColumn) {
      middleColumn.setAttribute('data-focus', 'true');
    }
  }

  // Initialize variables
  const { currentClass, classList } = getCurrentClassAndList(target);

  // Update lastDataIndex if data-index attribute is present
  if (target.hasAttribute("data-index")) {
    globalAttributes.lastDataIndex = target.getAttribute("data-index");
  }

  const iconId = target.id;
  const isSameIconClicked = lastClickedIconID === iconId;

  if (filterCategory) {
    // Check if filter summary item is active
    const isFilterSummaryActive =
      document.querySelector(`.${globalClasses.filterSummaryActiveStyle}`) !==
      null;

    const desktopControlIcons = document.querySelectorAll(
      `.${globalClasses.desktopControlIcon}`
    );
    let isDesktopControlIconActive = false;
    for (const icon of desktopControlIcons) {
      if (icon.classList.contains(globalClasses.currentGalleryStyle)) {
        isDesktopControlIconActive = true;
        break; // Exit loop early
      }
    }

    // Get all relevant app elements
    const appElements = getAppElements();

    // Find the closest element in appElements that contains the target
    const closestElement = Array.from(appElements).find((elem) =>
      elem.contains(target)
    );

    if (!closestElement) {
      return;
    }

    lastClickedIconDIV = target; // Save the clicked element for future reference
    updateActiveThumbnail(target, classList, currentClass);

    // Handle different filter categories
    if (
      filterCategory.toLowerCase().includes("home") ||
      (isPhotoCategoryActive() && filterCategory.toLowerCase() === "photos")
    ) {
      resetView("full");
      return;
    }

    if (isSameIconClicked && isDesktopControlIconActive) {
      if (isFilterSummaryActive) {
        filterImageGrid(target);
      } else {
        resetView("main");
      }
      return;
    } else if (
      filterCategory.includes("voice_search") ||
      filterCategory.includes("desktop_search")
    ) {
      console.log("handleDelegatedClick() speechRec", isSpeechActive());
      if (isSpeechActive()) {
        stopSpeechRecognitionService();
      }
      if (isPhotoCategoryActive()) {
        window.location.href = globalAttributes.speechRecService;
      }else{
        handleSpeechRecognitionClick();
      }
      return;
    }
  }

  // Traverse up the DOM tree to find and handle the action
  handleActionFromTarget(target);
}

// Helper function to reset focus for all scrollable elements
function resetScrollableFocus() {
  const scrollableElements = [
    document.getElementById('middle-column'),
    document.querySelector('.image-grid'),
    document.querySelector('.insight-left'),
  ];

  scrollableElements.forEach((el) => {
    if (el) {
      el.setAttribute('data-focus', 'false');
    }
  });
}

/**
 * Routes actions to their respective handlers based on the action type.
 *
 * @param {HTMLElement} target - The element that triggered the action.
 * @param {string} action - The action to handle.
 */
function handleAction(target, action) {
  console.log(`handleAction(): action = ${action}`);

  switch (action) {
    case "openPost":
      handlePostClick(target);
      break;
    case "iconClick":
      handleIconOrFilterClick(target);
      break;
    case "powerControl":
      handlePowerCenterControl(target);
      break;
    case globalAttributes.galleryAction:
    case "openSubjectImage":
      handleGalleryAction(target);
      break;
    case "ttsAction":
      handleTTS(target);
      break;
    case "filterImageGrid":
      console.log("handleAction() filterImageGrid");
      filterImageGrid(target);
      break;
    default:
      console.warn(`No handler for action: ${action}`);
  }

}

/**
 * Traverses up the DOM tree to find and handle the action based on the data-action attribute.
 *
 * @param {HTMLElement} target - The initial event target.
 * @param {HTMLElement} contentContainer - The content container element to scroll.
 */
function handleActionFromTarget(target) {
  console.log("handleActionFromTarget()");

  let currentTarget = target;
  while (currentTarget && currentTarget !== document) {
    const action = currentTarget.dataset.action;
    if (action) {
      // Scroll to the top of the content container
      handleAction(currentTarget, action);
      lastClickedIconID = currentTarget.id; // Save the clicked element for future reference
      return;
    }
    currentTarget = currentTarget.parentElement;
  }
}

/*********************************
 * Power Control
 *********************************/

/**
 * Sends a power action command to the server (e.g., sleep, restart).
 *
 * @param {HTMLElement} target - The element that triggered the power action.
 */
function handlePowerCenterControl(target) {
  console.log("handlePowerCenterControl()");

  // Get the power action from the data attribute or default to 'POWER_SLEEP'
  const powerAction =
    target.dataset.powerAction || globalAttributes.defaultPower;

  console.log(`Power Action: ${powerAction}`);

  // Make a request to the server to execute the script
  fetch(globalEndpoints.executePower, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ powerAction }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Command executed:", data);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function fadeInContainers() {
  const containerParents = document.querySelectorAll(".contentContainer");

  // Loop through each element in the NodeList
  containerParents.forEach((container) => {
    container.addEventListener("animationstart", (e) => {
      if (e.target.matches(".contentContainer")) {
        e.target.classList.add("fade-in");
      }
    });
  });
}