/* =======================================
   Utility Functions
   ======================================= */

/**
 * Removes the _PIL_* part from the filename in a URL.
 *
 * @param {string} url - The URL to process.
 * @returns {string} - The URL without the _PIL_* part.
 */
function removePilPart(url) {
    console.log('removePilPart()', url);
    return url.replace(/_PIL_\d+(\.\w+)$/, '$1');
  }
  
  /**
   * Debounce function to limit the rate at which a function can fire.
   *
   * @param {Function} func - The function to debounce.
   * @param {number} wait - The debounce delay in milliseconds.
   * @returns {Function} - The debounced function.
   */
  function debounce(func, wait, immediate = false) {
    let timeout;
    return function (...args) {
      const context = this;
      const callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        timeout = null;
        if (!immediate) func.apply(context, args);
      }, wait);
      if (callNow) func.apply(context, args);
    };
  }
  
  
  /**
   * Strips the URL to its pathname.
   *
   * @param {string} url - The URL to strip.
   * @returns {string} - The pathname of the URL.
   */
  function stripUrl(url) {
    try {
      const parsedUrl = new URL(url);
      return parsedUrl.pathname;
    } catch (e) {
      return url;
    }
  }
  
  /**
   * Removes specified strings from the input string.
   *
   * @param {string} input - The input string to process.
   * @returns {string} - The processed string.
   */
  function stripStrings(input) {
    console.log('stripStrings()', input);
    const stringsToStrip = ['desktop_search_'];
    let result = input;
    stringsToStrip.forEach((str) => {
      result = result.replace(new RegExp(str, 'g'), '');
      console.log('stripStrings result', result);
    });
    return result;
  }
  
  /**
   * Retrieves the filter category from the target or its ancestors.
   *
   * @param {HTMLElement} target - The initial event target.
   * @returns {string|null} - The filter category if found, otherwise null.
   */
  function getFilterCategory(target) {
    console.log('getFilterCategory()');
    let currentTarget = target;
    while (currentTarget && currentTarget !== document) {
      const filterCategory = currentTarget.dataset.filterCategory;
      if (filterCategory) {
        return filterCategory;
      }
      currentTarget = currentTarget.parentElement;
    }
    return null;
  }
  
  /**
   * Determines the current class and class list based on the target's closest matching ancestor.
   *
   * @param {HTMLElement} target - The initial event target.
   * @returns {Object} - An object containing currentClass and classList.
   */
  function getCurrentClassAndList(target) {
    console.log('getCurrentClassAndList()', target);
    let currentClass = globalClasses.currentGalleryStyle;
    let classList = globalClasses.desktopControlIcon;
  
    if (target.closest(`.${globalClasses.filterSummaryContentItem}`)) {
      currentClass = globalClasses.filterSummaryActiveStyle;
      classList = `${globalClasses.filterSummaryClassList}, ${currentClass}`;
    } else if (target.closest(`.${globalClasses.photoGalleryControl}`)) {
      currentClass = globalClasses.photoControlActiveStyle;
      classList = globalClasses.photoGalleryClassList;
    } else if (target.closest(`.${globalClasses.subjectReader}`)) {
      currentClass = globalClasses.photoControlActiveStyle;
      classList = globalClasses.subjectReaderClassList;
    } else if (target.closest(`.${globalClasses.relatedTopic}`)) {
      currentClass = globalClasses.filterSummaryActiveStyle;
      classList = globalClasses.relatedTopicClassList;
    } else if (target.closest(`.${globalClasses.postContainer}`)) {
      currentClass = globalClasses.filterSummaryActiveStyle;
      classList = globalClasses.postContainerClassList;
    }
  
    return { currentClass, classList };
  }
  
  /**
   * Retrieves all relevant app elements for event delegation.
   *
   * @returns {NodeListOf<Element>} - A list of relevant app elements.
   */
  function getAppElements() {
    console.log('getAppElements()');
    return document.querySelectorAll(
      `.${globalClasses.desktopControlIcon},
       .${globalClasses.toolbarSpeechResult},
       .${globalClasses.postContainer},
       .${globalClasses.relatedTopic},
       .${globalClasses.insightThumbnailImage},
       .${globalClasses.photoGalleryControl},
       .${globalClasses.desktopSearchSpeechResult},
       .${globalClasses.subjectReader},
       .${globalClasses.insightThumbnailGridFullscreen},
       .${globalClasses.filterSummaryContentItem},
       .${globalClasses.galleryFilterOption},
       .${globalClasses.powerCenter},
       .${globalClasses.imageGridItem}`
    );
  }
  