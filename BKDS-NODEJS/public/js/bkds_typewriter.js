function typewriterEffect(elementId, text, typingSpeed) {
    let i = 0;
    const element = document.getElementById(elementId);
    if (!element) {
        console.error(`Element with ID '${elementId}' not found.`);
        return;
    }
    
    element.innerHTML = "";

    function typing() {
        if (i < text.length) {
            element.innerHTML += `<span style="opacity: 1;">${text.charAt(i)}</span>`;
            i++;
            setTimeout(typing, typingSpeed);
        }
    }

    typing();
}

// Call the function with the ID of the element, the text, and the speed of typing (in milliseconds)
document.addEventListener('DOMContentLoaded', () => {
    typewriterEffect('dynamic-header-content','Hello Jason', 100);
});
