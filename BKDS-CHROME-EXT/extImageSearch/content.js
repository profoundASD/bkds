

function truncateByBytes(str, byteLimit) {
    let bytes = 0;
    let result = '';
    str = str.split(" OR ")[0];

    for (let char of str) {
        const charBytes = new Blob([char]).size;  // Convert char to bytes and get its size
        if (bytes + charBytes > byteLimit - 3) break;  // Ensure there's space for "..."
        bytes += charBytes;
        result += char;
    }

    // If the result string is shorter than the original, append "..."
    if (result.length < str.length) {
        result += "...";
    }

    return result.trim();
}



function hideParentOfNavigationElements() {
    const navigationElements = document.querySelectorAll('[role="navigation"]');  // Select all elements with role="navigation"
    
    navigationElements.forEach(navElement => {
        const parentElement = navElement.parentElement;  // Get the parent element
        
        if (parentElement) {
            parentElement.style.display = 'none';  // Hide the parent element
        }
    });
}

function createLeftSection() {
    // Create the left section with "Forever\nUniversity" text
    const leftDiv = document.createElement('div');
    leftDiv.style.cssText = `
        text-align: left;
        font-size: 1.5em;
        white-space: pre-line;  /* Allows text to wrap on two lines */
        color: #FFFFFF;
    `;
    leftDiv.innerHTML = 'Forever<br>University';  // The two lines of text
    return leftDiv;
}

function createCenterSection() {
    // Create the center section with "Custom Search Results" and a logo
    const centerDiv = document.createElement('div');
    centerDiv.style.cssText = `
        text-align: center;
        font-size: 1.5em;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
    `;
    centerDiv.innerHTML = 'Transformed Google Search Results';

    return centerDiv;
}

function createRightSection() {
    // Create the right section container
    const rightDiv = document.createElement('div');
    rightDiv.style.cssText = `
        text-align: right;
        display: flex;
        align-items: center;
    `;

    // Use chrome.runtime.getURL to map the logo path from the extension's images folder
    const logoImg = document.createElement('img');
    logoImg.src = chrome.runtime.getURL('images/bkds_UI_BKDS.jpg');  // Correctly map the image from the extension
    logoImg.alt = 'BKDS Logo';
    logoImg.style.cssText = `
        width: 30px;
        height: 30px;
        border-radius: 50%;  /* Makes the image a circle */
        object-fit: cover;   /* Ensures the image covers the area within the circle */
    `;
    
    rightDiv.appendChild(logoImg);  // Append the logo image to the right section

    return rightDiv;
}



function insertHeaderDiv() {
    // Get the searchForm element
    const searchFormElement = document.getElementById('searchform');

    // Hide the searchForm element if it exists
    if (searchFormElement) {
        searchFormElement.style.display = 'none';  // Hides the searchForm
        searchFormElement.style.height = 0;
    }

    const topElement = document.getElementById('top');

    // Hide the previous 'top' element if it exists
    if (topElement) {
        topElement.style.display = 'none';
        topElement.style.height = 0;
    }

    // Create the main div container for the new header
    const mainDiv = document.createElement('div');
    mainDiv.className = 'header';
    mainDiv.id = 'top';
    mainDiv.style.cssText = `
        display: flex; /* Enable flexbox layout */
        justify-content: space-between; /* Distribute space between the sections */
        align-items: center; /* Vertically align items in the center */
        top: 0;
        left: 0;
        right: 0;
        z-index: 1000;
        position: fixed;  /* Fixes the header at the top of the page */
        height: 5vh;  /* Limit to 5% of the viewport height */
        width: 100%;   /* Full width */
        background-color: #999999;
        padding: 0 1%; /* Padding around the header */
        box-sizing: border-box; /* Ensures padding is included in the element's width */
    `;

    // Append left, center, and right sections to the header
    mainDiv.appendChild(createLeftSection());
    mainDiv.appendChild(createCenterSection());
    mainDiv.appendChild(createRightSection());

    // Insert the main header div to the top of the body
    document.body.insertBefore(mainDiv, document.body.firstChild);

    // Push the body content down by adding padding at the top (same as the header height, 5vh)
    document.body.style.paddingTop = '5vh';  // Ensures the body content starts below the fixed header

    // Generate the second header (from genSearchResultsHeader) below the top header
    let headerElement = genSearchResultsHeader();
    if (headerElement) {
        headerElement.style.position = 'relative';  // Make sure this header does not overlap
        document.body.insertBefore(headerElement, document.body.children[1]);  // Insert after the main header
    }

}



function hideAllNavigationElements() {
    const navigationElements = document.querySelectorAll('[role="navigation"]');  // Select all elements with role="navigation"
    
    navigationElements.forEach(element => {
        element.style.display = 'none';  // Hide each navigation element
    });
}

function hideToolsButton() {
    // Select all elements with aria-controls="hdtbMenus" and role="button"
    const elements = document.querySelectorAll('[aria-controls="hdtbMenus"][role="button"]');
    
    elements.forEach(element => {
        const elementText = element.textContent.trim();  // Get the text content of the element
        
        // Check if the text content is exactly "Tools"
        if (elementText === "Tools") {
            element.style.display = 'none';  // Hide the element
        }
    });
}


function hideSpecificListItemElements() {
    // List of text strings to check for
    const targetStrings = ["Images", "Shopping", "Videos", "All", "Maps", "Tools", "Books", "More", "News"];
    
    // Select all elements with role="listitem"
    const listItemElements = document.querySelectorAll('[role="listitem"]');
    
    listItemElements.forEach(listItem => {
        const listItemText = listItem.textContent.trim();  // Get the text content of the list item
        
        // Check if the text matches any of the target strings
        if (targetStrings.some(target => listItemText === target)) {
            listItem.style.display = 'none';  // Hide the list item if it matches
        }
    });
}

function hideElementsWithMoreText() {
    // Helper function to check for the word "More" in sub-elements and hide the parent if found
    function hideIfContainsMoreText(element) {
        // Find any sub-element (e.g., span, div) that contains the word "More"
        const subElements = element.querySelectorAll('*');
        
        subElements.forEach(subElement => {
            if (subElement.textContent.trim() === "More") {
                element.style.display = 'none';  // Hide the parent element
            }
        });
    }

    // Select all elements with role="listitem"
    const listItemElements = document.querySelectorAll('[role="listitem"]');
    listItemElements.forEach(listItem => {
        hideIfContainsMoreText(listItem);  // Check and hide if "More" is found
    });

    // Select all elements with role="button"
    const buttonElements = document.querySelectorAll('[role="button"]');
    buttonElements.forEach(button => {
        hideIfContainsMoreText(button);  // Check and hide if "More" is found
    });
}



function hideElementsWithAriaControls() {
    const elements = document.querySelectorAll('[aria-controls="hdtbMenus"]');  // Select all elements with aria-controls="hdtbMenus"
    
    elements.forEach(element => {
        element.style.display = 'none';  // Hide each element
    });
}



function moveMainContentDown() {
    const mainElement = document.querySelector('#main.main');  // Select the element with both class and id

    if (mainElement) {
        mainElement.style.marginTop = '1vh';  // Move the element down by 10% of the viewport height
    }
}


window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        // The page was loaded from the bfcache
        document.body.style.opacity = '1';    
        

    }
    
    window.scrollTo(0, 0);
    
});



//blocks 'send feedback' popout by reloading page
window.addEventListener("click", function(event) {


    //alert(event.target.tagName)
    if (event.target.tagName === 'A' ) {
        if(event.target.hasAttribute('data-immersive')){
            event.preventDefault();
            location.reload();
        }

    }else if (event.target.tagName === 'SPAN' && event.target.parentElement.hasAttribute('data-immersive')){
        event.preventDefault();
        location.reload();
    }
  }, true); // Use capturing phase for better accuracy


// A helper function to extract and clean the search term from the URL
function extractSearchTermFromURL() {
    const params = new URLSearchParams(window.location.search);
    let searchTerm = params.get('q');
    
    if (searchTerm) {
        searchTerm = decodeURIComponent(searchTerm.replace(/\+/g, ' '));

        // Remove site filters and unnecessary characters
        searchTerm = searchTerm
            .replace(/ site:[^ ]+/g, '')
            .replace(/%7C/g, '|')
            .trim();

        // Truncate after the 2nd quotation mark
        const quoteMatches = searchTerm.match(/"/g);
        if (quoteMatches && quoteMatches.length > 2) {
            searchTerm = searchTerm.split('"', 3).slice(0, 2).join('"');
        }

        searchTerm = truncateByBytes(searchTerm, 200);

        if(searchTerm === 'OR'){
            searchTerm = 'Try Again!'
        }
    }

    return searchTerm;
}

function genSearchResultsHeader() {
    // Extract the search term from the URL
    const params = new URLSearchParams(window.location.search);
    let returnDiv = null;
    let searchTerm = params.get('q');
    if (searchTerm) {
        searchTerm = decodeURIComponent(searchTerm.replace(/\+/g, ' '));

        // Remove the site filters from the search term
        searchTerm = searchTerm.replace(/ site:[^ ]+/g, '').replace(/%7C/g, '|').trim();

        // Suppress everything after the 2nd quotation mark
        const quoteMatches = searchTerm.match(/"/g);
        if (quoteMatches && quoteMatches.length > 2) {
            searchTerm = searchTerm.split('"', 3).slice(0, 2).join('"');
        }
        searchTerm = truncateByBytes(searchTerm, 200);
        if (searchTerm === 'OR') {
            searchTerm = 'Try Again!';
        }

        // Create the new div with the desired content
        const newDiv = document.createElement('div');
        newDiv.style.justifyContent = 'space-between'; // Put maximum space between child divs
        newDiv.style.zIndex = '9999';

        // Div for the text
        const textDiv = document.createElement('div');
        textDiv.style.fontSize = "35pt";
        textDiv.style.textAlign = 'center';
        textDiv.style.color = '#000000';
        textDiv.innerHTML = `<div style='margin-top:2%; color:rgba(58, 60, 61, 0.75); font-style:italic'>"${searchTerm}"</div>`;
        newDiv.appendChild(textDiv);

        // Create a div for the images
        const imagesDiv = document.createElement('div');
        imagesDiv.style.textAlign = 'center';
        imagesDiv.style.marginTop = '2%';
        imagesDiv.style.marginBottom = '-2%';
        action: () => {const baseUrl = 'https://www.google.com/search?tbm=isch&q=';
             const query = encodeURIComponent(searchTerm); // Encodes the search term for URL safety
            window.location.href = `${baseUrl}${query}`;
        }
        // List of image file names and their actions
        const imageFiles = [
            { file: 'Back.png', action: () => window.history.back() },
            { file: 'Home.png', action: () => window.location.href = 'http://localhost:3000' },
            { file: 'Retry.png', action: () => window.location.href = 'http://localhost:3000/?startSpeech=true&type=voice_search_general' },
            { file: 'All.png', action: () => window.location.href = `https://www.google.com/search?tbm=isch&q=${encodeURIComponent(searchTerm)}` },
            { file: 'Flickr.png', action: () => executeSearch('flickr.com', searchTerm) },
            { file: 'Wiki.png', action: () => executeSearch('wikipedia.org', searchTerm) },
            { file: 'YTGrey.png', action: () => executeSearch('youtube.com', searchTerm) },
            { file: 'Google_Maps_Logo_2020.svg.png', action: () => window.location.href = `https://www.google.com/maps/search/${encodeURIComponent(searchTerm)}` },
            { file: 'Google_Earth_icon.png', action: () => window.location.href = `https://earth.google.com/web/search/${encodeURIComponent(searchTerm)}/` }
        ];

        // Add images to the imagesDiv and attach click events
        imageFiles.forEach(({ file, action }) => {
            const img = document.createElement('img');
            img.src = chrome.runtime.getURL('images/' + file);
            img.style.width = '80px';
            img.style.height = '80px';
            img.style.marginRight = '10px'; // Optional: Add some space between images

            // Set image as clickable and attach the action
            img.style.cursor = 'pointer';
            img.addEventListener('click', action);

            // Create a div to wrap the img
            const imgWrapper = document.createElement('div');
            imgWrapper.id = file; // Set the id of the div to the filename
            imgWrapper.appendChild(img); // Append the img to the wrapper div
            imgWrapper.style.display = 'inline-block'; // Ensure the divs are inline with each other
            imgWrapper.style.zIndex = '9999';  // Setting a high z-index value
            imgWrapper.style.position = 'relative';
            imgWrapper.role = 'filter';
            imagesDiv.appendChild(imgWrapper);
        });

        // Append the imagesDiv to the main newDiv
        newDiv.appendChild(imagesDiv);
        returnDiv = newDiv;
    }
    
    return returnDiv;
}

function createImageWrapperDiv() {
    const imagesDiv = document.createElement('div');
    imagesDiv.classList.add('images-div');

    const imageFiles = [
        'Back.png', 'Home.png', 'Retry.png', 'blank.png', 'All.png', 'Flickr.png', 
        'Wiki.png', 'YTGrey.png', 'Google_Maps_Logo_2020.svg.png', 'Google_Earth_icon.png'
    ];

    for (const file of imageFiles) {
        let img = document.createElement('img');
        img.src = chrome.runtime.getURL('images/' + file);
        img.classList.add('image-icon');

        let imgWrapper = document.createElement('div');
        imgWrapper.id = file;
        imgWrapper.classList.add('image-wrapper');
        imgWrapper.appendChild(img);
        imgWrapper.role = 'filter';

        imagesDiv.appendChild(imgWrapper);
    }

    return imagesDiv;
}


function executeSearch(siteFilter, query) {
    // Construct the new search URL
    var newUrl = 'https://www.google.com/search?q=' + encodeURIComponent(query + ' site:' + siteFilter) + '&tbm=isch';
    // Open the new search URL in a new tab
    window.location.href = newUrl;
}

window.addEventListener('load', function() {
    document.body.style.backgroundColor = '#D3D3D3';
    document.body.style.opacity = '1';

    let elementCounter = 0;
    const RGB_999999 = "rgb(153, 153, 153)";

    const observer = new MutationObserver(mutationsList => {
        mutationsList.forEach(_mutation => {
            handleBackgroundColorChange();
            hideSpecifiedButtons();
            handleDivHeaders();
            processButtons();
            processSpans();
            processLinksAndDivs();
            formatCWizElements();
            formatRelatedDivs();
            formatVisitButtons();
            //hideAllNavigationElements();
            hideSpecificListItemElements();
            hideToolsButton();
            hideElementsWithMoreText(); 
            
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
   insertHeaderDiv(); // Assuming you have defined the insertHeaderDiv function elsewhere

    function handleBackgroundColorChange() {
        const elements = document.querySelectorAll('div[data-hveid][data-rfg][data-ri][data-os][data-ved]');
        elements.forEach(element => {
            const bgColor = getComputedStyle(element).backgroundColor;
            if (bgColor !== RGB_999999) {
                elementCounter++;
                element.style.backgroundColor = "#999999";
                console.log('element counter: ', elementCounter);
            }
        });
    }

    function hideSpecifiedButtons() {
        const buttonsToHide = document.querySelectorAll("button[aria-label='Share'], button[aria-label='Saved'], button[aria-label='Save']");
        buttonsToHide.forEach(button => {
            button.style.display = 'none';
        });
    }

    function handleDivHeaders() {
        const divHeader = document.querySelectorAll('div[jscontroller="hwnrob"]');
        for (let i = 0; i < divHeader.length && i < 5; i++) {
            divHeader[i].firstChild.style.backgroundColor = '#D3D3D3';
        }
    }

    function processButtons() {
        const buttons = document.querySelectorAll('button');
        const ignoreAriaLabels = ['previous image', 'next image', 'close'];

        buttons.forEach(button => {
            const buttonAriaLabel = (button.getAttribute('aria-label') || "").trim().toLowerCase();
            if (!ignoreAriaLabels.includes(buttonAriaLabel) && button.firstElementChild) {
                button.firstElementChild.style.backgroundColor = '#999999';
            } else if (buttonAriaLabel.includes('More actions for this image')) {
                hideButtonAndParent(button);
            }

            removeSVGElementsAssociatedWithVisit();
            removeMoreActionsButtons();
        });
    }

    function hideSearchFormElements() {
        const elements = document.querySelectorAll('*[id]'); // Select all elements with an ID
        elements.forEach(element => {
            const id = element.id.toLowerCase();
            if (id.includes('search') && id.includes('form') && id.indexOf('search') < id.indexOf('form')) {
                element.style.display = 'none'; // Hide the element
                element.style.pointerEvents = 'none'; // Disable interactions
                if (element.parentElement) {
                    element.parentElement.style.display = 'none'; // Optionally hide the parent
                    element.parentElement.style.pointerEvents = 'none';
                }
            }
        });
    }
    

    function removeSVGElementsAssociatedWithVisit() {
        const svgElements = document.querySelectorAll('svg[viewBox="0 0 24 24"][focusable="false"]');
        svgElements.forEach(svg => {
            const previousSibling = svg.previousElementSibling;
            const nextSibling = svg.nextElementSibling;
            const hasVisitSiblingSpan = (previousSibling && previousSibling.tagName.toLowerCase() === 'span' && previousSibling.textContent.trim() === 'Visit') || (nextSibling && nextSibling.tagName.toLowerCase() === 'span' && nextSibling.textContent.trim() === 'Visit');
            if (hasVisitSiblingSpan) {
                svg.remove();
            }
        });
    }

    function removeMoreActionsButtons() {
        const buttons = document.querySelectorAll('button[aria-label="More actions for this image"]');
        buttons.forEach(button => {
            button.remove();
        });
    }

    function hideButtonAndParent(button) {
        button.style.display = 'none';
        button.style.pointerEvents = 'none';
        if (button.parentElement) {
            button.parentElement.style.display = 'none';
            button.parentElement.style.pointerEvents = 'none';
        }
    }

    function processSpans() {
        const spans = document.querySelectorAll('span');
        spans.forEach(span => {
            if (span.textContent.trim() === "Get help" || span.textContent.trim() === "Send feedback") {
                span.style.display = 'none';
                span.parentNode.remove();
            } else {
                span.style.color = "#000000";
            }
        });

        const savedLinks = document.querySelectorAll('a[href^="/save?"]');
        Array.from(savedLinks).filter(href => href.textContent.trim() === "Saved").forEach(href => {
            href.remove();
        });
    }

    function processLinksAndDivs() {
        const links = document.querySelectorAll('a');
        links.forEach(link => {
            link.style.color = '#000000';
        });
        
        const divs = document.querySelectorAll('div');
        divs.forEach(div => {
            div.style.color = '#000000';
        });
        document.body.style.opacity = '1';
    }

    function formatCWizElements() {
        const allCWiz = document.querySelectorAll('c-wiz');
        allCWiz.forEach(element => {
            element.style.backgroundColor = '#D3D3D3';
            element.style.color = '#000000';
        });
    }

    function formatRelatedDivs() {
        const divRelated = document.querySelectorAll('a[aria-label="See more Related content"]');
        divRelated.forEach(div => {
            if (div.firstElementChild) {
                div.firstElementChild.style.backgroundColor = '#999999';
            }
        });
    }

    function formatVisitButtons() {
        const hrefsWithAriaLabel = document.querySelectorAll("a[aria-label='Visit']");
        hrefsWithAriaLabel.forEach(href => {
            href.firstChild.style.backgroundColor = '#999999';
        });
    }

    
    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });
    
    function determineFilterType(url) {
        const params = new URLSearchParams(url.split('?')[1]);
        const query = params.get('q');
    
        if (!query) {
            return 'UNKNOWN';  // No 'q' parameter found in URL
        }
    
        const siteOccurrences = (query.match(/site:/g) || []).length;
    
        if (siteOccurrences > 1) {
            return 'ALL';
        } else if (query.includes('site:flickr.com')) {
            return 'FLICKR';
        } else if (query.includes('site:youtube.com')) {
            return 'YOUTUBE';
        } else if (query.includes('site:wikipedia.org')) {
            return 'WIKI';
        } else {
            return 'UNKNOWN';  // No known 'site' pattern found
        }
    }



  function constructFreshURL(searchTerm) {
        const baseUrl = "https://www.google.com/search?q=";
        const sites = [
            "flickr.com",
            "wikipedia.org",
            "wikimedia.org",
            "youtube.com",
            "spacex.com",
            "nextspaceflight.com",
            "RocketLaunch.live"
        ];
        const siteQuery = sites.map(site => `site:${site}`).join('+OR+');
        return `${baseUrl}${searchTerm}+${siteQuery}&hl=en&tbm=isch`;
  }

  // Set background color of elements with specified data attributes
  const elementsWithDataAttributes = document.querySelectorAll('[data-hveid][data-rfg][data-ri][data-os][data-ved]');
  elementsWithDataAttributes.forEach(element => {
      element.style.backgroundColor = "#999999";
  });

  // Check if first c-wiz element with banner role exists
  const firstCWizWithBannerRole = document.querySelector('c-wiz');
  if (firstCWizWithBannerRole) {
      firstCWizWithBannerRole.style.display = 'block';
      firstCWizWithBannerRole.style.opacity = 0;
  }

  // Hide the element with data-tn attribute set to 0
  const dataTnElement = document.querySelector('[data-tn="0"]');
  if (dataTnElement) {
      dataTnElement.style.display = 'none';
  }

  // Parse and sanitize search term
  const params = new URLSearchParams(window.location.search);
  let searchTerm = params.get('q');
  if (searchTerm) {
      searchTerm = decodeURIComponent(searchTerm.replace(/\+/g, ' '));
      searchTerm = searchTerm.replace(/ site:[^ ]+/g, '').replace(/%7C/g, '|').trim();

      const quoteMatches = searchTerm.match(/"/g);
      if (quoteMatches && quoteMatches.length > 2) {
          searchTerm = searchTerm.split('"', 3).slice(0, 2).join('"');
      }

      searchTerm = truncateByBytes(searchTerm, 200); // Assuming you have defined the truncateByBytes function elsewhere
      if (searchTerm === 'OR') {
          searchTerm = 'Try Again!';
      }
  }


});

