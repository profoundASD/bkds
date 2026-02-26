const path = require("path")
const fs = require("fs").promises
const { marked } = require("marked")
const jsdom = require("jsdom")
const { JSDOM } = jsdom
const DOMPurify = require("dompurify")(new JSDOM("").window)

router_state = "./bkds_router_functions_state"

// Import appCache and related variables
const {
  defaultPage,
  defaultLimit,
  appCache,
  isCacheValid,
} = require(router_state)


const tts_prefix ='bkds_tts'

// ###########################

// MAIN FUNCTIONS BEGIN

//###########################

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1)) // random index from 0 to i
    ;[array[i], array[j]] = [array[j], array[i]] // swap elements
  }
  return array
}

function processMedia(mediaData) {
  const images = mediaData.images
  const videos = mediaData.videos

  let defaultImage = null
  const featuredImages = []
  const galleryImages = []

  // Process images with label consideration
  images.forEach((img) => {
    const imageDetails = {
      img_url: img.img_url,
      img_title: img.img_title,
      img_url_id: img.img_url_id,
      img_desc1: img.img_desc1 || "",
      img_desc2: img.img_desc2 || "",
      img_desc3: img.img_desc3 || "",
      img_src: img.img_src || "",
      data_category: img.data_category || "",
      data_subject: img.data_subject || "",
    }
    switch (img.label) {
      case "default":
        // Ensure only the first default is set
        if (!defaultImage) defaultImage = imageDetails
        break
      case "featured":
        featuredImages.push(imageDetails)
        break
      default:
        galleryImages.push(imageDetails)
        break
    }
  })

  // Organize all images in the specified order: default, featured, gallery
  const orderedImages = []
  if (defaultImage) orderedImages.push(defaultImage)
  orderedImages.push(...featuredImages, ...galleryImages)

  // Videos are not categorized by label, just map them into desired structure
  const processedVideos = videos.map((vid) => ({
    vid_url: vid.vid_url,
    vid_thumb_url: vid.vid_thumb_url,
    vid_title: vid.vid_title,
    vid_url_id: vid.vid_url_id,
  }))

  return {
    images: orderedImages,
    videos: processedVideos,
  }
}



async function fetchAndTransformInsights(
  filterCategory = "main_feed",
  page = defaultPage,
  limit = defaultLimit
) {
  console.log("fetchAndTransformInsights()")
  // Create a unique cache key based on filterCategory, page, and limit.
  const cacheKey = `${filterCategory}_${page}_limit_${limit}_fetchAndTransformInsights`

  try {
    // Check cache validity. If invalid or missing, update the cache.
    if (
      !appCache.dataFileCache[cacheKey] ||
      !isCacheValid(appCache.dataFileCache[cacheKey], 3600)
    ) {
      //console.log("Updating cache:", cacheKey)

      // Define the file path based on the filter category.
      const dataFilePath = path.join(
        process.cwd(),
        "public",
        "data",
        "content_feeds",
        filterCategory,
        `${filterCategory}_batch.json`
      )

      // Read and parse the data file.
      const data = await fs.readFile(dataFilePath, "utf8")
      const parsedData = JSON.parse(data)

      // Implement pagination logic.
      const start = (page - 1) * limit
      const end = start + limit
      const paginatedData = parsedData.slice(start, end)

      // Transform each insight item and return a simplified structure.
      const transformedData = paginatedData.map(
        ({ insight_details, default_img, text_block = {}, media_link }) => {
          const {
            subject_title = "Title Missing",
            cluster_id = "No cluster_id",
            data_category = "Category Missing",
            data_category_id = "No data_category_id",
            url_id = "ID Missing",
          } = insight_details

          return {
            url_id,
            cluster_id,
            data_category,
            data_category_id,
            subject_title,
            default_img: default_img || "default image Missing",
            text_content: DOMPurify.sanitize(marked(text_block.content)) || "",
            media_link: media_link || null,
          }
        }
      )

      // Store the transformed data in the cache.
      appCache.dataFileCache[cacheKey] = {
        data: transformedData,
        timestamp: new Date().getTime(),
      }
    }

    //console.log("Using cache:", cacheKey)
    // Return the cached transformed data.
    return appCache.dataFileCache[cacheKey].data
  } catch (error) {
    console.error("Error fetching and transforming insights:", error)
    return []
  }
}

// Function to get icons data (from cache or file)
async function getIconsData() {
  const cacheKey = "icons"

  // Check if the cache exists and is valid
  if (
    !appCache.iconCache[cacheKey] ||
    !isCacheValid(appCache.iconCache[cacheKey])
  ) {
    console.log("Reading icons data from file and updating cache.")
    const iconDataPath = path.join(
      __dirname,
      "..",
      "public",
      "data",
      "config",
      "bkds_IconData.json"
    )
    const iconData = JSON.parse(await fs.readFile(iconDataPath, "utf8"))
    appCache.iconCache[cacheKey] = {
      data: iconData,
      timestamp: new Date().getTime(),
    }
  } else {
    console.log("Serving icons data from cache.")
  }

  // Access the cached data
  return appCache.iconCache[cacheKey].data
}

/**
 * Replaces @@_search_term_@@ in icon URLs with the given subject title.
 *
 * @param {Array} icons - The array of icon objects.
 * @param {string} subjectTitle - The subject title to replace in the URLs.
 * @returns {Array} - The updated array with replaced URLs.
 */
function updateIconUrls(icons, subjectTitle) {
  const cleanedTitle = encodeURIComponent(subjectTitle.trim())

  return icons.map((icon) => {
    if (icon.url && icon.url.includes("@@_search_term_@@")) {
      return {
        ...icon,
        url: icon.url.replace(/@@_search_term_@@/g, cleanedTitle),
      }
    }
    return icon
  })
}

// ###########################

// MAIN FUNCTIONS END

//###########################

// Export the helper functions
module.exports = {
  shuffleArray,
  processMedia,
  fetchAndTransformInsights,
  getIconsData,
  updateIconUrls,
  tts_prefix
  // Export other helper functions as needed
}
