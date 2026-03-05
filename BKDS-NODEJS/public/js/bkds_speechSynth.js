let currentAudio = null;
let currentChunkIndex = 0;
let chunks = [];
let isPaused = false;
const playbackRate = 0.75;

function handleTTS(target) {
    console.log('handleTTS() called for target:', target);

    // Get the subject title and category elements from the DOM
    const subjectTitleElement = document.querySelector('.insight-title');
    const subjectCategoryElement = document.querySelector('.insight-category');

    // Check if the elements exist
    if (!subjectTitleElement || !subjectCategoryElement) {
        console.warn('handleTTS(): Subject title or category element not found in the DOM.');
        return;
    }

    // Extract text content from the DOM elements
    const subjectTitle = subjectTitleElement.textContent.trim();
    const subjectCategory = subjectCategoryElement.textContent.trim();
    
    // Assuming `iconTitle` comes from the target's data or attribute
    const iconTitle = target.getAttribute('title') || target.textContent.trim();
    console.log('handleTTS() called for target:', iconTitle);

    // Call the readText function with the extracted content
    readText(subjectTitle, subjectCategory, iconTitle);
}


function readText(subjectTitle, subjectCategory, iconTitle) {

    console.log('readText(): ', iconTitle);

    const title = iconTitle.toLowerCase();

    if (title === "pause") {
        if (currentAudio) {
            currentAudio.pause();
            isPaused = true;
        } else if (isPaused) {
            currentAudio.play();
            isPaused = false;
        }
        return;
    } else if (title === "stop") {
        clearHighlights();
        if (currentAudio) {
            currentAudio.pause();
            currentAudio = null;
            isPaused = false;
        }
        return;
    } else if (title === "listen") {
        if (isPaused && currentAudio) {
            currentAudio.play();
            isPaused = false;
            return;
        } else if (!isPaused && !currentAudio) {
            const container = document.querySelector(`.${globalClasses.tts_listen}`);
            chunks = Array.from(container.querySelectorAll('span[id^="chunk-"]'));
            currentChunkIndex = 0;
            processChunks(subjectTitle, subjectCategory);
        } else if (isPaused) {
            currentAudio.play();
            isPaused = false;
        }
        return;
    }
}

function clearHighlights() {
    const functionName = clearHighlights.name;
    console.log(`${functionName} - Start`);

    const highlightedChunks = document.querySelectorAll(`.${globalClasses.tts_highlight}`);
    highlightedChunks.forEach(chunk => {
        console.log(`${functionName} - clearing chunk ${chunk}`);

        chunk.classList.remove(globalClasses.tts_highlight);
    });
}

async function processChunks(title, category) {
    console.log('processChunks:', title, category);
    console.log('chunks: ', chunks);
    console.log('chunks.length: ', chunks.length);

    for (let i = 0; i < chunks.length; i++) {
        console.log('processChunks:', i);
        await playNextChunk(chunks[i], title, category); // Pass playback rate
    }
}

function playNextChunk(chunkElement, title, category) {
    return new Promise((resolve, reject) => {
        const textChunk = chunkElement.textContent;
        highlightChunk(chunkElement);

        fetch(globalEndpoints.synth, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: textChunk, title: title, category: category })
        })
        .then(response => response.text())
        .then(url => {
            currentAudio = new Audio(url);
            currentAudio.playbackRate = playbackRate; // Set playback rate
            currentAudio.play();

            currentAudio.addEventListener('ended', () => {
                removeHighlight(chunkElement);
                resolve(); // Resolve the promise when the audio ends
            });

            currentAudio.addEventListener('error', (error) => {
                console.error('Audio playback error:', error);
                removeHighlight(chunkElement);
                reject(error); // Reject the promise if there's an error
            });
        })
        .catch(error => {
            console.error('Error:', error);
            reject(error); // Reject the promise if there's an error
        });
    });
}

function highlightChunk(chunkElement) {
    if (chunkElement) {
        chunkElement.classList.add('tts-highlight');
    }
}

function removeHighlight(chunkElement) {
    if (chunkElement) {
        chunkElement.classList.remove('tts-highlight');
    }
}

