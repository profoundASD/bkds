(function () {
  const tryAutoplay = () => {
    // Find the video element
    const videoElement = document.querySelector('video');

    if (videoElement) {
      // Ensure video is muted before trying to autoplay to avoid browser restrictions
      videoElement.muted = true;

      // Try playing the video
      videoElement.play().catch((error) => {
        console.warn('Autoplay failed:', error);
      });
    } else {
      console.warn('No video element found on the page.');
    }
  };

  // Use MutationObserver to handle dynamic loading of video elements (YouTube's SPA behavior)
  const observer = new MutationObserver(() => {
    const videoElement = document.querySelector('video');
    if (videoElement) {
      observer.disconnect(); // Stop observing once the video element is found
      tryAutoplay();
    }
  });

  // Start observing changes in the DOM
  observer.observe(document.body, { childList: true, subtree: true });

  // Run once immediately in case the video is already loaded
  tryAutoplay();
})();
