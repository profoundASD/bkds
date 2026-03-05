// Function to change the background of the element with class "mw-mmv-close" to red and modify its click behavior
function changeCloseButtonBackground() {
    console.log('changeCloseButtonBackground Checking for element with class "mw-mmv-close"...');
    // Select the element with the class "mw-mmv-close"
    const closeButton = document.querySelector('.mw-mmv-close');

    // Check if the element exists
    if (closeButton) {
        console.log('Element with class "mw-mmv-close" found. Modifying behavior.');

        // Change the background color to red
        closeButton.style.backgroundColor = 'red';

        // Extract the base URL by removing everything after the '#'
        const originalURL = window.location.href.split('#')[0];
        console.log('Redirect URL:', originalURL);

        // Modify the button's click behavior
        closeButton.onclick = () => {
            console.log('Redirecting to:', originalURL);
            window.location.href = originalURL; // Redirect to the base URL
        };

        // Optionally, add an href attribute for accessibility (not required for button functionality)
        closeButton.setAttribute('href', originalURL);
        closeButton.setAttribute('title', 'Return to original page');

        // Disconnect the observer since the target element has been found and modified
        if (mutationObserver) {
            mutationObserver.disconnect();
            console.log('MutationObserver disconnected.');
        }
    } else {
        console.log('Element with class "mw-mmv-close" not found yet.');
    }
}

// Create a MutationObserver to watch for changes in the DOM
const mutationObserver = new MutationObserver(() => {
    // Call the function to check and modify the element
    console.log('changeCloseButtonBackground MutationObserver...');
    changeCloseButtonBackground();
});

// Initialize the MutationObserver to watch the body for changes
function initializeMutationObserver() {
    console.log('changeCloseButtonBackground initializeMutationObserver()');
    mutationObserver.observe(document.body, {
        childList: true, // Watch for direct child additions/removals
        subtree: true,   // Watch for changes in all descendants
    });
    console.log('MutationObserver initialized.');
}

// Run the observer when the page is fully loaded
window.addEventListener('load', () => {
    console.log('changeCloseButtonBackground Page loaded. Initializing MutationObserver...');
    initializeMutationObserver();
    // Initial check in case the element is already present
    changeCloseButtonBackground();
});
