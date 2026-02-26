

function findParentWithHref(element) {
    while (element && !element.href) {
        element = element.parentElement;
    }
    return element ? element.href : null;
}

function showBlockedMessage() {
    // Create a div to hold the "blocked" message
    const blockedMessage = document.createElement('div');
    blockedMessage.innerHTML = "<span>Link Blocked!<br><br>Try Another One!</span>";

    blockedMessage.style.display = 'flex'; // Use Flexbox model
    blockedMessage.style.justifyContent = 'center'; // Horizontally center content (works with flex)
    blockedMessage.style.alignItems = 'center'; // Vertically center content (works with flex)
    blockedMessage.style.textAlign = 'center';
    blockedMessage.style.fontSize = "23pt";
    blockedMessage.style.position = 'fixed';
    blockedMessage.style.top = '65%';
    blockedMessage.style.left = '80%';
    blockedMessage.style.transform = 'translate(-50%, -50%)';
    blockedMessage.style.background = 'white'; // background color
    blockedMessage.style.padding = '10px 20px';
    blockedMessage.style.borderRadius = '15px';
    blockedMessage.style.border = '5px solid red'; // 5px thick solid red border
    blockedMessage.style.zIndex = '9999';  // Ensure it appears on top of other content
    blockedMessage.style.height = '15%'; // 10% of screen height
    blockedMessage.style.width = '15%'; // 10% of screen width

    // Append to body
    document.body.appendChild(blockedMessage);

    // Remove after 2 seconds
    setTimeout(() => {
        blockedMessage.remove();
    }, 2000);
}

function checkClickedURL(event) {
    console.log('checkClickedURL', event.target.tagName)

    // List of allowed URLs
    const allowedURLs = [
        'wikipedia.org',
        'wikipedia.org',
        'wikidata.org',
        'nextspaceflight.com',
        'rocketLaunch.live',
        'rocketlaunch.live',
        'www.google.com/photos',
        'spacex.com',
        'en.wikipedia.org',
        'www.wikipedia.org',
        'flickr.com',
        'earth.google.com',
        'google.earth.com',
        'music.youtube.com',
        'youtube.com',
        '/search?q=',
        '/search?sca_esv',
        '/imgres?imgurl=',
        'data:image/',
        'localhost',
        'spacenews.com',
        'www.google.com/maps',
        'photos.google',
        'google.photos',
        'javascript:void(0);' // allows screenshot filter 
        ];

    //alert(event.target.tagName)
    
    if ((event.target.tagName === 'DIV' || event.target.tagName === 'A' || event.target.tagName === 'SPAN' || event.target.tagName === 'IMG' || event.target.tagName === 'H3')
        && event.target.parentElement.getAttribute('role') !== 'filter') {
        
        let href = findParentWithHref(event.target);
        //alert(href)
        let isAllowed = false;

        for (let i = 0; i < allowedURLs.length; i++) {
            // Convert both href and allowedURLs[i] to lowercase for case-insensitive comparison
            if (href && href.toLowerCase().includes(allowedURLs[i].toLowerCase())) {
                isAllowed = true;
        
                if (href.toLowerCase().includes("ytimg")) {
                    // If href includes "imgrefurl" and is a YouTube link
                    if (href.toLowerCase().includes("imgrefurl") || href.toLowerCase().includes("imgres")) {
                        // Use a regex to extract the desired URL from the href string
                        let match = href.match(/imgrefurl=([^&]*)/);
                        if (match && match[1]) {
                            href = decodeURIComponent(match[1]);  // Decode the URL to convert any encoded characters
                        }
                        window.location.href = href;  // Redirect the current window to the YouTube URL
                    }
                    return;  // Exit the function to prevent further processing
                }
                break;  
            }
        }        

        if (isAllowed ) {
            console.log('Clicked URL matches the list:', href);
            
        } else if(href) {
            showBlockedMessage();
            event.preventDefault();  // Prevent the link from being followed if it doesn't match
        }
    }  

}

function findParentWithHrefOrLpage(element) {
    while (element) {
        if (element.href) {
            return { type: 'href', value: element.href };
        }
        if (element.getAttribute('data-lpage')) {
            return { type: 'lpage', value: element.getAttribute('data-lpage') };
        }
        element = element.parentElement;
    }
    return null;
}


window.addEventListener('click', checkClickedURL);
