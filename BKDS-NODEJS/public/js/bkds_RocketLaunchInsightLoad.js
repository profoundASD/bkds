function fetchAndProcessRocketLaunchData(callback) {
    const url = 'https://fdo.rocketlaunch.live/json/launches/next';
    //console.log(`Using ${url}`);
    //console.log("RL: fetchAndProcessRocketLaunchData");

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Failed to retrieve data. Status code: ${response.status}`);
            }
            //console.log("RL: got response.");
            return response.json();
        })
        .then(data => {
            if (!data || JSON.stringify(data).toLowerCase().includes("error")) {
                //console.log("RL:Data is null or contains an error.");
                callback(false); // Data error
                return;
            }
                // Extracting desired fields
                const launchData = data.result[0];
                const launchDescription = launchData.launch_description || '';
                const formattedLaunchDesc = splitStringByLength(launchDescription, 200);
                const formattedLaunchDescStr = formattedLaunchDesc.join('<br>');

                // Process 'quicktext' to extract the URL and make it a hyperlink
                const quickText = launchData.quicktext || '';
                const parsedQuickText = processQuickText(quickText);

                const estLaunchTime = convertToCentralTime(launchData.t0);
                const lastUpdateTime = convertToCentralTime(launchData.modified);
    
                const parsedData = {
                  //  'Mission ID': launchData.id,
                    'Mission': launchData.name,
                    //'Launch Pad': launchData.pad ? launchData.pad.id : null,
                    'Launch Pad': launchData.pad ? launchData.pad.location.name : null,
                    'Country': launchData.pad && launchData .pad.location.country ? launchData.pad.location.country : null,
                    'Description': formattedLaunchDescStr,
                    'Estimated Launch Time': estLaunchTime,
               //     'Launch Purpose': launchData.tags && launchData.tags.length > 0 ? launchData.tags[0].text : null,
                   // 'Quick Text': parsedQuickText.text,
                    'Last Update': lastUpdateTime
                };
                watchLink =parsedQuickText.url ? `<br><br><div class="watch-button"><a href="${parsedQuickText.url}" target="_blank">Get More Details</a></div>` : 'No URL Provided',
                //console.log("RL: displayData");

                displayData(parsedData,watchLink );

                callback(true); // Data processed successfully
                
            })
            .catch(error => {
                console.error(`Error: ${error.message}`);
                callback(false); // Fetch error
            });
    }
    function convertToCentralTime(utcTimestamp) {
        if (!utcTimestamp) return 'Unavailable';
        const date = new Date(utcTimestamp);
        const options = {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: 'numeric', minute: 'numeric', second: 'numeric',
            timeZone: 'America/Chicago', hour12: true
        };
        return date.toLocaleString('en-US', options) + ' Central';
    }
    // Function to process quicktext and extract URL
    function processQuickText(quickText) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        const found = quickText.match(urlRegex);
        const textWithoutUrl = quickText.replace(urlRegex, "").trim();
        
        return {
            text: textWithoutUrl,
            url: found ? found[0] : null
        };
    }
    // Utility function to split a string by length
    function splitStringByLength(str, maxLength) {
        const result = [];
        for (let i = 0; i < str.length; i += maxLength) {
            result.push(str.substring(i, i + maxLength));
        }
        return result;
    }

    // Function to display data
    function displayData(data, watchLink) {
        //console.log("RL: adding data and watch link");
        const container = document.getElementById('rocket-launch-text-descripton');
        container.innerHTML = ''; // Clear previous content
        Object.entries(data).forEach(([key, value]) => {
            if (value != null) {
                const div = document.createElement('div');
                div.innerHTML = `<strong>${key}:</strong> ${value}`;
                container.appendChild(div);

            }

        });
        container.innerHTML+=(watchLink);

    }

    document.addEventListener('DOMContentLoaded', () => {
        // Check if element exists
        const targetElement = document.getElementById('rocket-launch-text-descripton');
        if (targetElement) {
            fetchAndProcessRocketLaunchData((success) => {
                if (success) {
                    //console.log("Data fetched and processed successfully.");
                } else {
                    //console.log("An error occurred.");
                }
            });
        }
    });
    
