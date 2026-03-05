// appCache.js

const defaultPage = 1;
const defaultLimit = 50;

let appCache = {
    iconCache: {},
    headerCache: {},
    subjectCache: {},    // Supports dynamic keys
    dataFileCache: {},   // Supports dynamic keys
    clusterCache: {},    // Supports dynamic keys
    filterCache: {}
};

const { isCacheValid } = require('../utils/cacheUtils'); // Adjust the path based on your directory structure


const routerGlobalAttributes = {
    POWER_SLEEP:'POWER_SLEEP',
    POWER_REBOOT:'POWER_REBOOT'
}

// Export the variables and appCache object
module.exports = {
    defaultPage,
    defaultLimit,
    appCache,
    isCacheValid,
    routerGlobalAttributes
};

