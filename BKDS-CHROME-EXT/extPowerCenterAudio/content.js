// Define a mapping between filter categories and audio files
const audioMapping = {
    "POWER_REBOOT": chrome.runtime.getURL("audio/bkdsRestarting.mp3"),
    "POWER_SLEEP": chrome.runtime.getURL("audio/bkdsSleeping.mp3"),
    "POWER_SLEEP": chrome.runtime.getURL("audio/bkdsShowingDesktop.mp3")
};

// Attach an event listener to the icons
document.addEventListener('click', (event) => {
    const target = event.target.closest('.power_center_control');
    if (target) {
        const filterCategory = target.getAttribute('data-filter-category');
        const audioSrc = audioMapping[filterCategory];

        if (audioSrc) {
            const audio = new Audio(audioSrc);
            audio.play().catch((err) => console.error('Error playing audio:', err));
        }
    }
});
