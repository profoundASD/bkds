// Function to add the 'touch-to-hear' class to elements with target classes
const addClassToElements = () => {
  const targetClasses = ["content", "body", "row", "column", "button"];
  targetClasses.forEach((targetClass) => {
      const elements = document.querySelectorAll(`.${targetClass}`);
      elements.forEach((element) => {
          element.classList.add("touch-to-hear");
      });
  });
};

// Initial run when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  addClassToElements();

  // Observe changes to the DOM for dynamically added elements
  const observer = new MutationObserver(() => {
      addClassToElements();
  });

  observer.observe(document.body, { childList: true, subtree: true });
});
