// Function to unmute and set volume to 100%
function setYouTubeVolume() {
    const video = document.querySelector('video');
    if (video) {
      if (video.muted) {
        video.muted = false;  // Unmute the video
      }
      video.volume = 1.0;  // Set volume to 100%
    }
  }
  
  // Run the function when the DOM is ready and keep checking for new videos
  document.addEventListener('DOMContentLoaded', setYouTubeVolume);
  setInterval(setYouTubeVolume, 1000);  // Keep setting volume in case new videos load
  