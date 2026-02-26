const pino = require('pino');
const fs = require('fs');
const path = require('path');
const os = require('os');

// Helper to get the log file path with the specified structure
const getLogFilePath = () => {
  const baseLogDir = process.env.BKDS_UTIL_LOGS || './BKDS-LOGS';
  const hostname = os.hostname();
  const now = new Date();
  const dateStamp = now.toISOString().slice(0, 10); // e.g., "2024-11-26"
  const hourStamp = now.toISOString().slice(11, 13); // e.g., "14" for 2 PM UTC
  const yyyymmddUTC = now.toISOString().slice(0, 10).replace(/-/g, ''); // e.g., "20241126"

  const logDir = path.join(baseLogDir, hostname, yyyymmddUTC, 'BKDS_NODEJS_LOGS');
  const fileName = `bkkds_app_nodejs_${dateStamp}_hour${hourStamp}.log`;

  return path.join(logDir, fileName);
};

let currentLogFilePath = getLogFilePath();
let logStream = initializeLogStream(currentLogFilePath);

// Function to initialize the log stream
function initializeLogStream(filePath) {
  const logDir = path.dirname(filePath);
  if (!fs.existsSync(logDir)) {
    try {
      fs.mkdirSync(logDir, { recursive: true });
      console.log(`Directory created: ${logDir}`);
    } catch (error) {
      console.error(`Failed to create directory ${logDir}:`, error);
    }
  }
  return fs.createWriteStream(filePath, { flags: 'a' });
}

// Function to check and update the log file path
function updateLogStreamIfNeeded() {
  const newLogFilePath = getLogFilePath();
  if (newLogFilePath !== currentLogFilePath) {
    console.log(`Log file changed from ${currentLogFilePath} to ${newLogFilePath}`);
    currentLogFilePath = newLogFilePath;
    logStream.end(); // Close the existing stream
    logStream = initializeLogStream(currentLogFilePath); // Reinitialize
  }
}

// Create a Pino logger instance
const logger = pino(
  {
    level: 'info',
    timestamp: pino.stdTimeFunctions.isoTime,
  },
  {
    write: (msg) => {
      updateLogStreamIfNeeded(); // Ensure log file is up to date
      logStream.write(msg);
    },
  }
);

module.exports = logger;
