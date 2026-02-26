// ###########################
// IMPORTS AND SETUP
// ###########################
const express = require('express');
const path = require('path');
const router = express.Router();
const fs = require('fs').promises;
const crypto = require('crypto');
const os = require('os');
const { exec } = require('child_process');
const fetch = require('node-fetch');
const { marked } = require('marked');
const jsdom = require('jsdom');
const { JSDOM } = jsdom; 
const DOMPurify = require('dompurify')(new JSDOM('').window);
const globalEndpoints = require('../public/js/bkds_endPoints.js'); // Adjust path as needed
const logger = require('../bkds_nodeLogger.js'); // Adjust path as needed

router.use(express.json()); 

// Google Cloud Text-to-Speech client
const textToSpeech = require('@google-cloud/text-to-speech');

// Import application cache and helper functions
const { isCacheValid, defaultLimit, appCache, tts_prefix } = require('./bkds_router_functions_state');
const { shuffleArray, processMedia, fetchAndTransformInsights, getIconsData, updateIconUrls } = require('./bkds_router_functions');
rootNode= 'http://localhost:3000'


// ###########################
// CONSTANTS AND PATH SETUP
// ###########################

// Base directory paths
const BASE_DIR = {
    bkdsApp: process.env.BKDS_APP,
    nodeJsPublic: process.env.BKDS_NODEJS_DATA, 
    desktop: process.env.BKDS_DESKTOP,
    backend: process.env.BKDS_BACKEND,
    auto_config_base: process.env.BKDS_AUTO,
    base_relative_speech_path: '/audio/speech', // For client-side paths 
};

// Specific base paths within the BKDS app
const BASE_PATHS = {
    desktop_shell_script_base: path.join(BASE_DIR.desktop, 'shell'),
    config: path.join(BASE_DIR.nodeJsPublic, 'config'), 
    reporting: path.join(BASE_DIR.auto_config_base, 'reporting', 'data'), 
    images: path.join(BASE_DIR.nodeJsPublic, 'images'), 
    mp3_audio_speech: path.join(BASE_DIR.nodeJsPublic, BASE_DIR.base_relative_speech_path), 
};

// Paths for specific files
const today = new Date();
const YYYYMMDD = today.toISOString().slice(0, 10).replace(/-/g, '');
const hostname = os.hostname();

const FILE_PATHS = {
    headerContent: path.join(BASE_PATHS.config, 'bkds_headerContent.json'),
    bannedWordFilePath: path.join(BASE_PATHS.config, 'bkds_bannedWords.json'),
    ttsAPI: path.join(BASE_PATHS.config, 'bkds_tts_api.json'),
    masterImage: path.join(BASE_PATHS.images, 'master_image_index.json'),
    mp3_audio_rec: path.join(BASE_PATHS.mp3_audio_speech, 'recognition'),
    mp3_audio_synth: path.join(BASE_PATHS.mp3_audio_speech, 'synthesis'),
    client_relative_synth_path: path.join('data', BASE_DIR.base_relative_speech_path, 'synthesis'),
    screenshot_dir: path.join(BASE_PATHS.reporting, hostname, YYYYMMDD, 'BKDS_AUTO_STEP_REPORTING_SCREENSHOTS')
};
// ###########################q
// SHELL CONFIGURATION
// ###########################

const SHELL_CONFIG = {
    BashShellPath: '/usr/bin/bash',
    scriptName: 'bkds_DesktopControl.sh',
    batch_id: 'BKDS_DESKTOP_CONTROL_UI'
};

// ###########################
// FUNCTIONS SETUP
// ###########################


// ###########################
// UTILITY FUNCTIONS
// ###########################

// Function to sanitize input (replaces special characters)
const sanitizeInput = (input) => input.replace(/[,\-:&\/.\s?]/g, '_');

// ###########################
// ROUTER SETUP AND MIDDLEWARE
// ###########################

// Parse incoming JSON

// ###########################
// ROUTES
// ###########################


router.post(globalEndpoints.synth, async (req, res) => {
    const { text, title, category } = req.body;
    logger.info('Received request for text-to-speech synthesis: ', { text, title, category });

    // Utility function to clean and preprocess strings (unchanged)
    const cleanString = (input) => {
        return input
            .toLowerCase() // Convert to lowercase first
            .replace(/^(related to|category):?\s*/i, '') // Remove prefixes
            .replace(/[^a-zA-Z0-9_]/g, '') // Remove punctuation, but keep underscores
            .replace(/\s+/g, '_');  // Replace spaces with underscores
    };

    // Clean and preprocess inputs
    const filePrefix = 'BKDS_TTS'; 
    const cleanTitle = cleanString(title);
    const cleanCategory = `${cleanString(category)}`;
    const truncatedTitle = `${filePrefix}_${cleanTitle.substring(0, 30)}`; 

    // Generate the filename 
    const md5TextHash = crypto.createHash('md5').update(text).digest('hex');
    const fileName = `${truncatedTitle}_${md5TextHash}.mp3`;

    // Construct the output directory and file path (using FILE_PATHS)
    const outputDir = path.join(FILE_PATHS.mp3_audio_synth, cleanCategory, truncatedTitle); 
    // Construct the public-facing path (consistent with outputFilePath)
    const speechSynthPath = path.join(outputDir, fileName); 
    // Load the service account key JSON file
    const keyFilename = FILE_PATHS.ttsAPI;
    // Construct the relative path for the client (using FILE_PATHS)
    const relativePath = path.join(FILE_PATHS.client_relative_synth_path, cleanCategory, truncatedTitle, fileName); 

    // Create a client with the service account
    const client = new textToSpeech.TextToSpeechClient({ keyFilename });

    try {
        // Ensure the output directory exists
        await fs.mkdir(outputDir, { recursive: true });
        logger.info(`Checked/created directory: ${outputDir}`);

        // Check if the file already exists
        try {
            await fs.access(speechSynthPath);
            logger.info(`Audio file already exists: ${speechSynthPath}`);
            return res.send(relativePath); // Return existing file path if it exists
        } catch {
            logger.info('File does not exist. Proceeding to synthesize speech.');
        }

        // Prepare the TTS synthesis request
        const request = {
            input: { text },
            voice: { languageCode: 'en-US', ssmlGender: 'NEUTRAL' },
            audioConfig: { audioEncoding: 'MP3' },
        };

        // Synthesize speech and write the file
        const [response] = await client.synthesizeSpeech(request);
        await fs.writeFile(speechSynthPath, response.audioContent, 'binary');
        logger.info(`Audio file created: ${speechSynthPath}`);
        res.send(relativePath); // Send relativePath to client

    } catch (error) {
        logger.error(`Error during speech synthesis: ${error}`);
        res.status(500).send('Error synthesizing speech');
    }
});


// Endpoint to receive UI messages from a shell script and update the UI dynamically
router.post(globalEndpoints.uiMessage, (req, res) => {
    const { message } = req.body;

    // Log the received message for debugging purposes
    //logger.info('Received UI message from shell script:', message);

    // Render the EJS partial using the received message
    res.render('_powerCenterTerminal', { message, layout: false }, (err, html) => {
        if (err) {
            // Handle rendering errors and log the issue
            logger.error(`Error rendering _powerCenterTerminal partial: ${err}`);
            return res.status(500).json({ error: 'Failed to render the message' });
        }

        // Successfully render the HTML and send it back to the client
        res.status(200).send(html);
    });
});


router.get(globalEndpoints.appToolbar, async (req, res) => {
    // Check if search terms are already cached
    if (!appCache.searchTerms) {
        const {
            generalSearches,
            earthSearches,
            mapsSearches,
            wikimediaSearches,
            wikipediaSearches,
            youtubeSearches
        } = require('./searchTerms.js'); // Load and cache

        appCache.searchTerms = {
            generalSearches,
            earthSearches,
            mapsSearches,
            wikimediaSearches,
            wikipediaSearches,
            youtubeSearches
        };
    }

    const { generalSearches, earthSearches, mapsSearches, wikimediaSearches, wikipediaSearches, youtubeSearches } = appCache.searchTerms;

    try {
        // Fetch icons for both toolbar_search and voice_search_general
        const response = await fetch(`${rootNode}${globalEndpoints.icons}?type=toolbar_search`);

        if (!response.ok) {
            throw new Error('Failed to fetch icons');
        }

        const iconsData = await response.json();

        // Process the iconsData to replace '@@_search_term_@@' with random terms
        iconsData.forEach(icon => {
            let url = icon.url;
            icon.dataOriginalUrl = url; // Store the original URL template

            let searchPool = generalSearches;

            if (url) {
                if (url.includes('earth.google') || url.includes('google.com/earth')) {
                    searchPool = [...generalSearches, ...earthSearches];
                } else if (url.includes('maps.google') || url.includes('google.com/maps')) {
                    searchPool = [...generalSearches, ...mapsSearches];
                } else if (url.includes('wikimedia')) {
                    searchPool = [...generalSearches, ...wikimediaSearches];
                } else if (url.includes('wikipedia')) {
                    searchPool = [...generalSearches, ...wikipediaSearches];
                } else if (url.includes('youtube')) {
                    searchPool = [...generalSearches, ...youtubeSearches];
                }

                const shouldUseRandomString =
                    searchPool.length > 0 &&
                    (icon.filterCategory.includes('_general') ||
                        icon.filterCategory.includes('_default') ||
                        url.includes('wikimedia') ||
                        url.includes('wikipedia') ||
                        url.includes('google.com/images') ||
                        url.includes('images.google.com') ||
                        (url.includes('https://youtube') && new Date().getMinutes() % 2 !== 0));

                if (shouldUseRandomString && url.includes('@@_search_term_@@')) {
                    const randomString =
                        searchPool[Math.floor(Math.random() * searchPool.length)];
                    url = url.replace('@@_search_term_@@', encodeURIComponent(randomString));
                    icon.url = url; // Update the icon's URL
                } else if (url.includes('/search')) {
                    url = url.split('/search')[0];
                    icon.url = url; // Update the icon's URL
                }
            }
        });

        // Render the template with the processed iconsData
        res.render('_appLaunchToolbar', { iconsData, layout: false });

    } catch (error) {
        logger.error(`Error in /appLaunchToolbar: ${error}`);
        res.status(500).send('Internal Server Error');
    }
});


router.post(globalEndpoints.saveVoiceSearch, async (req, res) => {
    
    const { searchString, timestamp } = req.body;
    logger.info(`Received voice search data: ${timestamp}`);

    const VOICE_SEARCH_DIR = FILE_PATHS.mp3_audio_rec;
    const file_prefix='BKDS_TTS'
    const file_pattern='VOICE_SEARCH'
    const out_type='json'
    const utcTimestamp = new Date().toISOString().replace(/[:.]/g, '-');

    // Clean and preprocess the search string for the file name
    let cleanSearchString = searchString
        .replace(/[^a-zA-Z0-9\s]/g, '') // Remove all punctuation
        .replace(/\s+/g, '_'); // Replace spaces with underscores

    // Truncate the string to ensure the filename length is manageable
    const truncatedSearchString = cleanSearchString.substring(0, 30);
    const fileName = `${file_prefix}_${truncatedSearchString}_${file_pattern}_${utcTimestamp}.${out_type}`;
 
    // Ensure the output directory exists
    try {
        await fs.mkdir(VOICE_SEARCH_DIR, { recursive: true });
        //logger.info(`Checked/created directory: ${VOICE_SEARCH_DIR}`);
    } catch (error) {
        logger.error(`Error creating directory: ${error}`);
        return res.status(500).send('Error saving voice search data');
    }

    // Construct the full file path
    const outputFilePath = path.join(VOICE_SEARCH_DIR, fileName);

    // Prepare the data to be saved
    const dataToSave = {
        searchString,
        timestamp,
    };

    // Save the data to a JSON file
    try {
        await fs.writeFile(outputFilePath, JSON.stringify(dataToSave, null, 2));
        logger.info(`Voice search data saved: ${outputFilePath}`);
        res.sendStatus(200);
    } catch (error) {
        logger.error(`Error saving voice search data: ${error}`);
        res.status(500).send('Error saving voice search data');
    }
});


// Endpoint to serve bannedWordList from a JSON file
router.get(globalEndpoints.bannedWords, async (req, res) => {
    logger.info(globalEndpoints.bannedWords);
    const CACHE_EXPIRATION_SECONDS = 3600; // 1 hour

    try {
        // Check cache validity
        if (!appCache.bannedWords || !isCacheValid(appCache.bannedWords, CACHE_EXPIRATION_SECONDS)) {
            logger.info('Cache miss or expired. Reading banned words from file.');
            const data = await fs.readFile(FILE_PATHS.bannedWordFilePath, 'utf8');
            const bannedWords = JSON.parse(data).bannedWordList;

            appCache.bannedWords = {
                data: bannedWords,
                timestamp: Date.now(),
            };
        } else {
            logger.info('Serving banned words from cache.');
        }

        res.json({ bannedWords: appCache.bannedWords.data });
    } catch (error) {
        logger.error(`Error reading banned words: ${error}`);
        res.status(500).send('Error loading banned words');
    }
});



router.get(globalEndpoints.speechRec, (req, res) => {
    logger.info(globalEndpoints.speechRec);

    const type = req.query.type || 'voice_search_general';
    let message = "Listening...";

    if (type.includes("flickr")) {
        message = "Listening for Flickr";
    } else if (type.includes("wikipedia")) {
        message = "Listening for Wikipedia";
    } else if (type.includes("wikimedia")) {
        message = "Listening for Wikimedia";
    } else if (type.includes("google")) {
        message = "Listening for Google Images";
    } else{
        message ="Listening...";
    }

    res.render('_speechRec', { title: '', message, layout: false });
})

// POST route to execute a power command
router.post(globalEndpoints.executePower, async (req, res) => {
    logger.info(globalEndpoints.executePower);

    const { powerAction } = req.body;
    logger.info(`powerAction using ${powerAction}`);

    // Validate that the powerAction parameter exists and is a string
    if (!powerAction || typeof powerAction !== 'string') {
        return res.status(400).json({ error: 'Invalid power action specified' });
    }

    try {
        // Construct the full script path and command
        const scriptPath = path.join(BASE_PATHS.desktop_shell_script_base, SHELL_CONFIG.scriptName);
        const command = `${SHELL_CONFIG.BashShellPath} ${scriptPath} ${SHELL_CONFIG.batch_id} ${powerAction}`;

        logger.info(`Executing command: ${command}`);

        // Execute the command
        exec(command, (error, stdout, stderr) => {
            if (error) {
                logger.error(`Error executing command: ${error.message}`);
                return res.status(500).json({ error: error.message });
            }

            if (stderr) {
                logger.error(`Standard error: ${stderr}`);
                // Continue execution even if there's stderr output
            }

            logger.info(`Standard output: ${stdout}`);
            res.status(200).json({ message: 'Command executed successfully', output: stdout });
        });
    } catch (err) {
        logger.error(`Error in execute-power-command: ${err.message}`);
        res.status(500).json({ error: 'Failed to play audio or execute command' });
    }
});

router.post(globalEndpoints.photosFullscreen, (req, res) => {
    logger.info(`${globalEndpoints.photosFullscreen}`);

    const images = req.body.images;
    const currentImage = req.body.currentImage || 0;

    if (!images || !Array.isArray(images) || images.length === 0) {
        logger.error('No images data received.');
        // Skip rendering and return an empty response
        return res.status(200).send('');
    }

    try {
        // Render the _photoGallery partial with provided images
        res.render('_photoGallery', {
            images: images,
            currentImage: currentImage,
            layout: false
        }, (err, html) => {
            if (err) {
                logger.error(`Error rendering HTML: ${err}`);
                res.status(500).send('Error rendering HTML');
            } else {
                res.send(html); // Send the rendered HTML directly
            }
        });
    } catch (error) {
        logger.error(`Error rendering images: ${error}`);
        res.status(500).send('Failed to render images');
    }
});


router.get(globalEndpoints.imageGrid, async (req, res) => {
    logger.info(globalEndpoints.imageGrid);

    const type = req.query.type;
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 20;

    if (!type || type.trim() === '') {
        logger.info('Type is empty or undefined. No action taken.');
        return res.status(200).send('');
    }

    logger.info('Using image-grid page: ', page);
    logger.info('Using image-grid type: ', type);

    try {
        // Use BASE_PATHS.images instead of hardcoded path
        const jsonFilePath = path.join(BASE_PATHS.images, `master_image_${type}_index.json`); 
        const jsonData = await fs.readFile(jsonFilePath, 'utf8');
        const allImages = JSON.parse(jsonData);

        // Paginate images
        const startIndex = (page - 1) * limit;
        const endIndex = page * limit;
        const paginatedImages = allImages.slice(startIndex, endIndex);

        // Render the '_imageGrid' partial with the images
        res.render('_imageGrid', {
            paginatedImages: paginatedImages,
            layout: false
        });
    } catch (error) {
        logger.error(`Error fetching images: ${error}`);
        res.status(500).send('Failed to fetch images');
    }
});



// Endpoint to provide default content for "main" mode
router.get(globalEndpoints.refreshContent, async (req, res) => {
    try {
      // Fetch main feed insights without pagination (all insights)
      logger.info(globalEndpoints.refreshContent);
      const subjectInsights = await fetchAndTransformInsights('main_feed');

      // Fetch icons data
      const iconsData = await getIconsData();

      // Filter the icons for various toolbar sections
      const powerCenterIcons = iconsData.filter(icon => icon.type === 'power_center_control');
      const desktopControlIcons = iconsData.filter(icon => icon.type === 'desktop_control_icon');
      const photoGalleryFilterIcons = iconsData.filter(icon => icon.type.startsWith('desktop_app_search'));
      const categoryResponse = await fetch(`${rootNode}${globalEndpoints.dataCategoryFilters}?type=category`);
      const dataCategoryFilters = await categoryResponse.json();
      const toolbarIconsData = iconsData.filter(icon => icon.type.startsWith('toolbar_search'));

      // Set photoGridType to 'default' and pass an empty array for paginatedImages
      const photoGridType = 'default';
      const paginatedImages = []; // Empty array initially

      res.render('_home', {
          title: 'Hello Jason Home',
          subjectInsights,
          powerCenterIcons,
          desktopControlIcons,
          photoGalleryFilterIcons,
          dataCategoryFilters,
          toolbarIconsData,
          photoGridType,
          paginatedImages

      });
      
    } catch (error) {
        logger.error(`Error rendering home page: ${error}`);
        res.status(500).send('Internal Server Error');
    }
});




router.get(globalEndpoints.headerContent, async (req, res) => {
    const dataFilePath = headerContent;
    const cacheKey = 'headerContent';
    logger.info(globalEndpoints.headerContent);
    // Example route with custom cache expiration (e.g., 30 minutes)
    const CACHE_EXPIRATION_SECONDS = 1800; // Set cache expiration for this route

    try {
        // Check if the cache exists and is still valid
        if (!appCache.headerCache[cacheKey] || !isCacheValid(appCache.headerCache[cacheKey], CACHE_EXPIRATION_SECONDS)) {
            logger.info('Cache miss or expired. Reading from file.');
            
            const data = await fs.readFile(dataFilePath, 'utf8');
            appCache.headerCache[cacheKey] = {
                data: JSON.parse(data), 
                timestamp: new Date().getTime() 
            };
        } else {
            logger.info('Serving header content from cache.');
        }

        // Respond with the cached header content
        res.json(appCache.headerCache[cacheKey].data);

    } catch (error) {
        logger.error(`Error: ${error}`);
        res.status(500).send('Error reading the JSON file');
    }
});

router.get(globalEndpoints.dataCategoryFilters, async (req, res) => {
    logger.info(globalEndpoints.dataCategoryFilters);

    const { type } = req.query;
    const cacheKey = `dataCategoryFilters_${type}`;
    const indexFilePath = path.join(
        __dirname,
        '..',
        'public',
        'data',
        'content_feeds',
        'bkds_data_category_filter_index.json'
    );
    const CACHE_EXPIRATION_SECONDS = 3600; // You can adjust this as needed

    try {
        // Check if cache exists and is still valid
        if (appCache.filterCache?.[cacheKey] && isCacheValid(appCache.filterCache[cacheKey], CACHE_EXPIRATION_SECONDS)) {
            logger.info(`Serving data from cacheKey ${cacheKey}`);
            return res.json(appCache.filterCache[cacheKey].data);
        } else {
            logger.info('Not serving data from cache for cachekey: ', cacheKey);
        }

        // Read data from file if not cached or cache is expired
        logger.info('Reading data from file:', indexFilePath);
        const data = await fs.readFile(indexFilePath, 'utf8');
        const indexData = JSON.parse(data);

        // Ensure valid JSON structure (should be an array)
        if (!Array.isArray(indexData)) {
            throw new Error('Invalid JSON structure: data is not an array');
        }

        // Filter and sanitize data
        const filteredData = indexData
        .filter(item => item.type === type)
        .map(item => ({
            ...item,
            filter_name: item.filter_name.replace(/[\s,]/g, '_'),
        }));    

        // Cache the filtered data with a timestamp
        appCache.filterCache[cacheKey] = { 
            data: filteredData, 
            timestamp: new Date().getTime()  // Store the current time to check cache expiration
        };

        // Respond with the filtered data
        res.json(filteredData);
    } catch (error) {
        logger.error(`Error fetching or processing data: ${error}`);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});


router.get(globalEndpoints.insightStoryContent, async (req, res) => {
    logger.info(globalEndpoints.insightStoryContent);
    try {
        const { postId, filterCategory, clusterID, categoryID } = req.query;
        const cacheKey = `${clusterID}_${categoryID}_${filterCategory}_${postId}`;
        const dataFilePath = path.join(
          process.cwd(),
          'public',
          'data',
          'content_feeds',
          filterCategory,
          clusterID,
          postId,
          `${postId}_${filterCategory}.json`
        );
    
        // Fetch icons data with retry logic
        let iconsData = {};
        try {
          iconsData = await getIconsData();
        } catch (error) {
          logger.warn('Error fetching icons data:', error.message);
        }
        
        const CACHE_EXPIRATION_SECONDS = 3600; 
        // Serve from cache if valid
        if (appCache.clusterCache?.[cacheKey] && isCacheValid(appCache.clusterCache[cacheKey], CACHE_EXPIRATION_SECONDS)) {
            logger.info('Serving content from cache for key:', cacheKey);
            return renderInsightStory(appCache.clusterCache[cacheKey].data, iconsData);
        }else{
            logger.info('Not serving content from cache for key:', cacheKey);
        }

        // Check if JSON data file exists
        try {
            //logger.info(`\nTrying ${dataFilePath}`);
            await fs.access(dataFilePath);
        } catch (err) {
            logger.warn('JSON file not found:', dataFilePath);
            return res.status(404).render('error', { error: 'Insight data not found.' });
        }

        // Read and parse JSON data
        //logger.info(`\n\nawaiting dataFilePath ${dataFilePath}`);
        const fileData = await fs.readFile(dataFilePath, 'utf8');
        const jsonData = JSON.parse(fileData);
        //logger.info(`\n\got fileData from ${dataFilePath}`);


        // Cache the data with timestamp
        appCache.clusterCache[cacheKey] = {
            data: jsonData,
            timestamp: new Date().getTime()
        };
        //logger.info(`\n\nappCache.clusterCache: ${cacheKey}`);
        //logger.info(`\n\nrenderInsightStory with iconsData: ${iconsData}`);
        renderInsightStory(jsonData, iconsData)
        
        // Render the story
        async function renderInsightStory(jsonData, iconsData) {
            logger.info('renderInsightStoryy()');

            //logger.info(`\n\nrenderInsightStory with ${iconsData}`);

            const matchingInsight = jsonData.find(item => item.insight_details.url_id === postId);
            //logger.info(`\n\matchingInsight @ ${matchingInsight}`);

            if (!matchingInsight) {
                logger.info('no matching insight');
                return res.status(404).render('error', { error: 'No matching insight found.' });
            }
        
            // Update icon URLs with the subject title
            const updatedIcons = updateIconUrls(iconsData, matchingInsight.insight_details.subject_title);
            //logger.info(`\n\npdatedIcons @ ${updatedIcons}`);

            // Process related searches
            const relatedSearches = (matchingInsight.related_topics || []).map(topic => ({
                url_id: topic.url_id,
                cluster_id: topic.cluster_id,
                subject_title: topic.subject_title,
                data_category: topic.data_category,
                data_category_id: topic.data_category_id,
            }));
        
            const displayRelatedSearches = relatedSearches.length > 50
                ? shuffleArray(relatedSearches).slice(0, 50)
                : relatedSearches;
        
            // Process media
            const { images, videos } = await processMedia(matchingInsight.media);
            const defaultImgUrl = matchingInsight.media.default_img || (images.length > 0 ? images[0].img_url : '');
        
            // Ensure each image has a data_src_index
            images.forEach((img, index) => {
                if (typeof img.data_src_index === 'undefined') {
                    img.data_src_index = index;  // Or use the actual index from JSON if available
                }
            });
        
            // Convert Markdown to HTML
            const dirtyHtml = marked(matchingInsight.text_block.content);
        
            // Sanitize the HTML
            const cleanHtml = DOMPurify.sanitize(dirtyHtml);
            logger.info(`rendering content for ${matchingInsight.insight_details.subject_title}`);

            res.render('_insightStory', {
                data: jsonData,
                postId,
                searchTerms: displayRelatedSearches,
                images,
                default_image: defaultImgUrl,
                title: matchingInsight.insight_details.subject_title,
                category: matchingInsight.insight_details.data_category,
                categoryID: matchingInsight.insight_details.data_category_id,
                clusterID: matchingInsight.insight_details.cluster_id,
                subjTitle: matchingInsight.insight_details.search_term,
                text_block: cleanHtml,
                videoDetails: videos,
                iconsData: updatedIcons, // Pass updated icons here
                imgBasePath: '/img/',
                layout: false
            });
        }
        

    } catch (error) {
        logger.error(`Error: ${error}`);
        res.status(500).send('Internal Server Error');
    }
});

router.post(globalEndpoints.updateLeftColumn, (req, res) => {
    //logger.info(globalEndpoints.updateLeftColumn);
    const insights = req.body.insights || [];  // Ensure insights is an array, default to an empty array if not provided

    try {
        // Render the _leftColumnInsights.ejs with the insights data
        res.render('_leftColumnInsights', { insights, layout: false });
    } catch (error) {
        logger.error(`Error rendering left column: ${error}`);
        res.status(500).send('Internal Server Error');
    }
});

router.post(globalEndpoints.updateLeftColumnDetails, (req, res) => {
    //logger.info(globalEndpoints.updateLeftColumnDetails);
    const { dataTitle, dataCategory, dataSubject, imgDesc1, imgDesc2, imgSrc } = req.body;
    res.render('_leftColumnDetails', {
        dataTitle,
        dataCategory,
        dataSubject,
        imgDesc1,
        imgDesc2,
        imgSrc,
        layout: false
    });
});


router.get(globalEndpoints.serveImage, async (req, res) => {
    logger.info(globalEndpoints.serveImage);

    const { date, file } = req.query;
    if (!date || !file) {
        //logger.info('/serve-image missing parameters:', { date, file });
        return res.status(400).send('Date and file parameters are required');
    }
    //logger.info('/serve-image parameters:', { date, file });

    const screenshotsBaseDir=BASE_PATHS.reporting;
    logger.info('screenshotsBaseDir:', screenshotsBaseDir);
    console.log('screenshotsBaseDir:', screenshotsBaseDir);

    if (!screenshotsBaseDir) {
        logger.error(`BKDS_REPORTING_SCREENSHOTS environment variable is not set`);
        return res.status(500).send('Server configuration error: Missing BKDS_REPORTING_SCREENSHOTS');
    }

    const fullFilePath = path.join(FILE_PATHS.screenshot_dir, file);
    //logger.info('fullFilePath:', fullFilePath);
    console.log('fullFilePath:', fullFilePath);

    try {
        const image = await fs.readFile(fullFilePath);
        res.writeHead(200, { 'Content-Type': 'image/png' });
        res.end(image, 'binary');
    } catch (error) {
        logger.error(`Error reading image: ${error}`);
        res.status(404).send('Image not found');
    }
});
    

    
router.post(globalEndpoints.updateLeftColumnKeywords, async (req, res) => {    
    const { dataCategory } = req.body;
    logger.info(`update ${globalEndpoints.updateLeftColumnKeywords} with ${dataCategory}`);

    try {
        // Fetch icons and category filters from endpoints
        const iconsResponse = await fetch(`${globalEndpoints.icons}?type=desktop_app_search`);
        const categoryResponse = await fetch(`${rootNode}${globalEndpoints.dataCategoryFilters}?type=category`);

        if (!iconsResponse.ok || !categoryResponse.ok) {
            throw new Error('Failed to fetch icons or category data');
        }

        const iconsData = await iconsResponse.json();
        const dataItems = await categoryResponse.json();

        // Render the partials on the server
        res.render('_leftColumnIcons', { photoGalleryFilterIcons: iconsData, layout: false });
        res.render('_filterSummary', { dataCategoryFilters: dataItems, layout: false });


    } catch (error) {
        logger.error(`Error fetching icons or category filters: ${error}`);
        res.status(500).send('Internal Server Error');
    }
});


// Endpoint for fetching insights based on filterCategory
router.get(globalEndpoints.fetchAllInsights, async (req, res) => {
    logger.info(globalEndpoints.fetchAllInsights);
    const filterCategory = req.query.filterCategory || 'main_feed'; // Default category to 'main_feed' if none is provided
    const page = parseInt(req.query.page, 10) || 1; // Parse the page query param, default to 1 if invalid
    const limit = parseInt(req.query.limit, 10) || defaultLimit; // Parse the limit query param, default to defaultLimit if invalid
    logger.info(`update ${globalEndpoints.fetchAllInsights} with ${filterCategory}`);

    try {
        // Fetch insights based on filterCategory, page, and limit
        const insights = await fetchAndTransformInsights(filterCategory, page, limit);

        // Render the insights using the _mainFeed partial template with the fetched insights
        res.render('_mainFeed', {
            title: 'Hello Jason Home', 
            subjectInsights: insights, // Pass the insights data to the EJS template
            layout: false
        });
    } catch (error) {
        // Log the error and respond with a 500 Internal Server Error
        logger.error(`Error fetching insights: ${error}`);
        res.status(500).send('Internal Server Error');
    }
});



// New endpoint for fetching insights as JSON
router.get(globalEndpoints.fetchInsightsJson, async (req, res) => {
    logger.info(globalEndpoints.fetchInsightsJson);

    const filterCategory = req.query.filterCategory || 'main_feed';
    const page = parseInt(req.query.page, 10) || 1;
    const limit = parseInt(req.query.limit, 10) || 20;
    logger.info(`${globalEndpoints.fetchInsightsJson} with ${filterCategory}`);

    try {
        // Fetch and transform insights with pagination
        let insights = await fetchAndTransformInsights(filterCategory, page, limit);

        // Remove the 'text_content' field from each insight
        insights = insights.map(insight => {
            const { text_content, ...rest } = insight;  // Destructure and omit text_content
            return rest;
        });

        // Return the modified insights as JSON response
        res.json({ insights });
    } catch (error) {
        logger.error(`Error fetching insights: ${error}`);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});



router.get(globalEndpoints.home, async (req, res) => {
    logger.info(globalEndpoints.home);
    try {
        // Fetch main feed insights without pagination (all insights)
        const subjectInsights = await fetchAndTransformInsights('main_feed');

        // Fetch icons data
        const iconsData = await getIconsData();

        // Filter the icons for various toolbar sections
        const powerCenterIcons = iconsData.filter(icon => icon.type === 'power_center_control');
        const desktopControlIcons = iconsData.filter(icon => icon.type === 'desktop_control_icon');
        const photoGalleryFilterIcons = iconsData.filter(icon => icon.type.startsWith('desktop_app_search'));
        const categoryResponse = await fetch(`${rootNode}${globalEndpoints.dataCategoryFilters}?type=category`);
        const dataCategoryFilters = await categoryResponse.json();
        const toolbarIconsData = iconsData.filter(icon => icon.type.startsWith('toolbar_search'));

        // Set photoGridType to 'default' and pass an empty array for paginatedImages
        const photoGridType = 'default';
        const paginatedImages = []; // Empty array initially

        res.render('_home', {
            title: 'Hello Jason Home',
            subjectInsights,
            powerCenterIcons,
            desktopControlIcons,
            photoGalleryFilterIcons,
            dataCategoryFilters,
            toolbarIconsData,
            photoGridType,
            paginatedImages // Pass empty array to _imageGrid
        });
        
    } catch (error) {
        logger.error(`Error rendering home page: ${error}`);
        res.status(500).send('Internal Server Error');
    }
});

// ###########################

// SERVER END POINT END

//###########################


// ###########################
// EXPORT ROUTER
// ###########################

module.exports = router;