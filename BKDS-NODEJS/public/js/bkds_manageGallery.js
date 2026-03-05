/*********************************
 * Gallery and Image Handling
 *********************************/

/**
 * Manages gallery actions like next, previous, restart, and open image.
 *
 * @param {HTMLElement} target - The element that triggered the gallery action.
 */
function handleGalleryAction(target) {
  //console.log("handleGalleryAction()");
  //console.log("handleGalleryAction() target", target);

  const currentClass = globalClasses.currentGalleryStyle;

  // Determine if the photo gallery modal is active
  const photoGalleryModal = document.querySelector(
    `.${globalClasses.photoGalleryModalContainer}`
  );
  const isModalActive = photoGalleryModal?.classList.contains(
    globalAttributes.activeStatus
  );

  // Get the current thumbnail element
  const currentThumbnailElement = document.querySelector(`.${currentClass}`);
  if (!currentThumbnailElement) {
    console.error("No current thumbnail element found.");
    return;
  }

  // Check if the photo category is active
  const isPhotoCategoryActive = 
    currentThumbnailElement.getAttribute(globalAttributes.dataFilterCategory)?.toLowerCase() === globalClasses.photoCategory;

  // Cache thumbnails container and retrieve all thumbnails only once
  const thumbnailsContainerClass = getThumbnailsContainerClass(isPhotoCategoryActive, isModalActive);
  const thumbnailsContainer = getThumbnailsContainer(thumbnailsContainerClass);

  // Get all thumbnails and convert to an array once
  const thumbnails = Array.from(thumbnailsContainer.querySelectorAll(
    `.${globalClasses.insightThumbnailImage}`
  ));

  // Retrieve gallery action
  const galleryAction = target.getAttribute(globalAttributes.galleryAction);
  if (!galleryAction) {
    console.warn("No galleryAction attribute found on the target element.");
    return;
  }

  // Set imgIndex based on the target or the lastDataIndex
  let imgIndex = target.hasAttribute("data-index")
    ? parseInt(target.getAttribute("data-index"), 10)
    : globalAttributes.lastDataIndex;

  if (isNaN(imgIndex)) {
    console.error("Invalid data-index found.");
    return;
  }

  if (galleryAction === "openGalleryImage" && target.id === "expand" && isModalActive) {
    closeFullscreen();
    adjustGalleryPosition(thumbnails[imgIndex], currentClass);
    return;
  }

  // Update the lastDataIndex based on the gallery action
  globalAttributes.lastDataIndex = handleGallerySwitch(galleryAction, thumbnails, imgIndex);

  // Adjust gallery position based on lastDataIndex and currentClass
  adjustGalleryPosition(thumbnails[globalAttributes.lastDataIndex], currentClass);

  // Update left column details with selected thumbnail
  updateLeftColumnWithDetails(
    thumbnails[imgIndex+1].getAttribute(globalAttributes.dataTitle),
    thumbnails[imgIndex+1].getAttribute(globalAttributes.dataCategory),
    thumbnails[imgIndex+1].getAttribute(globalAttributes.dataSubject),
    thumbnails[imgIndex+1].getAttribute(globalAttributes.dataDesc1),
    thumbnails[imgIndex+1].getAttribute(globalAttributes.dataDesc2),
    thumbnails[imgIndex+1].getAttribute(globalAttributes.dataSrc)
  );
}

/**
 * Handles the switch between different gallery actions (next, previous, restart, open).
 *
 * @param {string} galleryAction - The action to perform.
 * @param {Array<Element>} thumbnails - The list of thumbnails.
 * @param {number} imgIndex - The current image index.
 * @returns {number} - The updated lastDataIndex.
 */
function handleGallerySwitch(galleryAction, thumbnails, imgIndex) {
  //console.log("handleGallerySwitch()");
  //console.log("handleGallerySwitch() imgIndex", imgIndex);

  switch (galleryAction) {
    case "nextImage":
      return (globalAttributes.lastDataIndex =
        (globalAttributes.lastDataIndex + 1) % thumbnails.length);
    case "prevImage":
      return (globalAttributes.lastDataIndex =
        (globalAttributes.lastDataIndex - 1 + thumbnails.length) %
        thumbnails.length);
    case "restartImage":
      return (globalAttributes.lastDataIndex = 0);
    case "openGalleryImage":
    case "openThumb":
      handleOpenSubjectImage(thumbnails[imgIndex], imgIndex);
      return imgIndex;
    default:
      console.warn(`Unknown galleryAction: ${galleryAction}`);
      return imgIndex;
  }
}

/**
 * Retrieves and displays the nearest 200 images to the target.
 *
 * @param {HTMLElement} target - The image element that was clicked.
 * @param {number} imgIndex - The index of the image clicked.
 */
async function handleOpenSubjectImage(target, imgIndex) {
  //console.log("handleOpenSubjectImage()");
  //console.log("handleOpenSubjectImage() target", target);

  try {
    const currentIndex = imgIndex;
    const imageGridContainerClass = getImageGridContainerClass();
    const imageGridContainer = document.querySelector(`.${imageGridContainerClass}`);

    if (!imageGridContainer) {
      console.warn(`No image grid container found with class "${imageGridContainerClass}"`);
      return;
    }

    // Cache all image elements in the container
    const imageElements = Array.from(imageGridContainer.querySelectorAll("img"));
    const totalImages = imageElements.length;

    // Calculate start and end indices for nearest 200 images
    const startIndex = Math.max(0, currentIndex - 100);
    const endIndex = Math.min(totalImages, currentIndex + 100 + 1); // Ensure up to 201 images

    // Slice to get the subset of nearest images
    const nearestImages = imageElements.slice(startIndex, endIndex);

    const imagesForGallery = nearestImages.map((imgElem) => ({
      img_url: imgElem.getAttribute(globalAttributes.src),
      img_title: imgElem.getAttribute(globalAttributes.dataTitle) || "",
      img_desc1: imgElem.getAttribute(globalAttributes.dataDesc1) || "",
      img_desc2: imgElem.getAttribute(globalAttributes.dataDesc2) || "",
      img_desc3: imgElem.getAttribute(globalAttributes.dataDesc3) || "",
      img_src: imgElem.getAttribute(globalAttributes.dataSrc) || "",
      img_data_index: imgElem.getAttribute(globalAttributes.dataIndex) || "",
      data_category: imgElem.getAttribute(globalAttributes.dataCategory) || "",
      data_subject: imgElem.getAttribute(globalAttributes.dataSubject) || "",
      originalIndex: currentIndex, 
    }));

    const adjustedCurrentIndex = currentIndex - startIndex;
    const currentImageSrc = target.src || imagesForGallery[adjustedCurrentIndex].img_src;

    // Fetch gallery HTML with the nearest images and current image source
    const url = globalEndpoints.photosFullscreen;
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        images: imagesForGallery,
        currentImage: currentImageSrc,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch gallery HTML");
    }

    const galleryHTML = await response.text();
    const photoGalleryModal = document.getElementById(globalClasses.photoGalleryModalContainer);
    if (!photoGalleryModal) {
      console.warn(`No element found with id "${globalClasses.photoGalleryModalContainer}"`);
      return;
    }

    photoGalleryModal.innerHTML = galleryHTML;
    photoGalleryModal.classList.add(globalAttributes.activeStatus);

    updateLeftColumnWithDetails(
      target.getAttribute(globalAttributes.dataTitle),
      target.getAttribute(globalAttributes.dataCategory),
      target.getAttribute(globalAttributes.dataSubject),
      target.getAttribute(globalAttributes.dataDesc1),
      target.getAttribute(globalAttributes.dataDesc2),
      currentImageSrc
    );
  } catch (error) {
    console.error("Error in handleOpenSubjectImage:", error);
  }
}


/**
 * Determines the appropriate image grid container class based on the active state.
 *
 * @returns {string} - The class name of the image grid container.
 */
function getImageGridContainerClass() {
  //console.log("getImageGridContainerClass()")

  const photoGridContainer = document.querySelector(
    `.${globalClasses.photoGridContainer}`
  )
  if (photoGridContainer?.classList.contains(globalAttributes.activeStatus)) {
    // Use the image grid container class if active
    return globalClasses.imageGridContainer
  } else {
    // Otherwise, use the insight thumbnail grid class
    return globalClasses.insightThumbnailGrid
  }
}


/**
 * Determines the correct thumbnails container class based on the current state.
 *
 * @param {boolean} isPhotoCategoryActive - Whether the photo category is active.
 * @param {boolean} isModalActive - Whether the modal is active.
 * @returns {string} - The class name of the thumbnails container.
 */
function getThumbnailsContainerClass(isPhotoCategoryActive, isModalActive) {
  //console.log("getThumbnailsContainerClass()")

  if (isPhotoCategoryActive) {
    return globalClasses.imageGridContainer
  } else if (isModalActive) {
    return globalClasses.insightThumbnailGridFullscreen
  }
  return globalClasses.insightThumbnailGrid
}

/**
 * Retrieves the thumbnails container.
 *
 * @param {string} thumbnailsContainerClass - The class name of the thumbnails container.
 * @returns {HTMLElement|null} - The thumbnails container element.
 */
function getThumbnailsContainer(thumbnailsContainerClass) {
  //console.log("getThumbnailsContainer()")

  return (
    document.querySelector(`.${thumbnailsContainerClass}`) ||
    document.querySelector(`.${globalClasses.imageGridContainer}`)
  )
}

/**
 * Aligns thumbnails to center the current thumbnail in the view.
 *
 * @param {HTMLElement} thumbnailsContainer - The container holding the thumbnails.
 * @param {string} currentClass - The class name used to mark the current thumbnail.
 */
function alignThumbnails(thumbnailsContainer, currentClass) {
  //console.log("alignThumbnails()")

  const currentThumbnail = thumbnailsContainer.querySelector(`.${currentClass}`)

  if (!currentThumbnail) {
    console.warn(`No thumbnail with the class "${currentClass}" found.`)
    return
  }

  // Get the height of the container and the current thumbnail
  const thumbnailHeight = currentThumbnail.offsetHeight
  const containerHeight = thumbnailsContainer.clientHeight

  // Calculate the scroll position to center the current thumbnail in the container
  const scrollPosition =
    currentThumbnail.offsetTop - containerHeight / 2 + thumbnailHeight / 2

  // Scroll to the calculated position
  setTimeout(() => {
    thumbnailsContainer.scrollTo({
      top: scrollPosition,
      behavior: globalAttributes.scrollBehaviorDefault,
    })
  }, 5)
}

/**
 * Adjusts the gallery position to highlight the current thumbnail.
 *
 * @param {HTMLElement} thumbnail - The current thumbnail element.
 * @param {string} currentClass - The class name used to mark the current thumbnail.
 */
function adjustGalleryPosition(thumbnail, currentClass) {
  //console.log("adjustGalleryPosition()")
  //console.log("adjustGalleryPosition() thumbnail", thumbnail)
  //console.log("adjustGalleryPosition() currentClass", currentClass)

  setTimeout(() => {
    setCurrentThumbnail(thumbnail, currentClass)
  }, 50) // Delay to allow the DOM to update

  setTimeout(() => {
    let containerClass = globalClasses.insightThumbnailGrid
    if (
      document.querySelector(`.${globalClasses.insightThumbnailGridFullscreen}`)
    ) {
      containerClass = globalClasses.insightThumbnailGridFullscreen
    }
    const container = document.querySelector(`.${containerClass}`)
    if (container) {
      alignThumbnails(container, currentClass)
    }
  }, 100)
}

/**
 * Sets the clicked thumbnail as active and updates the enlarged image.
 *
 * @param {HTMLElement} thumbnail - The thumbnail to set as current.
 * @param {string} currentClass - The class name used to mark the current thumbnail.
 */
function setCurrentThumbnail(thumbnail, currentClass) {
  //console.log("setCurrentThumbnail()")

  const insightImgs = document.querySelectorAll(
    `.${globalClasses.insightThumbnailImage}`
  )

  insightImgs.forEach((img) => {
    if (img.src === thumbnail.src) {
      img.classList.add(currentClass)
    } else {
      img.classList.remove(currentClass)
    }
  })

  const enlargedImages = [
    ...document.querySelectorAll(`.${globalClasses.enlargedImgFullscreen}`),
    ...document.querySelectorAll(`.${globalClasses.enlargedImg}`),
  ]

  // Loop through each enlarged image and set src
  enlargedImages.forEach((enlargedImg) => {
    if (enlargedImg instanceof HTMLImageElement) {
      enlargedImg.src = removePilPart(thumbnail.src)
    } else {
      console.error(
        "setCurrentThumbnail Found a non-HTMLImageElement in enlargedImages:",
        enlargedImg
      )
    }
  })

  if (enlargedImages.length === 0) {
    console.error("No enlarged image found in either container.")
  }
}

/**
 * Handles clicks on icons or filters to update the UI accordingly.
 *
 * @param {HTMLElement} target - The element that was clicked.
 */
function handleIconOrFilterClick(target) {
  //console.log("handleIconOrFilterClick()")

  // Retrieve filter category and active class
  const filterCategory = target.dataset.filterCategory
  const activeClass = globalAttributes.activeStatus

  // Map elements by their roles
  const elements = {
    toolbarContainer: document.getElementById(
      globalClasses.mainFeedToolbarContainer
    ),
    toolbarWrapper: document.querySelector(
      `.${globalClasses.mainFeedToolbarWrapper}`
    ),
    homeDefault: document.querySelector(`.${globalClasses.homeDefaultInsight}`),
    mainFeedContainer: document.querySelector(
      `.${globalClasses.mainFeedContent}`
    ),
    filterSummaryContent: document.querySelector(
      `.${globalClasses.filterSummaryContent}`
    ),
    photoGrid: document.querySelector(`.${globalClasses.photoGridContainer}`),
    photoGalleryFilters: document.querySelector(
      `.${globalClasses.photoGalleryFilters}`
    ),
    leftColumn: document.querySelector(`.${globalClasses.leftColumn}`),
    leftColumnDefault: document.querySelector(
      `.${globalClasses.leftColumnDefault}`
    ),
    middleColumn: document.querySelector(`.${globalClasses.middleColumn}`),
    contentContainer: document.querySelector(
      `.${globalClasses.contentContainer}`
    ),
    toolbarIconGridContainer: document.querySelector(
      `.${globalClasses.toolbarIconGridContainer}`
    ),
    photoGridDetails: document.querySelector(
      `.${globalClasses.photoGridDetails}`
    ),
    mainFeedReplace: document.querySelector(
      `.${globalClasses.mainFeedReplace}`
    ),
  }

  // Define element groups for easy toggling
  const elementGroups = {
    hide: ["mainFeedContainer", "contentContainer"],
    show: ["filterSummaryContent", "photoGrid", "photoGalleryFilters"],
    activate: [
      "leftColumn",
      "middleColumn",
      "contentContainer",
      "mainFeedContainer",
    ],
    toolbar: ["toolbarContainer", "toolbarWrapper"],
    show2: ["homeDefault"],
  }

  // Determine if category is photos and toggle classes accordingly
  const isPhotoCategory = filterCategory.includes(globalClasses.photoCategory)
  //console.log(`handleIconOrFilterClick() isPhotoCategory ${isPhotoCategory}`)

  toggleActiveClass(elements, elementGroups.hide, isPhotoCategory, activeClass)
  toggleActiveClass(elements, elementGroups.show, isPhotoCategory, activeClass)
  toggleActiveClass(
    elements,
    elementGroups.activate,
    isPhotoCategory,
    activeClass
  )
  toggleActiveClass(
    elements,
    elementGroups.toolbar,
    isPhotoCategory,
    activeClass
  )
  toggleActiveClass(elements, elementGroups.show2, isPhotoCategory, activeClass)

  // Scroll the middle column back to the top
  if (elements.middleColumn) {
    elements.middleColumn.scrollTo(0, 0)
  } else {
    console.warn("handleIconOrFilterClick() - Middle column element not found.")
  }

  // Filter main feed based on the selected category
  currentPage = 1
  const contentReplaceElements = document.querySelectorAll(
    `.${globalClasses.mainFeedReplace}`
  )
  contentReplaceElements.forEach((element) => {
    element.innerHTML = ""
  })
  filterMainFeed(filterCategory)

  const summaryContent = document.querySelector(
    `.${globalClasses.summaryContent}`
  )
  const leftColumnContent = document.querySelector(
    `.${globalClasses.leftColumnDefault}`
  )

  leftColumnContent.classList.add(globalAttributes.activeStatus)
  summaryContent.classList.add(globalAttributes.activeStatus)
}

/**
 * Utility function to toggle active classes on UI elements.
 *
 * @param {Object} elements - An object mapping element names to elements.
 * @param {string[]} elementKeys - The keys of elements to toggle.
 * @param {boolean} isVisible - Whether to add or remove the active class.
 * @param {string} activeClass - The class name to toggle.
 */
function toggleActiveClass(elements, elementKeys, isVisible, activeClass) {
  //console.log("toggleActiveClass()")

  elementKeys.forEach((key) => {
    if (elements[key]) {
      elements[key].classList.toggle(activeClass, isVisible)
    }
  })
}

/**
 * Opens a post or media link when a post is clicked.
 *
 * @param {HTMLElement} target - The element that was clicked.
 */
async function handlePostClick(target) {
  //console.log("handlePostClick()")

  const mediaLink = target.getAttribute(globalAttributes.dataMediaLink)
  if (mediaLink) {
    window.open(mediaLink, "_blank")
    return
  }

  const postId = target.id
  const filterCategory = target.getAttribute(
    globalAttributes.dataFilterCategory
  )
  const clusterID = target.getAttribute(globalAttributes.dataInsightCluster)
  const categoryID = target.getAttribute(globalAttributes.dataCategoryId)
  const url = `.${globalEndpoints.insightStoryContent}?postId=${postId}&filterCategory=${filterCategory}&clusterID=${clusterID}&categoryID=${categoryID}`

  // Get modal container
  const modal = document.getElementById(globalClasses.modalContainer)

  // Attempt to load the content with a retry button if an error occurs
  try {
    await loadModalContent(url, modal)
  } catch (error) {
    console.error("handlePostClick() - Error loading post content:", error)
    await loadModalContent(url, modal)
  }
}

/**
 * Fetches content from the server and loads it into the modal.
 *
 * @param {string} url - URL to fetch content from.
 * @param {HTMLElement} modal - Modal element to load content into.
 */
async function loadModalContent(url, modal) {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`)
  }
  const html = await response.text()
  modal.innerHTML = html
  modal.style.display = "block"
}

/**
 * Closes the fullscreen view, removes all fullscreen classes, and exits fullscreen mode.
 */
function closeFullscreen() {
  //console.log("closeFullscreen()")

  const timeOut = 50

  // Locate the last clicked icon in the image grid using lastDataIndex
  const imageGridContainer = document.querySelector(
    `.${globalClasses.imageGridContainer}`
  )

  if (imageGridContainer && globalAttributes.lastDataIndex !== undefined) {
    const lastClickedIcon = imageGridContainer.querySelector(
      `[data-index="${globalAttributes.lastDataIndex}"]`
    )

    if (lastClickedIcon) {
      // Scroll smoothly to the last clicked icon before closing the modal
      lastClickedIcon.scrollIntoView({
        behavior: globalAttributes.scrollBehaviorDefault,
        block: "center",
      })
    }
  }

  // Set a timeout to ensure smooth scroll is done before closing the modal
  setTimeout(() => {
    // Get the modal element by class
    const photoGalleryModal = document.querySelector(
      `.${globalClasses.photoGalleryModalContainer}`
    )

    if (photoGalleryModal) {
      // Remove the activeStatus class from the modal
      photoGalleryModal.classList.remove(globalAttributes.activeStatus)

      // Clear the inner HTML of the modal
      photoGalleryModal.innerHTML = ""
    } else {
      console.warn(
        `closeFullscreen(): No element with the class ${globalClasses.photoGalleryModalContainer} found.`
      )
    }

    // Exit fullscreen mode if active
    if (
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.mozFullScreenElement ||
      document.msFullscreenElement
    ) {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        // Safari
        document.webkitExitFullscreen()
      } else if (document.mozCancelFullScreen) {
        // Firefox
        document.mozCancelFullScreen()
      } else if (document.msExitFullscreen) {
        // IE/Edge
        document.msExitFullscreen()
      }
      //console.log("Exiting fullscreen mode")
    }
  }, timeOut) // Adjust this delay as needed to allow smooth scroll to finish
}
