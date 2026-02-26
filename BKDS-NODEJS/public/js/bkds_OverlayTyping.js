
// Display the message on the page
const el = document.getElementById('loading-overlay');

text='Going Home!'
// Function to add text to element one letter at a time
function typeWriter(text, i) {
    if (i < text.length) {
        el.innerHTML += text.charAt(i);
        i++;
        setTimeout(() => typeWriter(text, i), 50);
    }
}

const dynamicMessage = "Going Home!";
typeWriter(dynamicMessage, 0);

