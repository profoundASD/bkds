// bkds_speechRec.js

let recognitionInstance = null

// Initialize the script after the DOM is fully loaded
document.addEventListener("DOMContentLoaded", () => {
  // Auto-start speech recognition based on URL parameters
  autoStartSpeechRecognition()
})

// Function to get query parameters
function getQueryParams() {
  const params = new URLSearchParams(window.location.search)
  const startSpeech = params.get("startSpeech") // e.g., 'true'
  const type = params.get("type") // e.g., 'voice_search_general'
  return { startSpeech, type }
}

// Function to automatically start speech recognition if URL parameters are present
function autoStartSpeechRecognition() {
  const { startSpeech, type } = getQueryParams()

  if (startSpeech === "true" && type) {
    handleSpeechRecognitionClick(type)
  }
}

async function handleSpeechRecognitionClick(type = "voice_search_general") {
  console.log("handleSpeechRecognitionClick() with type:", type)

  // Stop any ongoing recognition service
  await stopSpeechRecognitionService()

  // Fetch and initialize speech recognition content
  try {
    console.log("Fetching speech recognition content...")
    const response = await fetch(`${globalEndpoints.speechRec}?type=${type}`)

    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`)
    }

    const html = await response.text()
    const middleColumn = document.querySelector(".main-feed-content")
    middleColumn.innerHTML = html

    initializeSpeechRecognition(type)
  } catch (error) {
    console.error("Error fetching speech recognition content:", error)
    // Optionally handle errors or retries here
  }
}

function stopSpeechRecognitionService() {
  return new Promise((resolve) => {
    if (recognitionInstance) {
      console.log("Stopping active speech recognition service...")

      recognitionInstance.onend = () => {
        console.log("Speech recognition stopped.")
        recognitionInstance = null
        resolve()
      }

      recognitionInstance.stop()
    } else {
      console.log("No active speech recognition service to stop.")
      resolve()
    }
  })
}

function initializeSpeechRecognition(speechRecType) {
  console.log("initializeSpeechRecognition()")

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    console.error("Web Speech API is not supported in this browser.")
    handleUnsupportedBrowser()
    return
  }

  const output = document.getElementById("speechRec-output")
  if (!output) {
    console.error("Output element not found.")
    return
  }

  // Initialize the speech output
  initializeOutput(output)

  // Display "Speak!" prompt
  const speechOutputElement = output.querySelector(".speech-output")
  if (speechOutputElement) {
    speechOutputElement.innerHTML = `<span class="speak-prompt">Speak to Search!</span>`
  }

  // Initialize a new SpeechRecognition instance
  recognitionInstance = new SpeechRecognition()
  recognitionInstance.continuous = true
  recognitionInstance.interimResults = true

  recognitionInstance.onstart = function () {
    console.log("Speech recognition started")
  }

  recognitionInstance.onresult = function (event) {
    let interim_transcript = ""
    let final_transcript = ""

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript
      } else {
        interim_transcript += event.results[i][0].transcript
      }
    }

    updateOutput(final_transcript, interim_transcript, output, speechRecType)
  }

  recognitionInstance.onerror = function (event) {
    console.error("Speech recognition error:", event.error)
    recognitionInstance = null
    // Optionally handle errors here
  }

  recognitionInstance.onend = function () {
    console.log("Speech recognition ended")
    recognitionInstance = null

    // Restart the recognition service
    initializeSpeechRecognition(speechRecType)
  }

  try {
    recognitionInstance.start()
  } catch (error) {
    console.error("Failed to start speech recognition:", error)
    recognitionInstance = null
  }
}

function escapeRegExp(string) {
  // Escape special characters for RegExp
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
}

function normalizeSpeechResult(input) {
  // Remove punctuation from speechResult but preserve spaces
  return input.replace(/[.,\/#!$%\^&\*;:{}=\-_~()'"]/g, "").toLowerCase()
}

function stripKeywords(keywords, speechResult) {
  console.log("stripKeywords()", keywords)

  // Normalize speechResult for comparison
  const normalizedSpeechResult = normalizeSpeechResult(speechResult)

  keywords.forEach((keyword) => {
    const escapedKeyword = escapeRegExp(keyword)
    const regex = new RegExp("\\b" + escapedKeyword + "\\b", "i") // Case-insensitive match
    const match = regex.exec(normalizedSpeechResult)

    if (match) {
      // Replace the keyword exactly as it appears in speechResult
      const matchedKeyword = match[0]
      speechResult = speechResult.replace(
        new RegExp(escapeRegExp(matchedKeyword), "gi"),
        ""
      )
    }
  })

  // Clean up multiple spaces and trim
  speechResult = speechResult.replace(/\s+/g, " ").trim()

  console.log("stripKeywords updated speechResult", speechResult)
  return speechResult
}

function stripPrefix(str) {
  return str.replace(/^[^_]+_/, "")
}

function saveVoiceSearchData(cleanedText) {
  const data = {
    searchString: cleanedText,
    timestamp: new Date().toISOString(), // UTC timestamp
  }

  fetch(globalEndpoints.saveVoiceSearch, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => {
      if (!response.ok) {
        console.error("Failed to save voice search data.")
      } else {
        console.log("Voice search data saved successfully.")
      }
    })
    .catch((error) => {
      console.error("Error saving voice search data:", error)
    })
}

async function fetchBannedWords() {
  console.log("fetchBannedWords:", globalEndpoints.bannedWords)

  try {
    const response = await fetch(globalEndpoints.bannedWords)
    if (!response.ok) {
      throw new Error("Failed to fetch banned words")
    }
    const data = await response.json()

    return data.bannedWords
  } catch (error) {
    console.error("Error fetching banned words:", error)
    return []
  }
}


function embedSearchString(cleanedText, speechRecType) {
  console.log("embedSearchString()")

  const iconsContainer = document.querySelector(".toolbar-icon-grid-container")
  if (!iconsContainer) {
    console.warn("embedSearchString(): icons container not found.")
    return
  }

  const icons = iconsContainer.querySelectorAll(".desktop_search_speech_result")

  icons.forEach((icon) => {
    const originalUrl = icon.dataset.originalUrl
    if (originalUrl) {
      const updatedUrl = originalUrl.replace(
        /@@_search_term_@@/g,
        encodeURIComponent(cleanedText)
      )
      icon.href = updatedUrl
      icon.dataset.updatedUrl = updatedUrl // Store updated URL
      icon.classList.add("search_result_pulsate")
      console.log("classList after: ", icon.classList)
    } else {
      console.warn(
        "embedSearchString(): original URL not found for icon.",
        icon
      )
    }
  })
}


function updateOutput(
  final_transcript,
  interim_transcript,
  output,
  speechRecType
) {
  let speechOutputElement = output.querySelector(".speech-output")

  if (!speechOutputElement) {
    console.warn("Speech output element not found. Reinitializing...")
    initializeOutput(output)
    speechOutputElement = output.querySelector(".speech-output")
    if (!speechOutputElement) {
      console.error(
        "Speech output element still not found after reinitialization."
      )
      return
    }
  }

  // Hide the prompt when the user starts speaking
  if (interim_transcript !== "" || final_transcript !== "") {
    removePrompt(output)
  }

  // Update the UI with interim or final transcripts
  if (interim_transcript !== "" || final_transcript === "") {
    speechOutputElement.classList.remove("final")
    speechOutputElement.innerHTML =
      final_transcript +
      '<span class="interim">' +
      interim_transcript +
      "</span>"
  }

  if (final_transcript !== "") {
    // Process and display the final transcript
    processFinalTranscript(
      final_transcript,
      speechOutputElement,
      speechRecType,
      output
    )
  }
}

async function processFinalTranscript(
  final_transcript,
  speechOutputElement,
  speechRecType,
  output
) {
  const bannedWordList = await fetchBannedWords()
  let cleanedText = stripKeywords(
    bannedWordList,
    final_transcript.replace("*", "").trim()
  )

  if (!cleanedText || cleanedText.trim() === "") {
    cleanedText = "Try Again!"
  }

  speechOutputElement.textContent = cleanedText
  speechOutputElement.classList.add("final")

  // Adjust text size based on length
  adjustTextSize(cleanedText, speechOutputElement)

  // Save and process the result
  
  embedSearchString(cleanedText, speechRecType)
  saveVoiceSearchData(cleanedText)
  
  // Show the prompt when there's a final result
  insertPrompt(output)
}

function adjustTextSize(cleanedText, speechOutputElement) {
  const textLength = cleanedText.length
  speechOutputElement.classList.remove(
    "speech-rec-small-text-resize",
    "speech-rec-medium-text-resize",
    "speech-rec-large-text-resize"
  )

  if (textLength <= 150) {
    speechOutputElement.classList.add("speech-rec-small-text-resize")
  } else if (textLength > 150 && textLength <= 250) {
    speechOutputElement.classList.add("speech-rec-medium-text-resize")
  } else {
    speechOutputElement.classList.add("speech-rec-large-text-resize")
  }
}

function removePrompt(output) {
  const promptElement =
    output.querySelector(".speak-prompt") ||
    output.querySelector(".speech-prompt")
  if (promptElement) {
    promptElement.remove()
  }
}

function initializeOutput(output) {
  // Remove existing content
  output.innerHTML = ""

  // Create a container for the speech output
  const speechOutput = document.createElement("div")
  speechOutput.classList.add("speech-output")

  // Insert the speech output into the output element
  output.appendChild(speechOutput)
}

function insertPrompt(output) {
  // Create the prompt element
  const prompt = document.createElement("div")
  prompt.classList.add("speech-prompt")

  // Use Unicode characters for arrows
  prompt.innerHTML = "&#x2B06; Choose! &#x2B06;" // Up arrow Unicode (⬆)

  // Insert the prompt at the beginning of the output container
  output.prepend(prompt)
}

// ... (The rest of your functions remain unchanged)

// Handle Unsupported Browser and Provide Fallback
function handleUnsupportedBrowser() {
  alert(
    "Speech recognition is not supported in your browser. Please use Chrome or another supported browser for this feature."
  )

  // Optionally, show a fallback input
  const fallbackDiv = document.getElementById("speechRec-fallback")
  if (fallbackDiv) {
    fallbackDiv.style.display = "block"
  }

  // Attach event listener to the submit button if fallback is provided
  const submitButton = document.getElementById("submit-manual-input")
  if (submitButton) {
    submitButton.addEventListener("click", () => {
      const manualInput = document.getElementById("manual-input").value.trim()
      if (manualInput) {
        // Process the manual input as needed
        console.log("Manual Input:", manualInput)
        embedSearchString(manualInput, "manual_input")
      }
    })
  }
}
