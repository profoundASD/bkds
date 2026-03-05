// Function to disable vertical scrolling of the page
const disablePageScrolling = () => {
  document.documentElement.style.overflow = "hidden" // Disable scrolling on the root element
  document.body.style.overflow = "hidden" // Disable scrolling on the body
}

// Function to hide elements by a list of class names
const hideElementsByClassNames = (classNames) => {
  if (!Array.isArray(classNames)) {
    console.error("The classNames parameter should be an array of strings.")
    return
  }

  classNames.forEach((className) => {
    const elements = document.getElementsByClassName(className)
    Array.from(elements).forEach((element) => {
      element.style.display = "none" // Hide the element from view
      element.style.pointerEvents = "none" // Prevent user interaction
    })
  })
}

// List of class names to hide
const classesToHide = [
  "vector-main-menu-dropdown",
  "vector-typeahead-search-container",
  "vector-user-links",
  "vector-sitenotice-container",
  "cn-fundraising",
  "mw-footer-container",
  "mw-body-header",
  "vector-page-toolbar",
  "vector-page-titlebar",
  "vector-header-container",
  "vectors",
]


const createControlOverlay = () => {
    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100vh"; // Use viewport height
    overlay.style.background = "white"; // Overlay background
    overlay.style.zIndex = "9999";
    overlay.style.display = "flex";
    overlay.style.flexDirection = "column";
    overlay.style.padding = "2vh"; // Add padding for content spacing
    overlay.style.overflow = "hidden"; // Prevent overlay from scrolling

    // Header area
    const header = document.createElement("div");
    header.style.flex = "0 0 auto";
    header.style.display = "flex";
    header.style.alignItems = "center";
    header.style.margin = "0 auto"; // Center header
    header.style.background = "lightgray"; // Optional: background for visibility
    header.style.width = "98vw";
    header.style.marginLeft = "-0.025vw";

    // Column 1: Logo (25%)
    const logoContainer = document.createElement("div");
    logoContainer.style.flex = "0 0 25%";
    logoContainer.style.display = "flex";
    logoContainer.style.alignItems = "center";
    logoContainer.style.paddingLeft = "1vw"; // Left padding for logo
    const logoElement = document.querySelector(".mw-logo");
    if (logoElement) {
        const clonedLogo = logoElement.cloneNode(true);
        clonedLogo.style.maxWidth = "100%";
        clonedLogo.style.maxHeight = "50px";
        logoContainer.appendChild(clonedLogo);
    } else {
        logoContainer.textContent = "No Logo"; // Fallback text
    }

    // Column 2: Control Label (8%)
    const controlLabel = document.createElement("div");
    controlLabel.style.flex = "0 0 8%";
    controlLabel.textContent = "Read Aloud Controls";
    controlLabel.style.fontSize = "1.25em";
    controlLabel.style.background = "lightgray"; // Optional: background for visibility

    // Column 3: Controls (20%)
    const controlsContainer = document.createElement("div");
    controlsContainer.style.flex = "0 0 20%";
    controlsContainer.style.display = "flex";
    controlsContainer.style.justifyContent = "center"; // Center buttons
    controlsContainer.style.alignItems = "center";
    controlsContainer.style.background = "lightgray"; // Optional: background for visibility

    // Add a wrapper for buttons
    const buttonsWrapper = document.createElement("div");
    buttonsWrapper.style.display = "flex";
    buttonsWrapper.style.justifyContent = "space-evenly"; // Even spacing between buttons
    buttonsWrapper.style.alignItems = "center";
    buttonsWrapper.style.gap = "10px"; // Space between buttons

    const buttonStyle = {
        color: "#333", // Dark gray for good contrast
        border: "none",
        padding: "10px 20px",
        borderRadius: "5px",
        fontSize: "1.25em",
        cursor: "pointer",
    };

    const playButton = document.createElement("button");
    playButton.textContent = "Play";
    Object.assign(playButton.style, buttonStyle, { background: "#A8D5BA" }); // Soft green

    const pauseButton = document.createElement("button");
    pauseButton.textContent = "Pause";
    Object.assign(pauseButton.style, buttonStyle, { background: "#F9D8A7" }); // Soft orange

    const stopButton = document.createElement("button");
    stopButton.textContent = "Stop";
    Object.assign(stopButton.style, buttonStyle, { background: "#F7A8A8" }); // Soft red

    // Dynamically resolve the image path using chrome.runtime.getURL
    const imageURL = chrome.runtime.getURL("Home.png");

    // Create the home button
    const homeButton = document.createElement("button");
    homeButton.style.cursor = "pointer";
    homeButton.style.display = "flex"; // Flexbox for alignment
    homeButton.style.alignItems = "center";
    homeButton.style.justifyContent = "center";
    homeButton.style.border = "none"; // Remove any image-specific border
    homeButton.style.background = "lightgray"; // Optional: Ensure white background

    // Add the image to the button
    const homeIcon = document.createElement("img");
    homeIcon.src = imageURL; // Use the resolved image URL
    homeIcon.alt = "Home Icon";
    homeIcon.style.width = "3.5vw";
    homeIcon.style.border = "none"; // Remove any image-specific border
    homeIcon.style.marginLeft = "8px"; // Optional: Add spacing
    homeIcon.style.backgroundColor = "lightgray";
    homeButton.appendChild(homeIcon);

    // Append buttons to the wrapper
    buttonsWrapper.appendChild(playButton);
    buttonsWrapper.appendChild(pauseButton);
    buttonsWrapper.appendChild(stopButton);
    buttonsWrapper.appendChild(homeButton);

    controlsContainer.appendChild(buttonsWrapper);

    // Column 4: Placeholder (remaining space)
    const rightSection = document.createElement("div");
    rightSection.style.flex = "0 0 45%"; // Remaining space
    rightSection.style.textAlign = "right"; // Right-align text
    rightSection.style.fontSize = ".95em";
    rightSection.style.background = "lightgray"; // Optional: background for visibility
    rightSection.innerHTML =
        "Wikipedia Content Transformed by<br>Brothers Keeper Data Solutions";

    // Append all columns to the header
    header.appendChild(logoContainer);
    header.appendChild(controlLabel);
    header.appendChild(controlsContainer);
    header.appendChild(rightSection);

    // Main content area
    const contentArea = document.createElement("div");
    contentArea.style.flex = "1 1 auto";
    contentArea.style.display = "flex";
    contentArea.style.gap = "1vw";
    contentArea.style.width = "98%";
    contentArea.style.margin = "0 auto";
    contentArea.style.height = "100%";
    contentArea.style.paddingTop = "4vh";
    contentArea.style.overflow = "hidden"; // Prevent contentArea from scrolling

    // Create text column
    const textColumn = document.createElement("div");
    textColumn.style.flex = "0 0 63%";
    textColumn.style.overflowY = "auto";
    textColumn.style.color = "black";
    textColumn.style.height = "100%";
    textColumn.style.fontSize = "1.5em";
    textColumn.style.paddingLeft = "1vw"; // Add left padding
    textColumn.style.paddingRight = "5vw"; // Add right padding
    textColumn.style.boxSizing = "border-box"; // Ensure padding is included within width

    // Create image column
    const imageColumn = document.createElement("div");
    imageColumn.style.flex = "0 0 35%";
    imageColumn.style.overflowY = "auto";
    imageColumn.style.height = "100%";
    imageColumn.style.alignContent = "center";
    imageColumn.style.textAlign = "center";

    contentArea.appendChild(textColumn);
    contentArea.appendChild(imageColumn);

    overlay.appendChild(header);
    overlay.appendChild(contentArea);

    document.body.appendChild(overlay);

    return {
        playButton,
        pauseButton,
        stopButton,
        homeButton,
        textColumn,
        imageColumn,
    };
};


// Add CSS for scrollbar width
const style = document.createElement("style")
style.textContent = `
    /* Apply styles to all scrollbars */
    ::-webkit-scrollbar {
        width: 2vw; 
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(100, 100, 100, 0.7); /* Custom scrollbar thumb color */
        border-radius: 10px; /* Round the scrollbar thumb */
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 100, 100, 0.9); /* Darker on hover */
    }
    ::-webkit-scrollbar-track {
        background: rgba(200, 200, 200, 0.3); /* Custom scrollbar track color */
    }
`
document.head.appendChild(style)

// Text-to-speech setup
const synth = window.speechSynthesis;
let utterance;
let currentChunkIndex = 0;

// Function to load voices
const loadVoices = () => {
    return new Promise((resolve) => {
        let voices = synth.getVoices();
        if (voices.length !== 0) {
            resolve(voices);
        } else {
            synth.onvoiceschanged = () => {
                voices = synth.getVoices();
                resolve(voices);
            };
        }
    });
};

// Function to read text chunks
const highlightColor = '#F9D8A7'; // Hexadecimal color

const readChunks = (chunks) => {
    if (currentChunkIndex >= chunks.length) {
        currentChunkIndex = 0;
        return;
    }

    const chunk = chunks[currentChunkIndex];

    // Replace [BR] placeholders with periods to treat them as sentence breaks
    let chunkHTML = chunk.innerHTML;
    let chunkText = chunkHTML.replace(/\[BR\]/g, '. ').replace(/<br\s*\/?>/gi, '. ');

    // Create the utterance with the processed text
    utterance = new SpeechSynthesisUtterance(chunkText);

    // Optional: Set voice, rate, pitch, etc.
    // utterance.voice = synth.getVoices()[0]; // Example: Select first available voice
    // utterance.rate = 1; // Normal rate
    // utterance.pitch = 1; // Normal pitch

    // Handle the end of the utterance
    utterance.onend = () => {
        currentChunkIndex++;
        readChunks(chunks);
    };

    // Handle errors
    utterance.onerror = (event) => {
        console.error('Speech synthesis failed:', event.error);
        // Optionally, reset or stop reading
    };

    // Start speaking
    synth.speak(utterance);

    // Highlight the current chunk
    chunks.forEach((span, index) => {
        span.style.background = index === currentChunkIndex ? highlightColor : '';
    });

    // Scroll to the current chunk
    chunk.scrollIntoView({ behavior: 'smooth', block: 'center' });
};

// Start reading
const startReading = async (chunks) => {
    console.log('startReading()');
    console.log(`synth.speaking: ${synth.speaking}, synth.paused: ${synth.paused}, synth.pending: ${synth.pending}`);

    // Wait for voices to load
    await loadVoices();

    if (synth.paused) {
        // Resume speaking if paused
        console.log('startReading() resuming');
        synth.resume();
        return;
    }

    // Cancel any existing speech synthesis
    if (synth.speaking || synth.pending) {
        console.log('startReading() cancelling existing speech');
        synth.cancel();
    }

    console.log('startReading() starting to read chunks from index', currentChunkIndex);
    readChunks(chunks);
};

// Pause reading
const pauseReading = () => {
    console.log('pauseReading()');
    if (synth.speaking && !synth.paused) {
        console.log('Pausing speech synthesis');
        synth.pause();
    }
};

// Stop reading
const stopReading = (chunks) => {
    console.log('stopReading()');
    synth.cancel();
    currentChunkIndex = 0;
    chunks.forEach((span) => (span.style.background = ''));
};

/**
 * Normalize a filename to its base extension.
 * @param {string} filename - The filename to normalize.
 * @returns {string} - The filename with only the base extension.
 */
function normalizeFileExtension(filename) {
  console.log("normalizeFileExtension()", filename)

  // Match and keep the first extension, removing any chained extensions
  return filename.replace(/(\.[a-zA-Z0-9]+)+$/, (match) => {
    const extensions = match.split(".").filter(Boolean) // Split and remove empty entries
    console.log("normalizeFileExtension() extensions", extensions)
    console.log("normalizeFileExtension() extensions[0]", extensions[0])

    return `.${extensions[0]}` // Return the first extension as the base
  })
}

// Function to process images and wrap them with appropriate HREF links
function processImages() {
  const image_tags = document.getElementsByTagName("img")
  let image_list = []
  let k = 0

  // Extract base page name from current URL
  const currentURL = new URL(window.location.href)
  const pathSegments = currentURL.pathname.split("/")

  // Ensure the URL has the expected format
  // Example: /wiki/Lockheed_Martin_C-130J_Super_Hercules
  let pageName = ""
  if (pathSegments.length >= 3 && pathSegments[1] === "wiki") {
    pageName = pathSegments.slice(2).join("/") // Supports nested paths if any
  } else {
    console.warn(
      "Unexpected URL format. HREF links may not be constructed correctly."
    )
  }

  for (const image_tag of image_tags) {
    // Exclude images nested within an element with the class 'navbox-image'
    if (image_tag.closest(".navbox-image")) {
      console.log(
        `Excluding image nested within 'navbox-image': ${image_tag.src}`
      )
      continue // Skip this image
    }

    let fileType = image_tag.src
      .substring(image_tag.src.lastIndexOf(".") + 1)
      .toUpperCase()
    let alt_text = image_tag.alt.toUpperCase()
    let src_upper = image_tag.src.toUpperCase()
    let parent_outer_html = image_tag.parentElement.outerHTML.toUpperCase()

    // Apply filters to exclude certain images
    if (
      fileType !== "OGG" &&
      !src_upper.includes("POWEREDBY_MEDIAWIKI") &&
      !src_upper.includes("PROTECTED") &&
      !src_upper.includes("PROTECTION") &&
      !src_upper.includes("PENDING") &&
      !src_upper.includes("FEATURED") &&
      !src_upper.includes("UI_ICON_EDIT") &&
      !src_upper.includes("LISTEN") &&
      !alt_text.includes("FEATURED") &&
      !alt_text.includes("LISTEN") &&
      !src_upper.includes("SYMBOL") &&
      parent_outer_html.includes(":") &&
      !src_upper.includes("QUESTION_BOOK") &&
      !src_upper.includes("WIKI_LETTER") &&
      !src_upper.includes("TEXT_DOCUMENT") &&
      !src_upper.includes("QUESTION_MARK") &&
      !src_upper.includes("EMBLEM-MONEY") &&
      !alt_text.includes("ICON") &&
      !src_upper.includes("RED_PENCIL") &&
      !parent_outer_html.includes("PORTAL:TECHNOLOGY") &&
      !parent_outer_html.includes("STATIC/IMAGES")
    ) {
      if (k >= 200) break

      // Decode the URL to handle %28 and %29
      let decodedSrc = decodeURIComponent(image_tag.src)
      console.log(`Decoded image source: ${decodedSrc}`)

      // Extract the filename and remove leading digits and 'px-'
      let filenameWithSize = decodedSrc.substring(
        decodedSrc.lastIndexOf("/") + 1
      )
      const normalizedFilename = normalizeFileExtension(
        filenameWithSize.replace(/^\d+px-/, "")
      )

      console.log(`Normalized filename: ${normalizedFilename}`)

      // Re-encode the filename for safe HREF
      const encodedFilename = encodeURIComponent(normalizedFilename)
      console.log(`Encoded filename: ${encodedFilename}`)

      // Construct the HREF
      const href = `${currentURL.origin}/wiki/${encodeURIComponent(
        pageName
      )}#/media/File:${encodedFilename}`
      console.log(`Constructed HREF: ${href}`)

      // Clone the image
      const clonedImage = image_tag.cloneNode(true)
      clonedImage.style.height = "350px"
      clonedImage.style.width = "420px" // Fixed width
      clonedImage.style.objectFit = "contain" // Maintain aspect ratio
      clonedImage.style.margin = "10px auto" // Center within column
      clonedImage.style.display = "block" // Center horizontally
      clonedImage.style.cursor = "pointer"
      clonedImage.dataset.index = k // Add data-index attribute
      clonedImage.style.background = "rgba(0, 0, 0, 0.4)" // 70% transparent black

      // Create an anchor element and wrap the cloned image
      const anchor = document.createElement("a")
      anchor.href = href
      anchor.target = "_blank" // Opens the link in a new tab
      anchor.appendChild(clonedImage)

      // Suppress default link styles
      anchor.style.textDecoration = "none" // Removes underline
      anchor.style.color = "inherit" // Inherits text color from parent
      anchor.style.all = "unset" // Resets all styles to behave like a plain element
      anchor.style.display = "inline-block" // Ensure proper block behavior for contained elements

      // Add the anchor to the image list
      image_list.push(anchor)
      k++
    }
  }

  return image_list
}


// Process the page to prepare it for text-to-speech and image gallery
const processPage = () => {
  // Ensure overlay is created and structured properly
  const {
    playButton,
    pauseButton,
    stopButton,
    homeButton,
    textColumn,
    imageColumn,
  } = createControlOverlay();

  const bodyContent = document.getElementById("bodyContent");
  const pageTitleElement = document.querySelector(".mw-page-title-main");

  if (!bodyContent) {
    alert("No readable content found!");
    return;
  }

  // Extract and process valid links
  const extractValidLinks = () => {
    const allLinks = Array.from(bodyContent.querySelectorAll("a[href]"));
    const filteredLinks = allLinks
      .filter((link) => {
        const href = link.getAttribute("href");
        // Include only links that match the "/wiki/<page>" pattern
        return href && href.startsWith("/wiki/") &&
          !href.includes(":") && // Exclude special pages (e.g., ":Category", ":File")
          !href.includes("wikidata.org") &&
          !href.includes("commons.wikimedia.org");
      })
      .slice(0, 10); // Limit to the first 10 valid links

    return filteredLinks.map((link) => {
      const href = link.getAttribute("href");
      const text = link.textContent.trim();
      const fullUrl = `https://en.wikipedia.org${href}`;
      return { text, fullUrl };
    });
  };

  // Add links as buttons above the title
  const addRelatedLinks = (links) => {
    if (links.length === 0) return;

    const linksContainer = document.createElement("div");
    linksContainer.style.display = "flex";
    linksContainer.style.flexWrap = "wrap";
    linksContainer.style.gap = "0.5em";
    linksContainer.style.marginBottom = "1em";

    links.forEach(({ text, fullUrl }) => {
      const linkButton = document.createElement("button");
      linkButton.textContent = text || "Related Link";
      linkButton.style.padding = "0.5em 1em";
      linkButton.style.border = "1px solid #ccc";
      linkButton.style.borderRadius = "4px";
      linkButton.style.backgroundColor = "#f9f9f9";
      linkButton.style.cursor = "pointer";
      linkButton.style.textAlign = "center";
      linkButton.style.fontSize = "0.75em";

      // Open the link in a new tab
      linkButton.addEventListener("click", () => {
        window.open(fullUrl, "_blank");
      });

      linksContainer.appendChild(linkButton);
    });

    // Prepend the links container so it appears above the title
    textColumn.prepend(linksContainer);
  };

  // Process and add related links
  const relatedLinks = extractValidLinks();
  addRelatedLinks(relatedLinks);

  // Get the page title
  let pageTitle = "";
  if (pageTitleElement) {
    pageTitle = pageTitleElement.textContent.trim();
  }

  // Add the title to the text column
  if (pageTitle) {
    const titleElement = document.createElement("h2");
    titleElement.textContent = pageTitle;
    titleElement.style.marginBottom = "1em";
    titleElement.style.fontSize = "2em"; // Slightly larger for emphasis
    titleElement.style.fontWeight = "bold";
    titleElement.setAttribute("touch-to-hear", "");
    textColumn.appendChild(titleElement);
  }

  // Get and process the text content
  const text = bodyContent.innerText.trim();
  if (!text) {
    alert("No readable text found in the content area!");
    return;
  }

  // Convert text to chunks and append to text column
  const processedHTML = splitTextIntoSpans(text);
  const contentElement = document.createElement("div");
  contentElement.innerHTML = processedHTML;
  textColumn.appendChild(contentElement);

  // Find all the text chunks (span elements)
  const chunks = Array.from(
    contentElement.querySelectorAll('span[id^="chunk-"]')
  );

  // Process images and append to the image column
  const imageList = processImages();
  imageList.forEach((img) => {
    imageColumn.appendChild(img);
  });

  // Add event listeners to the player controls
  playButton.addEventListener("click", () => startReading(chunks));
  pauseButton.addEventListener("click", pauseReading);
  stopButton.addEventListener("click", () => stopReading(chunks));

  // Add event listener to the "Home" button
  homeButton.addEventListener("click", () => {
    window.location.href = "http://localhost:3000"; // Navigate to home URL
  });

  // Set up image navigation
  let currentImageIndex = 0;

  const highlightImage = (index) => {
    imageList.forEach((img, idx) => {
      img.style.border = idx === index ? "2px solid blue" : "";
    });
    // Scroll to the current image
    imageList[index].scrollIntoView({ behavior: "smooth", block: "center" });
  };

  highlightImage(currentImageIndex);

  // Keyboard navigation
  document.addEventListener("keydown", (event) => {
    if (event.key === "ArrowUp") {
      textColumn.scrollBy({ top: -50, behavior: "smooth" });
    } else if (event.key === "ArrowDown") {
      textColumn.scrollBy({ top: 50, behavior: "smooth" });
    } else if (event.key === "ArrowRight") {
      if (currentImageIndex < imageList.length - 1) {
        currentImageIndex++;
        highlightImage(currentImageIndex);
      }
    } else if (event.key === "ArrowLeft") {
      if (currentImageIndex > 0) {
        currentImageIndex--;
        highlightImage(currentImageIndex);
      }
    }
  });

  // Click navigation for images
  imageList.forEach((img, index) => {
    img.addEventListener("click", () => {
      currentImageIndex = index;
      highlightImage(currentImageIndex);
    });
  });
};


// Split text into spans
function splitTextIntoSpans(text) {
  // Replace [NEWPARA] with a unique placeholder
  text = text.replace(/\n\n+/g, "[NEWPARA]");
  text = text.replace(/\n/g, " ");

  // Ensure <br> tags are treated as sentence breaks
  text = text.replace(/<br\s*\/?>/gi, ".[BRBREAK]");

  const abbreviations = [
    "Mr",
    "Mrs",
    "Ms",
    "Dr",
    "Prof",
    "Inc",
    "Ltd",
    "D.C",
    "U.S",
    "Jr",
    "Sr",
    "Mx",
    "St",
    "Ave",
    "Blvd",
    "Mt",
    "Ft",
    "Rd",
    "Co",
    "Corp",
    "Etc",
    "PhD",
    "M.D",
    "B.A",
    "M.A",
    "D.D.S",
    "Esq",
    "Rev",
    "Gen",
    "Lt",
    "Capt",
    "Cmdr",
    "Col",
    "Sgt",
    "Pvt",
    "Adm",
    "C.E.O",
    "C.F.O",
    "C.I.O"
  ];

  const regex = new RegExp(
    `(?<!\\b(?:${abbreviations
      .map((abbr) => abbr.replace(".", "\\."))
      .join("|")})\\b)([\\.\\:\\?\\!])\\s+`,
    "g"
  );

  // Split sentences based on the regex
  let parts = text.split(regex);
  let fullSentences = [];
  let tempSentence = "";

  for (let i = 0; i < parts.length; i += 2) {
    let sentence = parts[i];
    let punctuation = parts[i + 1] || "";

    tempSentence += sentence.trim() + punctuation + " ";

    // If [BRBREAK] is encountered, split as a sentence break
    if (tempSentence.includes("[BRBREAK]")) {
      const tempParts = tempSentence.split("[BRBREAK]");
      tempParts.forEach((part) => {
        if (part.trim().length > 0) {
          fullSentences.push(part.trim());
        }
      });
      tempSentence = "";
    } else if (tempSentence.length >= 10) {
      fullSentences.push(tempSentence.trim());
      tempSentence = "";
    }
  }

  if (tempSentence.trim() !== "") {
    fullSentences.push(tempSentence.trim());
  }

  // Wrap each sentence in a span tag and restore paragraph breaks
  let mergedSentences = fullSentences
    .map((sentence, index) => {
      return `<span touch-to-hear id="chunk-${index}">${sentence}</span>`;
    })
    .join(" ");

  mergedSentences = mergedSentences.replace(/\[NEWPARA\]/g, "<br><br>");
  mergedSentences = mergedSentences.replace(/\[BRBREAK\]/g, "<br>");
  return `<div touch-to-hear>${mergedSentences}</div>`;
}
  
// Initialize the script when the page is fully loaded
window.addEventListener("load", () => {
  // Check if the URL contains "#/media/"
  if (window.location.href.includes("#/media/")) {
    console.log("Extension will not run on media pages:", window.location.href)
    // Exit script early
    // throw new Error('Excluded media page');

  } else {
    //hideElementsByClassNames(classesToHide) // Initial hiding
    disablePageScrolling() // Disable vertical scrolling
    processPage() // Process the page content
  }
})
