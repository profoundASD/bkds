// Global Variables and Conmstants
let lastClickedIconID = null;
let lastClickedIconDIV = null;
//let lastDataIndex = 0;
let currentPage = 1;
let startPage = 1;

const pageSize = 50;
const loadThreshold = 0.75;
let isLoading = false;
let lastClickedGalleryIcon = null;
// Function to initialize the gallery and setup scroll event listener
let currentDataCategory = null;
let isFetching = false;

const globalAttributes = {
    lastDataIndex: 0,
    src: "src",
    dataTitle: "data-title",
    dataDesc1: "data-desc1",
    dataDesc2: "data-desc2",
    dataDesc3: "data-desc3",
    dataSrc: "data-src",
    dataPage: "data-page",
    dataLimit: "data-limit",
    dataCategory: "data-category",
    dataSubject: "data-subject",
    dataIndex: "data-index",
    dataFilterCategory: "data-filter-category",
    dataInsightCluster: "data-insight-cluster",
    dataCategoryId: "data-category-id",
    dataMediaLink: "data-media-link",
    href: "href", // New entry
    photoType: "photos",
    defaultOption: "main",
    searchTermReplace: "@@_search_term_@@",
    defaultPower: "POWER_SLEEP",
    activeStatus: 'active',
    scrollBehaviorDefault: "smooth",
    galleryAction: "galleryAction",
    dataIndex: "data-index",
    speechRecService: "http://localhost:3000/?startSpeech=true&type=voice_search_general",
    homeEndPoint: "http://localhost:3000"
  };

const globalClasses = {
    // General class lists
    galleryContainer: 'gallery-container',
    insightContainer: 'insight-container',
    mainFeedFilterCategory: 'main_feed',
    desktopControlIcon: 'desktop_control_icon',
    toolbarSpeechResult: 'toolbar_speech_result',
    postContainer: 'post-container',
    relatedTopic: 'related-topic',
    insightThumbnailImage: 'insight-thumbnail-image',
    photoGalleryControl: 'photo-gallery-control',
    desktopSearchSpeechResult: 'desktop_search_speech_result',
    subjectReader: 'subject_reader',
    insightThumbnailGridFullscreen: 'insight-thumbnail-grid-fullscreen',
    insightThumbnailGrid: 'insight-thumbnail-grid',
    filterSummaryContentItem: 'filter-summary-content-item',
    galleryFilterOption: 'gallery-filter-option',
    imageGridItem: 'image-grid-item',
    photoGalleryModalContainer: 'photo-gallery-modal',
    powerCenter: "power_center_icon",

    // Specific styles
    currentGalleryStyle: 'current-gallery-thumbnail',
    filterSummaryActiveStyle: 'filter-summary-active-style',
    ttsActiveStyle: 'tts-control-active-style',
    relatedTopicActiveStyle : 'related-topic-active-style',

    photoControlActiveStyle: 'photo-control-active-style',
    activeStyles: ['current-gallery-thumbnail', 'highlighted-thumbnail', 'active-thumbnail'],
  
    // Grouped class lists
    filterSummaryClassList: 'filter-summary-content-item',
    photoGalleryClassList: 'photo-gallery-control',
    subjectReaderClassList: 'subject_reader',
    relatedTopicClassList: 'related-topic-container, filter-summary-content',
    postContainerClassList: 'contentContainer',
    imageGridContainer: 'image-grid-container',
    enlargedImgFullscreen: 'enlarged-image-fullscreen',
    enlargedImg: 'enlarged-image',
    fullscreenImage: 'fullscreen-image',
    fullscreenImageModal: 'fullscreen-image-modal',
    photoCategory: 'photos',
    photoSearchIconContainer: 'photo-search-icon-container',
    // New Entries
    mainFeedToolbarContainer: 'main-feed-toolbar-container',
    mainFeedToolbarWrapper: 'main-feed-toolbar-wrapper',
    homeDefaultInsight: 'home-default-insight',
    mainFeedContent: 'main-feed-content',
    filterSummaryContent: 'filter-summary-content',
    summaryContent: 'summary-content',
    photoGridContainer: 'photo-grid-container',
    photoGalleryFilters: 'photo-gallery-filters',
    leftColumn: 'left-column',
    leftColumnDefault: 'left-columnDefault',
    leftColumnContent: 'leftColumnContent',
    leftColumnDefaultContent: 'leftColumnDefaultContent',
    middleColumn: 'middle-column',
    contentContainer: 'contentContainer',
    toolbarIconGridContainer: 'toolbar-icon-grid-container',
    photoGridDetails: 'forever-photo-gallery-left-wrapper',
    photoGalleryThumbImage: 'photo-gallery-thumbnail-image',
    mainFeedContainer: 'mainFeedContainer',
    mainFeedReplace: 'mainFeedReplace',
    photoGrid: 'photoGrid',
    // Modal container for post content
    modalContainer: 'modal',
    tts_listen: 'tts_listen',
    tts_highlight: 'tts-highlight'
  };
  
  const globalVariables = {
    rootNode: 'http://localhost:3000',
    screenshotFolder:`BKDS_REPORTING_SCREENSHOTS`,
    screenshotRptBasePath:`../../../BKDS-APP/BKDS-BACKEND/BKDS-AUTOMATION-CONFIG/reporting/data`
  };

  const globalIds = {
    insightContainer: 'insightContainer',
    mainFeedContent: 'mainFeedContent',
    // Other IDs...
  };
  