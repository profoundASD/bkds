// background.js

// Listen for any new tab being created
chrome.tabs.onCreated.addListener((newTab) => {
  manageTabs(newTab.windowId);
});

// Listen for any tab being updated (e.g., navigation)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // Optional: Implement if you need to handle specific tab updates
});

// Listen for any window being focused or changed
chrome.windows.onFocusChanged.addListener((windowId) => {
  // Optional: Implement if you need to handle window focus changes
});

/**
* Manages open tabs within a specific window.
* Ensures only the active tab remains open.
* @param {number} windowId - The ID of the window to manage tabs for.
*/
function manageTabs(windowId) {
  chrome.tabs.query({ windowId: windowId }, (tabs) => {
      if (tabs.length <= 1) {
          // Only one tab is open in this window; no action needed
          return;
      }

      // Identify the active tab in the window
      const activeTabs = tabs.filter(tab => tab.active);
      if (activeTabs.length === 0) {
          // No active tab found; select the first tab as active
          chrome.tabs.update(tabs[0].id, { active: true });
          return;
      }

      const activeTab = activeTabs[0];

      // Iterate through all tabs and close those that are not active
      tabs.forEach(tab => {
          if (tab.id !== activeTab.id) {
              // Avoid closing internal Chrome pages
              if (tab.url && !isInternalURL(tab.url)) {
                  chrome.tabs.remove(tab.id, () => {
                      if (chrome.runtime.lastError) {
                          console.error(`Error closing tab ${tab.id}:`, chrome.runtime.lastError);
                      } else {
                          console.log(`Closed tab ${tab.id} (${tab.url})`);
                      }
                  });
              }
          }
      });
  });
}

/**
* Checks if a URL is an internal Chrome URL.
* @param {string} url - The URL to check.
* @returns {boolean} - True if it's an internal Chrome URL, false otherwise.
*/
function isInternalURL(url) {
  return url.startsWith("chrome://") || url.startsWith("chrome-extension://") || url.startsWith("chrome.google.com");
}
