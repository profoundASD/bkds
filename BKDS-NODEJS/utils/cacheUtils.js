// Function to check if the cache is still valid 
//default to 1 hour
function isCacheValid(cacheEntry, maxCacheAgeSeconds = 3600) {
    const now = new Date();
    if (!cacheEntry.timestamp) return false; // If there's no timestamp, cache is not valid
    const cacheAge = now.getTime() - cacheEntry.timestamp;
    const maxCacheAgeMillis = maxCacheAgeSeconds * 1000;
    return cacheAge < maxCacheAgeMillis; // Cache is valid if less than maxCacheAgeSeconds old
}


module.exports = { isCacheValid};