/*********************************
 * Data Fetching and Rendering
 *********************************/

/**
 * Fetches the image grid based on the target's filter category and updates the DOM.
 *
 * @param {HTMLElement} target - The element that triggered the action.
 */
async function filterImageGrid(target) {
  //console.log('filterImageGrid() - Start', target);

  // Determine filterCategory based on whether the same icon was clicked
  const iconId = target.id;
  const isSameIconClicked = lastClickedIconID === iconId;
  let filterCategory = target.getAttribute(globalAttributes.dataFilterCategory);

  // If the same icon is clicked, override with photoType
  filterCategory = isSameIconClicked
    ? globalAttributes.photoType
    : filterCategory || globalAttributes.photoType;

  // Set default values for pagination
  const page = target.getAttribute(globalAttributes.dataPage) || 1;
  const limit = globalAttributes.dataLimit || 40;

  // Construct the endpoint URL for fetching the image grid
  const endpoint = `${globalEndpoints.imageGrid}?type=${filterCategory}&page=${page}&limit=${limit}`;
  //console.log(`filterImageGrid() - Fetching image grid from: ${endpoint}`);

  try {
    const response = await fetch(endpoint, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    });

    if (!response.ok) {
      throw new Error(
        `filterImageGrid() - Failed to load image grid. Status: ${response.status} ${response.statusText}`
      );
    }

    const html = await response.text();

    // Update the last clicked icon information
    lastClickedIconID = iconId;
    lastClickedIconDIV = target;

    // Update the DOM with the new image grid content
    const imageGridContainer = document.getElementById(globalClasses.imageGridContainer);

    if (imageGridContainer) {
      imageGridContainer.innerHTML = html;
      //console.log('filterImageGrid() - Image grid successfully updated');
    } else {
      console.warn('filterImageGrid() - imageGridContainer not found.');
    }
  } catch (error) {
    console.error('filterImageGrid() - Error fetching image grid:', error);

    // Display an error message to the user
    const errorMessage = document.createElement('div');
    errorMessage.className = 'error-message';
    errorMessage.textContent =
      'An error occurred while loading images. Please try again later.';

    const imageGridContainer = document.getElementById(globalClasses.imageGridContainer);
    if (imageGridContainer) {
      imageGridContainer.innerHTML = '';
      imageGridContainer.appendChild(errorMessage);
    }

    // Reset the last clicked icon information
    lastClickedIconID = null;
    lastClickedIconDIV = null;
  } finally {
    //console.log('filterImageGrid() - End');
  }
}

/**
 * Fetches and renders insights or image grid into the container element.
 *
 * @param {HTMLElement} containerElement - The element to render content into.
 * @param {string} filterCategory - The filter category to fetch data for.
 * @param {number} page - The page number for pagination.
 * @param {number} limit - The number of items per page.
 */
async function fetchAndRenderInsights(containerElement, filterCategory, page, limit) {
  const functionName = fetchAndRenderInsights.name;
  //console.log(`${functionName} - Start`);

  // Determine if we are loading photo grid or insights based on the filter category
  const isPhotoCategory = filterCategory === globalAttributes.photoType ||
                          document.querySelector('.filter-summary-active-style') !== null;
  
  //console.log(`${functionName} - filterCategory`, filterCategory)
  //console.log(`${functionName} - isPhotoCategory`, isPhotoCategory);

  // Construct endpoint based on category type
  const endpoint = isPhotoCategory
    ? `${globalEndpoints.imageGrid}?type=${filterCategory}&page=${page}&limit=${limit}`
    : `${globalEndpoints.fetchAllInsights}?filterCategory=${filterCategory}&page=${page}&limit=${limit}`;

  // Set default container if none is provided

  const defaultSelector = isPhotoCategory ? `.${globalClasses.imageGridContainer}` : `.${globalClasses.mainFeedContent}`;
  containerElement = document.querySelector(defaultSelector);

  ////console.log(`${functionName} - containerElement`, containerElement);

  try {
    const html = await fetchContent(endpoint, functionName);

    if (containerElement) {
      if (isPhotoCategory) {
        containerElement.insertAdjacentHTML('beforeend', html); // Efficiently append
      } else {
        containerElement.innerHTML = html; // Replace content for insights
      }
      //console.log(`${functionName} - Content successfully rendered`);
    } else {
      console.warn(`${functionName} - Container element is null or undefined`);
    }
  } catch (error) {
    handleFetchError(containerElement, error);
  } finally {
    //console.log(`${functionName} - End`);
  }
}

/**
 * Helper function to fetch HTML content from the server.
 *
 * @param {string} url - The URL endpoint to fetch content from.
 * @param {string} functionName - Name of the calling function for logging purposes.
 * @returns {Promise<string>} - The fetched HTML content.
 */
async function fetchContent(url, functionName) {
  //console.log(`${functionName} - Fetching content from: ${url}`);
  const response = await fetch(url, {
    headers: { "X-Requested-With": "XMLHttpRequest" }
  });

  if (!response.ok) {
    throw new Error(`${functionName} - Failed to fetch content: ${response.status} ${response.statusText}`);
  }
  return response.text();
}

/**
 * Handles fetch errors by displaying an error message in the container element.
 *
 * @param {HTMLElement} containerElement - The element to display the error message in.
 * @param {Error} error - The error object.
 */
function handleFetchError(containerElement, error) {
  console.error('Error fetching data:', error);

  const errorMessage = document.createElement('div');
  errorMessage.className = 'error-message';
  errorMessage.textContent = 'An error occurred while loading content. Please try again later.';

  if (containerElement) {
    containerElement.innerHTML = '';
    containerElement.appendChild(errorMessage);
  }
}


/**
 * Fetches more insights for infinite scrolling and appends them to the main feed container.
 *
 * @param {HTMLElement} mainFeedContainer - The main feed container element.
 * @param {string} filterCategory - The filter category to fetch data for.
 * @param {number} page - The page number for pagination.
 * @param {number} limit - The number of items per page.
 */
async function fetchAndScrollInsights(
  mainFeedContainer,
  filterCategory = globalClasses.mainFeedFilterCategory,
  page,
  limit
) {
  //console.log('fetchAndScrollInsights() - Start. Filter Category:', filterCategory);

  try {
    const filterSummaryActive = document.querySelector('.filter-summary-active-style');

    if (filterCategory === 'photos' || filterSummaryActive) {
      // If filterCategory is 'photos', use fetchAndRenderInsights instead
      await fetchAndRenderInsights(mainFeedContainer, filterCategory, page, limit);
      return; // Exit the function after calling fetchAndRenderInsights
    }

    // Fetch insights for scrolling
    const endpoint = `${globalEndpoints.fetchAllInsights}?filterCategory=${filterCategory}&page=${page}&limit=${limit}`;
    //console.log(`fetchAndScrollInsights() - Fetching insights: ${endpoint}`);

    const response = await fetch(endpoint, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    });

    if (!response.ok) {
      throw new Error(
        `fetchAndScrollInsights() - Failed to fetch insights. Status: ${response.status} ${response.statusText}`
      );
    }

    const html = await response.text();
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    while (tempDiv.firstChild) {
      mainFeedContainer.appendChild(tempDiv.firstChild);
    }
  } catch (error) {
    console.error('fetchAndScrollInsights() - Error fetching more data:', error);
  }
}

/**
 * Filters the main feed based on the given filter category.
 *
 * @param {string} filterCategory - The filter category to filter the main feed.
 */
async function filterMainFeed(filterCategory) {
  //console.log('filterMainFeed() - Start. Filter Category:', filterCategory);

  const currentPage = 1;
  const limit = pageSize; // Ensure 'pageSize' is defined in your scope

  let summaryContent = document.querySelector(`.${globalClasses.summaryContent}`);
  let leftColumnContent = document.querySelector(`.${globalClasses.leftColumnDefault}`);
  let homeDefault = document.querySelector(`.${globalClasses.homeDefault}`);
  let mainFeedContent = document.querySelector(`.${globalClasses.middleColumn}`);

  try {
    if (filterCategory === 'photos') {
      // For 'photos', skip fetching insights JSON data and updating left column
      //console.log('filterMainFeed() - Filter category is "photos", fetching image grid.');

      // Clear or hide left column content
      if (summaryContent) {
        summaryContent.innerHTML = '';
      }
      if (leftColumnContent) {
        leftColumnContent.classList.add(globalAttributes.activeStatus);
      }
      if (homeDefault) {
        homeDefault.classList.add(globalAttributes.activeStatus);
      }

      // Fetch and render image grid for the main feed
      mainFeedContent = document.querySelector(`.${globalClasses.photoGridContainer}`) || mainFeedContent;
      await filterImageGrid(mainFeedContent);
    } else {
      // Fetch insights JSON data
      const dataCategoryLimit = 50;
      const jsonEndpoint = `${globalEndpoints.fetchInsightsJson}?filterCategory=${filterCategory}&page=${currentPage}&limit=${dataCategoryLimit}`;
      //console.log(`filterMainFeed() - Fetching insights JSON data from: ${jsonEndpoint}`);

      const jsonResponse = await fetch(jsonEndpoint, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      });

      if (!jsonResponse.ok) {
        throw new Error(
          `filterMainFeed() - Failed to fetch insights JSON data. Status: ${jsonResponse.status} ${jsonResponse.statusText}`
        );
      }

      const data = await jsonResponse.json();
      const insights = data.insights;

      // Send POST request to update left column
      const updateLeftColumnEndpoint = globalEndpoints.updateLeftColumn;
      //console.log(`filterMainFeed() - Posting insights data to: ${updateLeftColumnEndpoint}`);

      const response = await fetch(updateLeftColumnEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ insights }), // Pass insights in the request body
      });

      if (!response.ok) {
        throw new Error(
          `filterMainFeed() - Failed to update left column insights. Status: ${response.status} ${response.statusText}`
        );
      }

      const html = await response.text();

      // Update left column content
      if (leftColumnContent && summaryContent && html) {
        //console.log('filterMainFeed() - Updating left column content.');
        summaryContent.innerHTML = html;

        // Fetch and render insights for the main feed
        mainFeedContent = document.querySelector(`.${globalClasses.mainFeedContent}`) || mainFeedContent;

        await fetchAndRenderInsights(mainFeedContent, filterCategory, currentPage, limit);

        //console.log('filterMainFeed() - Left column content updated successfully.');
      } else {
        console.warn('filterMainFeed() - Could not find left column elements or HTML is empty.');
      }
    }
  } catch (error) {
    console.error('filterMainFeed() - Error occurred:', error);

    // Display an error message to the user
    const errorMessage = document.createElement('div');
    errorMessage.className = 'error-message';
    errorMessage.textContent =
      'An error occurred while loading content. Please try again later.';

    // Update summary content
    if (summaryContent) {
      summaryContent.innerHTML = '';
      summaryContent.appendChild(errorMessage.cloneNode(true));
    }

    // Update main feed content
    if (mainFeedContent) {
      mainFeedContent.innerHTML = '';
      mainFeedContent.appendChild(errorMessage);
    }
  } finally {
    //console.log('filterMainFeed() - End.');
  }
  fadeInContainers();
}
