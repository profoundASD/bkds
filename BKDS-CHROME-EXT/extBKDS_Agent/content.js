const floatingUI = document.createElement('div');
floatingUI.id = 'myFloatingUI';

const imagePaths = [
    '/images/bkds_UI_Home_alt.png',
    '/images/bkds_UI_show_desktop.png',
    '/images/bkds_UI_SpeakAndGo.png'
];

// Corresponding URLs for each image
const imageLinks = [
    'http://example.com/home',
    'http://example.com/desktop',
    'http://example.com/speakandgo'
];

function createImageLauncher() {
    const launcherDiv = document.createElement('div');
    launcherDiv.id = 'myImageLauncher';
    launcherDiv.style.display = 'flex';
    launcherDiv.style.justifyContent = 'space-evenly'; // Evenly space images
    launcherDiv.style.alignItems = 'center';
    launcherDiv.style.width = '100%'; // Take full width of the parent

    const imageFiles = [
        'bkds_UI_Home_alt.png',
        'bkds_UI_show_desktop.png',
        'bkds_UI_SpeakAndGo.png'
    ];

    imageFiles.forEach(file => {
        const imgWrapper = document.createElement('div');
        imgWrapper.style.display = 'inline-block';

        const img = document.createElement('img');
        img.src = chrome.runtime.getURL('images/' + file);
        img.style.width = '80px'; // Adjust as needed
        img.style.height = '80px'; // Adjust as needed

        imgWrapper.appendChild(img);
        launcherDiv.appendChild(imgWrapper);
    });

    return launcherDiv;
}


// Initially hidden
floatingUI.style.display = 'block';

// Function to toggle visibility
function toggleUI() {
    floatingUI.style.display = (floatingUI.style.display === 'none') ? 'flex' : 'none';
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((msg, sender, response) => {
    if (msg.toggle) {
        toggleUI();
    }
});

document.body.appendChild(floatingUI);

