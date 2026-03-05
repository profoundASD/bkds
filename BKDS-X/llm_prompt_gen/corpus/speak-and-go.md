Feature Spotlight

# "Speak & Go"

To introduce the abstract concept of "search"—a function the user had no prior experience with—the nomenclature "Speak & Go" was utilized, inspired by the Texas Instruments _Speak & Read_. This familiar reference frame helped the user conceptualize speech synthesis and generation, transforming a complex digital task into a recognizable interaction similar to the childhood device his siblings once used. This scaffolding successfully accelerated adoption, enabling the transition from the nostalgic "Speak & Go" label to the standard utility of "Voice Search."

Inspiration: TI Speak & Read
[Joe Haupt](https://commons.wikimedia.org/wiki/File:TI_Speak_%26_Read,_with_booklet.jpg), CC BY-SA 2.0

Here is a look at the architecture, from the initial trigger to the final data persistence.

Demo Video 1: Real-time interim text rendering

## 1\. The Trigger: URL Parameters as Control Signals

The feature is designed to be launched not just by clicking an icon, but by external shortcuts (like a shell script or a specialized keyboard key). To achieve this, the application checks the URL query parameters immediately upon loading.

In `bkds_speechRec.js`, the `autoStartSpeechRecognition` function listens for a specific signal: `?startSpeech=true`. This allows the kiosk to wake up directly into "listening mode" without requiring a mouse click.


    // bkds_speechRec.js
    function autoStartSpeechRecognition() {
      const { startSpeech, type } = getQueryParams()

      if (startSpeech === "true" && type) {
        handleSpeechRecognitionClick(type)
      }
    }


When this triggers, the client fetches a dedicated UI partial from the server (`/speech`) and injects it into the main view, overlaying the content with a "Listening..." prompt.

## 2\. The Listener: Web Speech API Implementation

Once the UI is ready, the system initializes the **Web Speech API**. I specifically configured the `SpeechRecognition` instance to be both _continuous_ and to provide _interim results_. This is crucial for user feedback—it allows the UI to display the text _as the user is speaking_ (in gray) before solidifying it into the final transcript (in black).


    // bkds_speechRec.js
    recognitionInstance = new SpeechRecognition()
    recognitionInstance.continuous = true
    recognitionInstance.interimResults = true

    recognitionInstance.onresult = function (event) {
      // Loop through results to separate interim from final transcripts
      // ...
      updateOutput(final_transcript, interim_transcript, output, speechRecType)
    }


Speak & Go Voice Search Prompt - BKDS Forever U

Speak & Go Voice Search Prompt Response - BKDS Forever U

## 3\. The Rebound Effect: Continuous Recognition Loop

The system employs a continuous recognition loop that auto-restarts after every utterance, enabling seamless query correction. The session remains active until a destination is selected or the voice filter is toggled off.

Demo Video 1: Real-time interim text rendering

## 4\. The Filter: "Nuisance" Sanitization

A critical requirement for a public or semi-public kiosk is preventing inappropriate searches or accidental triggers. The system employs a "banned words" filter that runs on the client side before any search is executed.

The client fetches a cached list of banned words from the server (`/banned-words`). The `stripKeywords` function then normalizes the speech (removing punctuation and casing) and uses regex word boundaries to surgically remove unwanted terms from the final transcript.


    // bkds_speechRec.js
    function stripKeywords(keywords, speechResult) {
      const normalizedSpeechResult = normalizeSpeechResult(speechResult)

      keywords.forEach((keyword) => {
        const escapedKeyword = escapeRegExp(keyword)
        // Case-insensitive regex match for whole words
        const regex = new RegExp("\\b" + escapedKeyword + "\\b", "i")

        if (match) {
            // ... removal logic
        }
      })
      return speechResult
    }


If a user says a banned phrase, it is stripped out. If the entire query consists of banned words, the system defaults to a safe "Try Again!" prompt.

## 5\. The Handoff: Dynamic URL Injection

Once the speech is finalized and sanitized, the system doesn't just run a single search. It updates the entire "App Launch Toolbar" dynamically.

Using the `embedSearchString` function, the system targets the toolbar icons (Google, Wikipedia, YouTube) and replaces a placeholder token (`@@_search_term_@@`) in their standard URLs with the new sanitized transcript.

// bkds_speechRec.js const updatedUrl = originalUrl.replace( /@@search_term@@/g, encodeURIComponent(cleanedText) ) icon.href = updatedUrl icon.classList.add("search_result_pulsate")

Speak & Go Voice Search Prompt Keyword Injection & Selection - BKDS Forever U

Speak & Go Voice Search Landing / Customized Search Result Transformation - BKDS Forever U

## 6\. The Result: Transformed DOM Elements

Once the speech is captured and sanitized, the application updates the DOM in real-time. The `embedSearchString` function targets links with the class `desktop_search_speech_result` and injects the new query.

Snapshot of the generated HTML after a user has spoken the phrase "2008 Anderson Air Force Base B-2 accident" Notice how the `href` and `data-updated-url` attributes have been rewritten while preserving the `data-original-url` template for future searches.


    <a class="desktop_search_speech_result"
       data-original-url="https://earth.google.com/web/search/@@_search_term_@@"
       data-updated-url="https://earth.google.com/web/search/2008%20Anderson%20Air%20Force%20Base%20B-2%20accident"
       href="https://earth.google.com/web/search/2008%20Anderson%20Air%20Force%20Base%20B-2%20accident">
      Google Earth
    </a>

    <a class="desktop_search_speech_result"
       data-original-url="https://youtube.com/search/?q=@@_search_term_@@"
       data-updated-url="https://youtube.com/search/?q=2008%20Anderson%20Air%20Force%20Base%20B-2%20accident"
       href="https://youtube.com/search/?q=2008%20Anderson%20Air%20Force%20Base%20B-2%20accident">
      YouTube
    </a>


This allows the user to speak once, and then choose _where_ to send that query—whether to Google Images, Wikipedia, or a local file search—with a single tap.

## 7\. Persistence: Logging the Session

For analytics and debugging, the application persists every valid voice search to the server. The client-side `saveVoiceSearchData` function transmits the cleaned transcript and a timestamp to the Node.js backend.

On the server side (`bkds_router.js`), this payload is serialized into a JSON file within the `public/data/audio/speech/recognition/` directory. This creates a permanent, readable history of user interactions that exists independently of browser history.


    // bkds_router.js
    router.post(globalEndpoints.saveVoiceSearch, async (req, res) => {
      const { searchString, timestamp } = req.body;

      // Logic to write file as: BKDS_TTS_[SearchTerm]_VOICE_SEARCH_[Timestamp].json
      await fs.writeFile(outputFilePath, JSON.stringify(dataToSave, null, 2));
    });



    /* JSON Log: Sanitized Search Query */
    {
      "searchString": "Hello World Saved Search String",
      "timestamp": "2025-03-13T17:05:36.111Z"
    }


## 8\. Data Patterns & Future AI Integration

Reviewing these persisted logs reveals specific linguistic patterns that are difficult to handle with standard logic. The data highlights the limitations of current keyword stripping and points toward a need for Large Language Model (LLM) agents to handle complex intent.

###  The "Navigation Noise" Problem

Users frequently conflate the _search query_ with the _destination application_. For example, a user might say "F-16 Thunderbirds Little Rock Air Force Base" Currently, the system uses a hard-coded `bannedWordList` to strip terms like "Google Maps" or "Wikipedia" from the string.

While effective, this regex-based approach is a blunt instrument. It simply deletes the app name, even if the user intended to switch contexts—for example, asking for "Air Show Videos" (implied YouTube) but appending "Google Maps." The current logic sanitizes the string but cannot intelligently reroute the user to the correct view.


    /* JSON Log: Sanitized Search Query */
    {
      "searchString": "F-16 Thunderbirds Little Rock Air Force Base",
      "timestamp": "2025-03-13T17:05:36.111Z"
    }


###  The "Echolalia" Challenge

The complexity increases with circumstantial speech or echolalia, where a user may use elaborate, scripted phrases to refer to simple concepts. Simple regex heuristics struggle here because the redundancy is variable and highly context-dependent.

 In-Depth Report Reciting a Commercial Might Mean ‘Thank You’ Explore the mechanics of **Delayed Echolalia** and Gestalt Scripting. Includes a "Translation Matrix" for pop-culture quotes.    Complex Communication Context The Scenic Route vs. The Detour Distinguishing sensory needs and motor deficits from intent in neurodivergent speech.    System Architecture Decoding the Echo While neurotypical children typically process language analytically (word-by-word), many autistic individuals are Gestalt Language Processors (GLP).    Neurobiology Circumstantial Speech in Autism The Scenic Route vs. The Detour. Visualizing the difference between circular logic and tangential thinking in neurodivergent communication.

In the log below, the user is searching for the "Wings Over Houston" air show, but the input is wrapped in a specific, repetitive script regarding Texas. Standard assistants often fail here by attempting to parse every word as a literal command.


    /* JSON Log: Verbose/Scripted Input */
    {
      "searchString": "Harris County. Deep in the Heart of Texas. In the Lone Star State of Texas where Wings over Houston Fly. That's what I've been missing.",
      "timestamp": "2025-03-13T17:05:36.111Z"
    }


Complex Communication Needs - Circumstantial Speech Synthesis Challenge

**The Future Architecture:** Future iterations could allow caregivers to describe a user's complex communication tendencies in plain English, configuring the system to recognize specific idiolects. By training the application on common speech disorders—such as echolalia, which is often complex and combined with other divergences—the assistant could parse specific gestalt tendencies to provide real-time aid.

1\. User Input (Raw)

"Deep in the Heart of Texas..."

Complex / Scripted Speech

2\. Caregiver Context (LLM)

Translation Matrix

"Heart of Texas" = "Houston"

3\. System Action

Search: "Houston"

Sanitized Intent

Figure 1: The proposed "Context Injection" pipeline, where caregiver-defined rules resolve complex speech patterns.

This shifts the workflow from the current "loop-until-perfect" model to a seamless intent-based interaction. Instead of forcing the user to correct the text before selecting a destination, they could speak the query once. The agent would then translate the input, automatically building a custom results page and guiding the user through improved search results.
