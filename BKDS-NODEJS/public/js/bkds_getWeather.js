// CONFIGURATION OBJECTS
const CONFIG = {
  api: {
    key: 'becf3070f7250aea3c8e52b03be3af6c',
    baseUrl: 'https://api.openweathermap.org/data/2.5/weather',
    iconUrl: 'http://openweathermap.org/img/wn/',
    units: 'imperial',
  },
  elements: {
    weatherStatsId: 'weather_stats',
  },
  geolocation: {
    notSupportedMessage: 'Geolocation is not supported by your browser for weather',
  },
  defaultOverrides: {
    locationName: {}, // e.g., { "White": "Searcy City" }
  },
};

const overrideConfig = {
  // Users can set these values to xoverride the default behavior
  manualZipCode: null, // e.g., '72370'
  customLocationNames: {
    // Example override
    // 'White': 'Searcy City',
        'North Little Rock' : 'Las Vegas',
        'White' : 'White County'
  },
};

// UTILITY FUNCTIONS
/**
 * Fetches geographic coordinates (latitude and longitude) for a given zip code.
 * Utilizes the OpenWeatherMap Geocoding API.
 * @param {string} zipCode - The zip code to geocode.
 * @returns {Promise<{ latitude: number, longitude: number }>}
 */
async function getCoordinatesByZip(zipCode) {
  const geoUrl = `https://api.openweathermap.org/geo/1.0/zip?zip=${zipCode}&appid=${CONFIG.api.key}`;
  try {
    const response = await fetch(geoUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch coordinates for zip code ${zipCode}: ${response.status}`);
    }
    const data = await response.json();
    return { latitude: data.lat, longitude: data.lon };
  } catch (error) {
    throw new Error(`Error fetching coordinates: ${error.message}`);
  }
}

/**
 * Constructs the weather API URL with given parameters.
 * @param {number} latitude
 * @param {number} longitude
 * @returns {string}
 */
function constructWeatherApiUrl(latitude, longitude) {
  return `${CONFIG.api.baseUrl}?lat=${latitude}&lon=${longitude}&units=${CONFIG.api.units}&appid=${CONFIG.api.key}`;
}

/**
 * Applies any configured overrides to the location name.
 * @param {string} originalName
 * @returns {string}
 */
function applyLocationNameOverrides(originalName) {
  return overrideConfig.customLocationNames[originalName] || originalName;
}

/**
 * Fetches weather data from the OpenWeatherMap API.
 * @param {number} latitude
 * @param {number} longitude
 * @returns {Promise<Object>}
 */
async function fetchWeatherData(latitude, longitude) {
  //console.log('weather: fetchWeatherData');
  const url = constructWeatherApiUrl(latitude, longitude);
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch weather data: ${response.status}`);
    }
    const forecastData = await response.json();
    return forecastData;
  } catch (error) {
    throw new Error(`Error fetching weather data: ${error.message}`);
  }
}

/**
 * Renders the weather data into the DOM.
 * @param {Object} forecastData
 */
function renderWeatherData(forecastData) {
  //console.log('Handling weather data...renderWeatherData');
  const originalLocName = forecastData.name;
  const locName = applyLocationNameOverrides(originalLocName);
  const weatherDesc = forecastData.weather[0].description;
  const weatherTemp = Math.round(forecastData.main.temp);
  const weatherFeelsLike = Math.round(forecastData.main.feels_like);
  const weatherIconURL = `${CONFIG.api.iconUrl}${forecastData.weather[0].icon}@2x.png`;

  const weatherHTML = `
    <div class="weather-container">
      <div>${locName}</div>
      <div>
        <img src="${weatherIconURL}" alt="${weatherDesc}">
      </div>
      <div class="weather-temp">
        ${weatherTemp}&deg;F
      </div>
      <div class="weather-desc">
        ${weatherDesc}<br>
        Feels like ${weatherFeelsLike}&deg;F
      </div>
    </div>`;

  const weatherStatsElement = document.getElementById(CONFIG.elements.weatherStatsId);
  if (weatherStatsElement) {
    weatherStatsElement.innerHTML = weatherHTML;
  } else {
    console.error(`Element with ID '${CONFIG.elements.weatherStatsId}' not found.`);
  }
}

/**
 * Retrieves the current geographic location of the user.
 * @returns {Promise<GeolocationPosition>}
 */
async function getCurrentLocation() {
  //console.log('Handling weather data...getCurrentLocation');
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(CONFIG.geolocation.notSupportedMessage);
    } else {
      navigator.geolocation.getCurrentPosition(resolve, reject);
      //console.log('weather: got weather');
    }
  });
}

/**
 * Handles the retrieval and rendering of weather data.
 * Applies manual overrides if configured.
 */
async function handleWeather() {
  //console.log('Handling weather data...');
  try {
    let latitude, longitude, locName;

    if (overrideConfig.manualZipCode) {
      //console.log(`Using manual zip code override: ${overrideConfig.manualZipCode}`);
      const coords = await getCoordinatesByZip(overrideConfig.manualZipCode);
      latitude = coords.latitude;
      longitude = coords.longitude;
      // Optionally, you can set a default override for location name based on zip code
      // For example, fetch location name from geocoding API if needed
    } else {
      const position = await getCurrentLocation();
      //console.log('weather position: ', position);
      latitude = position.coords.latitude;
      longitude = position.coords.longitude;
      //console.log('weather coordinates: ', latitude, longitude);
    }

    const forecastData = await fetchWeatherData(latitude, longitude);
    //console.log('weather forecast: ', forecastData);

    renderWeatherData(forecastData);
  } catch (error) {
    console.error('Error getting weather data:', error);
  }
}

/**
 * Observes the DOM for the addition of the weather stats element and initializes weather handling.
 */
function initializeWeatherHandling() {
  if (document.getElementById(CONFIG.elements.weatherStatsId)) {
    handleWeather();
  } else {
    const weatherObserver = new MutationObserver(mutations => {
      for (const mutation of mutations) {
        for (const node of mutation.addedNodes) {
          if (
            node instanceof Element &&
            (node.id === CONFIG.elements.weatherStatsId ||
              node.querySelector(`#${CONFIG.elements.weatherStatsId}`))
          ) {
            //console.log('Observing weather stats...');
            handleWeather();
            weatherObserver.disconnect();
            break;
          }
        }
      }
    });

    weatherObserver.observe(document.body, { childList: true, subtree: true });
  }
}

// EVENT LISTENERS
document.addEventListener('DOMContentLoaded', initializeWeatherHandling);
