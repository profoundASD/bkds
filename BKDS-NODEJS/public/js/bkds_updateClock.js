function updateClock() {
    //console.log("updating clock");
    const now = new Date();
    const seconds = now.getSeconds();
    const minutes = now.getMinutes();
    let hours = now.getHours();
    //console.log("updating clock");
    //console.log("Now is: ", now);
    //console.log("seconds is: ", seconds);
    //console.log("minutes is: ", minutes);
    //console.log("hours is: ", hours);
    // Convert 24-hour format to 12-hour format
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    //console.log("hours is: ", hours);

    const secondHand = document.querySelector('.second-hand');
    const minsHand = document.querySelector('.minute-hand');
    const hourHand = document.querySelector('.hour-hand');

    const secondsDegrees = ((seconds / 60) * 360) + 90;
    const minsDegrees = ((minutes / 60) * 360) + ((seconds / 60) * 6) + 90;
    const hourDegrees = ((hours / 12) * 360) + ((minutes / 60) * 30) + 90;

    secondHand.style.transform = `rotate(${secondsDegrees}deg)`;
    minsHand.style.transform = `rotate(${minsDegrees-92}deg)`;
    hourHand.style.transform = `rotate(${hourDegrees-92}deg)`;
}


// This checks for the data and iterates a few times if no data before giving up */
// this data is loaded at runtime and the DOM might not be fully ready with all elements, this gives a few extra
// the wait time per JS can be overriden from the JSON plan
let ClockIntervalCount = 0;
const getClockIntervalId = setInterval(() => {
    let ClockCurrentScript = document.currentScript;
    let ClockMaxRuns = ClockCurrentScript ? parseInt(ClockCurrentScript.dataset.maxWait, 10) : 5; // Default to 5 if not specified
    ClockIntervalCount++;
    if (ClockIntervalCount >= ClockMaxRuns || updateClock()) {
        clearInterval(getClockIntervalId);
        setInterval(updateClock, 1000);

    }
}, 500);