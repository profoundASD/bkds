// Global variable to hold the array of content
const contents = [
    { type: 'text', content: 'Hello Jason' },
    { type: 'text', content: 'Forever U' }
];

function typewriterEffect(elementId, text, speed) {
    let i = 0;
    const element = document.getElementById(elementId);
    element.innerHTML = ''; // Clear existing content

    function typeWriter() {
        if (i < text.length) {
            // Append the next character (including space) to the element's content
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(typeWriter, speed);
        }
    }

    typeWriter();
}

function updateHeaderContent(contents, time_interval) {
    //console.log('updateHeaderContent()');
    let currentIndex = 0;

    // Function to display the content
    function displayContent(currentIndex) {
        const content = contents[currentIndex];
        const headerElement = document.getElementById('dynamic-header-content');
        //console.log('updateHeaderContent content:', content);
        
        if (content.type === 'text') {
            // Create a temporary element to parse the HTML string
            const tempElement = document.createElement('div');
            tempElement.innerHTML = content.content;
            // Extract the text and use it in the typewriter effect
            typewriterEffect('dynamic-header-content', tempElement.innerText, 100);
        } else if (content.type === 'image') {
            headerElement.innerHTML = `<img src="${content.content}" alt="Header Image">`;
        }
    }

    // Immediately display the first content
    displayContent(currentIndex);

    // Update the content at set intervals
    setInterval(() => {
        currentIndex = (currentIndex + 1) % contents.length;
        displayContent(currentIndex);
    }, time_interval); // Change interval as needed
}

document.addEventListener('DOMContentLoaded', () => {
    // Call the updateHeaderContent function with global 'contents' and an interval of 5000ms (5 seconds)
    updateHeaderContent(contents, 15000);
});
