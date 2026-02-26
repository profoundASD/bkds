// bkds_router_variables.js
import path from 'path';

// Helper function to get the current date in YYYYMMDD format using local time
const getCurrentDateFormatted = () => {
    const currentDate = new Date();
    const year = currentDate.getFullYear();
    const month = String(currentDate.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const day = String(currentDate.getDate()).padStart(2, '0');
    return `${year}${month}${day}`;
};

// Function to dynamically generate global variables using environment variables
const routerGlobalVariables = (hostname) => {

    const screenshotsBaseDir = path.join(
        process.env.BKDS_REPORTING_SCREENSHOTS || '/default/path/for/screenshots', // Use default if not set
        hostname
    );

    return {
        screenshotsBaseDir,
        shellPath: '/usr/bin/bash',  // The path to the shell to use
        programName: 'bkds_DesktopControl.sh',  // Script name for power control
        defaultProgramArg: 'BKDS_DESKTOP_CONTROL_UI',  // Default argument type for power control scripts
    };
};

export { routerGlobalVariables };
