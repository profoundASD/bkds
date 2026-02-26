chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    if (
      tab.url.includes('https://www.youtube.com') ||  // Full version
      tab.url.includes('https://youtube.com') ||       // Shortened main URL
      tab.url.includes('https://m.youtube.com') ||     // Mobile version
      tab.url.includes('https://youtu.be')             // Shortened video links
    ) {
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['content.js']
      });
    }
  }
});
