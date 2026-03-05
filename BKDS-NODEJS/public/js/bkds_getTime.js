
function updateTime() {
    const currentTime = new Date();
    const optionsTime = { hour: 'numeric', minute: '2-digit', hour12: true };
    
    const formattedTime = currentTime.toLocaleTimeString('en-US', optionsTime);
    const timeDisplayElement = document.getElementById("time_display");
    
    if (timeDisplayElement) {
        timeDisplayElement.textContent = formattedTime;
    }
}

// Call updateTime once and set an interval to update it every minute
document.addEventListener('DOMContentLoaded', () => {
    updateNumericTime();
    setInterval(updateNumericTime, 60000); // Update time every minute
});




// Function to get the current time and format it as "HH:MM am/pm"
function updateNumericTime() {
    const timeDisplay = document.getElementById("time_display");
    
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'pm' : 'am';
    
    // Convert hours to 12-hour format
    hours = hours % 12;
    hours = hours ? hours : 12; // The hour '0' should be '12'
    
    // Pad minutes with a leading zero if necessary
    const minutesStr = minutes < 10 ? '0' + minutes : minutes;
    
    // Format time as "HH:MM am/pm"
    const timeString = `${hours}:${minutesStr} ${ampm}`;
    
    // Display the time
    timeDisplay.textContent = timeString;
}

// Call updateNumericTime every second to refresh the displayed time
setInterval(updateNumericTime, 1000);
