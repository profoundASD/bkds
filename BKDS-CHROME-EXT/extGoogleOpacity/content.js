document.addEventListener('DOMContentLoaded', () => {
    // Create the overlay
    const overlay = document.createElement('div');
    overlay.id = 'fade-in-overlay';
    document.body.appendChild(overlay);

    // Set up the fade-out logic
    setTimeout(() => {
        overlay.style.opacity = '0'; // Start fade-out
        setTimeout(() => {
            overlay.remove(); // Remove overlay after transition
        }, 2500); // Match the CSS transition duration
    }, 50); // Slight delay before fade-out starts
});
