function generateCalendar() {
    const now = new Date();
    const today = now.getDate();
    const month = now.getMonth();
    const year = now.getFullYear();

    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);

    // Weekday headers
    const weekdays = ["S", "M", "T", "W", "T", "F", "S"];
    let calendarHtml = "<table><tr>";
    for (const day of weekdays) {
        calendarHtml += `<th>${day}</th>`; // Adding weekday headers
    }
    calendarHtml += "</tr><tr>";

    for (let i = 0; i < firstDayOfMonth.getDay(); i++) {
        calendarHtml += "<td></td>"; // Empty cells for days before the first of the month
    }

    for (let day = 1; day <= lastDayOfMonth.getDate(); day++) {
        if ((day + firstDayOfMonth.getDay() - 1) % 7 === 0) {
            calendarHtml += "</tr><tr>"; // Start a new row each week
        }

        let classes = "day-cell ";
        if (day === today) {
            classes += "current-day "; // Class for the current day
        }
        calendarHtml += `<td class='${classes}'>${day}</td>`;
    }

    calendarHtml += "</tr></table>";
    if (document.getElementById("calendar_grid").innerHTML = calendarHtml)
        return true;
    else
        return false;
}

function updateCalendarName() {
    const currentTime = new Date();
    const optionsDate = { month: 'long'};
    const formattedDate = currentTime.toLocaleDateString('en-US', optionsDate);
    document.getElementById("month_display").innerHTML = `${formattedDate}`;
}


//console.log('obeserving time' )

document.addEventListener('DOMContentLoaded', (event) => {
    generateCalendar();
    updateCalendarName();
});