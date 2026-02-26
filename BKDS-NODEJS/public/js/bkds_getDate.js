function updateMonthDay() {
    
    const currentTime = new Date();
    const optionsDay = { weekday: 'long' };
    const optionsDate = { month: 'long', day: 'numeric' };
    const formattedDay = currentTime.toLocaleDateString('en-US', optionsDay);
    const formattedDate = currentTime.toLocaleDateString('en-US', optionsDate);

    const dateDisplayElement = document.getElementById("date_display");
    if (dateDisplayElement) {
        dateDisplayElement.innerHTML = `${formattedDay}<br>${formattedDate}`;
        return true;
    } else {
        return false;
    }
}

//console.log('obeserving')

// Call updateTime once and set an interval to update it every minute
document.addEventListener('DOMContentLoaded', () => {
    updateMonthDay();
});

