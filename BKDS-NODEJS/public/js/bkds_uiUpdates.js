/*********************************
 * UI Update Module
 * This module handles updates to user interface components.
 *********************************/

/*********************************
 * Left Column Updates
 *********************************/

/**
 * Updates the left column with keywords based on the provided data category.
 *
 * @param {string} dataCategory - The category for which to update keywords.
 */
async function updateLeftColumnWithKeywords(dataCategory) {
  //console.log(`updateLeftColumnWithKeywords() with:`, dataCategory);

  try {
    const response = await fetch(globalEndpoints.updateLeftColumnKeywords, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({ dataCategory }),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch left column or filter summary content`);
    }
  } catch (error) {
    console.error(`Error updating left column and filter summary with keywords:`, error);
  }
}

/**
 * Updates the left column with insights.
 *
 * @param {Array} insights - The insights data to update.
 */
async function updateLeftColumn(insights) {
  //console.log("updateLeftColumn()");

  try {
    const response = await fetch(globalEndpoints.updateLeftColumn, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ insights }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch left column insights");
    }

    const html = await response.text();

    const summaryContent = document.querySelector(`.${globalClasses.summaryContent}`);
    if (summaryContent) {
      summaryContent.innerHTML = html;
      summaryContent.classList.add(globalAttributes.activeStatus);
    }

    const leftColumnContent = document.querySelector(`.${globalClasses.leftColumnDefault}`);
    if (leftColumnContent) {
      leftColumnContent.classList.add(globalAttributes.activeStatus);
    }

    const leftColumn = document.querySelector(`.${globalClasses.leftColumn}`);
    if (leftColumn) {
      leftColumn.classList.add(globalAttributes.activeStatus);
    }
  } catch (error) {
    console.error("Error updating left column:", error);
  }
}

/**
 * Updates the left column with detailed information.
 *
 * @param {string} dataTitle - The title of the data.
 * @param {string} dataCategory - The category of the data.
 * @param {string} dataSubject - The subject of the data.
 * @param {string} imgDesc1 - Image description 1.
 * @param {string} imgDesc2 - Image description 2.
 * @param {string} imgSrc - Image source URL.
 */
async function updateLeftColumnWithDetails(
  dataTitle,
  dataCategory,
  dataSubject,
  imgDesc1,
  imgDesc2,
  imgSrc
) {
  //console.log("updateLeftColumnWithDetails()", dataCategory);

  try {
    const response = await fetch(globalEndpoints.updateLeftColumnDetails, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        dataTitle,
        dataCategory,
        dataSubject,
        imgDesc1,
        imgDesc2,
        imgSrc,
      }),
    });

    if (!response.ok) {
      console.error("Failed to fetch left column details:", response.statusText);
      return;
    }

    const html = await response.text();
    const leftColumn = document.querySelector(`.${globalClasses.photoGridDetails}`);

    if (leftColumn) {
      leftColumn.innerHTML = html;
      leftColumn.classList.add(globalAttributes.activeStatus);
    }
  } catch (error) {
    console.error("Error updating left column with details:", error);
  }
}

/*********************************
 * Thumbnail and View Updates
 *********************************/

/**
 * Updates the active thumbnail by toggling the active class.
 *
 * @param {HTMLElement} selectedThumbnail - The thumbnail element that was selected.
 * @param {string} [parentClass=globalClasses.desktopControlIcon] - The parent class of thumbnails.
 * @param {string} [thumbnailStyle=globalClasses.currentGalleryStyle] - The class indicating the active thumbnail.
 */function updateActiveThumbnail(
  selectedThumbnail,
  parentClass = globalClasses.desktopControlIcon
) {
  if (!selectedThumbnail || !parentClass) {
    console.warn("Invalid selectedThumbnail or parentClass.");
    return;
  }

  console.log("updateActiveThumbnail - Selected thumbnail:", selectedThumbnail);
  console.log("updateActiveThumbnail - Dataset:", selectedThumbnail.dataset);

  // Define mapping of attributes to styles
  const styleMapping = {
    "data-img-filter-gallery-highight": globalClasses.filterSummaryActiveStyle,
    "data-desktop-filter-gallery-highight": globalClasses.currentGalleryStyle,
    "data-tts-option-gallery-highight": globalClasses.ttsActiveStyle,
    "data-related-topic-highight": globalClasses.relatedTopicActiveStyle,
  };

  // Determine which style to apply based on attributes
  let thumbnailStyle = null;

  for (const [attribute, style] of Object.entries(styleMapping)) {
    if (selectedThumbnail.getAttribute(attribute) !== null) {
      thumbnailStyle = style;
      break;
    }
  }

  if (thumbnailStyle) {
    const hasActiveStyle = selectedThumbnail.classList.contains(thumbnailStyle);

    // If it has the style and the filterCategory is NOT "voice_search_general", remove it
    if (hasActiveStyle && selectedThumbnail.dataset.filterCategory !== "voice_search_general") {
      selectedThumbnail.classList.remove(thumbnailStyle);
      console.log("updateActiveThumbnail: Removed active thumbnail style from selected thumbnail.");
    } else {
      // Remove all styles from other thumbnails within the parent class
      const thumbnails = document.querySelectorAll(`.${parentClass}`);
      thumbnails.forEach((thumb) => thumb.classList.remove(...Object.values(styleMapping)));
      console.log("updateActiveThumbnail: Removed active styles from other thumbnails.");

      // Apply the determined style to the selected thumbnail
      selectedThumbnail.classList.add(thumbnailStyle);
      console.log("updateActiveThumbnail: Added active style to selected thumbnail.");
    }
  } else {
    console.log("No applicable style found for the selected thumbnail.");
  }

  // Update the last clicked icon reference
  lastClickedIconDIV = selectedThumbnail;
}



/**
 * Resets the application view based on the specified mode.
 *
 * Modes:
 * - "full": Redirects to the homepage.
 * - "main": Resets key content areas.
 *
 * @param {string} mode - Mode to reset view ("full" or "main").
 */
async function resetView(mode) {
  console.log(`resetView() - Start with mode:`, mode);

  const photoGalleryModal = document.getElementById(globalClasses.photoGalleryModal); // Adjust ID if necessary

  const isModalActive = photoGalleryModal?.classList.contains(globalAttributes.activeStatus);
  //console.log(`resetView()1 - isModalActive:`, isModalActive);

  if (isModalActive) {
    console.log(`resetView()2 - isModalActive:`, isModalActive);
    //console.log("Photo gallery modal is active. Closing modal...");
    photoGalleryModal.classList.remove(globalAttributes.activeStatus);

    // Additional cleanup if needed
    // For example: Clear modal content or reset other modal-related states
    return;
  }

  if(mode === "speech"){
    console.log(`resetView mode`, mode);

    window.location.href = globalAttributes.speechRecService; // Redirect to the home page
    return;

  }

  if (mode === "full") {
    window.location.href = globalAttributes.homeEndPoint; // Redirect to the home page
    return;
  }

  if (mode === "main") {
    try {
      const elements = getElements();

      // Fetch and parse default content
      await fetchContent(globalEndpoints.refreshContent);

      // Reset the main feed and other components
      filterMainFeed('main_feed');  

      const isPhotoCategoryActive = lastClickedIconID === 'photos';

      if (isPhotoCategoryActive) {
        resetContent([
          elements.leftColumnDefaultContent,
          elements.filterSummary,
          elements.imageGridContainer,
          elements.mainToolbar,
          elements.leftColumn,
          elements.photoGridContainer,
          elements.middleColumn,
          elements.mainFeedContent,
          elements.leftColumnDefault,
        ]);
      } else {
        elements.summaryContent.classList.remove(globalAttributes.activeStatus);
        elements.leftColumnDefault.classList.remove(globalAttributes.activeStatus);
        elements.mainFeedContent.classList.remove(globalAttributes.activeStatus);
      }
    } catch (error) {
      console.error("Failed to reset view:", error);
      const elements = getElements();
      showErrorMessages(elements.leftColumn, elements.mainFeedContent, elements.mainToolbar);
    }
  } else {
    console.warn(`resetView() - Unrecognized mode: '${mode}'`);
  }
}

/**
 * Retrieves DOM elements used in the resetView function.
 *
 * @returns {Object} - An object containing references to various DOM elements.
 */
function getElements() {
  return {
    leftColumnDefaultContent: document.getElementById(globalClasses.leftColumnDefaultContent),
    leftColumnDefault: document.querySelector(`.${globalClasses.leftColumnDefault}`),
    leftColumn: document.querySelector(`.${globalClasses.leftColumn}`),
    middleColumn: document.querySelector(`.${globalClasses.middleColumn}`),
    mainFeedContent: document.querySelector(`.${globalClasses.mainFeedContent}`),
    filterSummary: document.querySelector(`.${globalClasses.filterSummaryContent}`),
    imageGridContainer: document.querySelector(`.${globalClasses.imageGridContainer}`),
    photoGridContainer: document.querySelector(`.${globalClasses.photoGridContainer}`),
    mainToolbar: document.getElementById(globalClasses.mainFeedToolbarContainer),
    summaryContent: document.querySelector(`.${globalClasses.summaryContent}`),
  };
}

/**
 * Fetches content from a specified endpoint.
 *
 * @param {string} endpoint - The URL to fetch content from.
 * @returns {Promise<string>} - A promise that resolves to the fetched content.
 */
async function fetchContent(endpoint) {
  const response = await fetch(endpoint, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
  });
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
  }
  return response.text();
}

/**
 * Resets specified elements by toggling the active status.
 *
 * @param {HTMLElement[]} elementsToReset - Array of elements to reset.
 */
function resetContent(elementsToReset) {
  //console.log("resetContent() - Resetting elements.");

  elementsToReset.forEach((element) => {
    if (element) {
      element.classList.toggle(globalAttributes.activeStatus);
    }
  });
}

/**
 * Displays error messages for critical UI sections.
 *
 * @param {HTMLElement} leftColumn - The left column element.
 * @param {HTMLElement} mainFeedContent - The main feed content element.
 * @param {HTMLElement} mainToolbar - The main toolbar element.
 */
function showErrorMessages(leftColumn, mainFeedContent, mainToolbar) {
  if (leftColumn) {
    leftColumn.innerHTML = "<p>Error loading left column. Please try again.</p>";
  }
  if (mainFeedContent) {
    mainFeedContent.innerHTML = "<p>Error loading main feed. Please try again.</p>";
  }
  if (mainToolbar) {
    mainToolbar.innerHTML = "<p>Error loading toolbar. Please try again.</p>";
  }
}

/**
 * Updates the toolbar with dynamic search URLs.
 */
function updateToolBar(containerClass, iconClass) {
  //console.log("updateToolBar()");
  ////console.log("updateToolBar() containerClass", containerClass);
  ////console.log("updateToolBar() iconClass", iconClass);

  const toolbarHeader = document.getElementById(containerClass);
  if (!toolbarHeader) {
    console.error("Toolbar container not found.");
    return;
  }

  const filterIcons = toolbarHeader.querySelectorAll(`.${iconClass}`);

  filterIcons.forEach((icon) => {
    let url = icon.getAttribute(globalAttributes.href);

    if (!url) {
      console.warn("Icon does not have a href attribute:", icon);
      return;
    }

    // Determine the appropriate search pool
    let searchPool = [...globalSearches.generalSearches];
    const urlIncludes = (str) => url.includes(str);

    if (urlIncludes("earth.google") || urlIncludes("google.com/earth")) {
      searchPool.push(...globalSearches.earthSearches);
    } else if (urlIncludes("maps.google") || urlIncludes("google.com/maps")) {
      searchPool.push(...globalSearches.mapsSearches);
    } else if (urlIncludes("wikimedia") || urlIncludes("wikipedia")) {
      searchPool.push(...globalSearches.wikimediaSearches);
    } else if (urlIncludes("youtube")) {
      searchPool.push(...globalSearches.youtubeSearches);
    }

    const filterCategory = icon.getAttribute(globalAttributes.dataFilterCategory) || '';
    const shouldUseRandomString =
      searchPool.length > 0 &&
      (filterCategory.includes("_general") ||
        filterCategory.includes("_default") ||
        urlIncludes("wikimedia") ||
        urlIncludes("wikipedia") ||
        urlIncludes("google.com/images") ||
        urlIncludes("images.google.com") ||
        (url.startsWith("https://youtube") && new Date().getMinutes() % 2 !== 0));

    if (shouldUseRandomString) {
      const randomString = searchPool[Math.floor(Math.random() * searchPool.length)];
      url = url.replace(globalAttributes.searchTermReplace, encodeURIComponent(randomString));
      icon.setAttribute(globalAttributes.href, url);
      ////console.log(`Updated URL for icon with random search: ${randomString}`);
    } else {
      url = url.split("/search")[0];
      icon.setAttribute(globalAttributes.href, url);
      //console.log(`Set default URL for icon: ${url}`);
    }
  });
}

/*********************************
 * Scroll Handling
 *********************************/

/**
 * Handles infinite scrolling by fetching more content when the user scrolls near the bottom.
 */
let isFetchingMap = new Map();
let currentPageMap = new Map();
function handleScroll(scrollableElement) {
  if (!scrollableElement) {
    console.error("Scrollable element not provided.");
    return;
  }

  // Check if the element is the active scrollable element
  if (scrollableElement.getAttribute('data-focus') !== 'true') {
    return; // Do not proceed if it's not the active element
  }

  const elementId = scrollableElement.id || scrollableElement.className;  

  if (!isFetchingMap.has(elementId)) {
    isFetchingMap.set(elementId, false);
    currentPageMap.set(elementId, 1);
  }

  const isFetching = isFetchingMap.get(elementId);
  let currentPage = currentPageMap.get(elementId);

  let currentFilter = "main_feed"; // Default filter

  // Determine the current filter based on active elements
  const option2Filter = document.querySelector(
    `.${globalClasses.filterSummaryContentItem}.${globalClasses.filterSummaryActiveStyle}`
  );
  const option1Filter = document.querySelector(
    `.${globalClasses.desktopControlIcon}.${globalClasses.currentGalleryStyle}`
  );
  const option0Filter = document.querySelector(`.${globalClasses.photoCategory}`);

  if (option2Filter) {
    currentFilter = option2Filter.dataset.filterCategory;
  } else if (option0Filter?.classList.contains(globalClasses.currentGalleryStyle)) {
    currentFilter = option0Filter.dataset.filterCategory;
  } else if (option1Filter) {
    currentFilter = option1Filter.dataset.filterCategory;
  }

  const scrollPosition = scrollableElement.scrollTop + scrollableElement.clientHeight;
  const threshold = scrollableElement.scrollHeight - scrollableElement.clientHeight * 2;

  if (scrollPosition > threshold && !isFetching) {
    isFetchingMap.set(elementId, true);
    fetchAndScrollInsights(scrollableElement, currentFilter, currentPage, pageSize)
      .then(() => {
        isFetchingMap.set(elementId, false);
        currentPage++;
        currentPageMap.set(elementId, currentPage);
      })
      .catch((error) => {
        console.error("Error fetching more data:", error);
        isFetchingMap.set(elementId, false);
      });
  }
}
