const globalEndpoints = {
  imageGrid: '/image-grid',
  fetchInsightsJson: '/fetch-insights-json',
  fetchAllInsights: '/fetch-all-insights',
  photosFullscreen: '/photos/fullscreen',
  updateLeftColumnKeywords: '/update-left-column-keywords', 
  updateLeftColumnDetails: '/update-left-column-details', 
  updateLeftColumn: '/update-left-column', 
  refreshContent: '/refresh-content', 
  insightStoryContent: '/insightStoryContent',
  executePower: '/execute-power-command',
  speechRec: '/speech',
  synth: '/synthesize',
  uiMessage: '/ui-message',
  icons: '/icons',
  appToolbar: '/appLaunchToolbar',
  saveVoiceSearch: '/saveVoiceSearch',
  bannedWords: '/banned-words',
  headerContent: '/header-content',
  dataCategoryFilters: '/dataCategoryFilters',
  serveImage: '/serve-image',
  home: '/',
};

// Export for both Node.js (server) and browser (client)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = globalEndpoints;
} else {
  window.globalEndpoints = globalEndpoints;
}