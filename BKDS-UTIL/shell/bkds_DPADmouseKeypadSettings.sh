#!/bin/bash

########################################################################
# Toggle MouseKeys on/off using the D-Pad.
# This script toggles between enabling and disabling MouseKeys, 
# providing visual feedback and logging status.
########################################################################

# Set DISPLAY variable for X session
export DISPLAY=:0

# Define the control file to track MouseKeys status
CONTROL_FILE="$HOME/.mousekeys_status"

# Debug: Check if DISPLAY is set correctly
echo "DISPLAY is set to: $DISPLAY"

# Check if xkbset is installed
if ! command -v xkbset &> /dev/null; then
    echo "Error: xkbset command not found. Please install it."
    exit 1
fi

# Helper function to reset key repeat
reset_key_repeat() {
    xset r off
    sleep 0.15
    xset r on
}

# Function to turn off MouseKeys
turn_off_mousekeys() {
    xkbset -m
    if [ $? -eq 0 ]; then
        rm -f "$CONTROL_FILE"
        echo "MouseKeys turned off."
    else
        echo "Error: Failed to turn off MouseKeys. Check XKB support on display: $DISPLAY"
    fi
}

# Function to turn on MouseKeys with custom settings
turn_on_mousekeys() {
    # Set MouseKeys acceleration settings (modify values as needed)
    xkbset ma 60 10 10 15 15
    sleep 0.15
    xkbset ma 60 10 10 15 15

    if [ $? -eq 0 ]; then
        xkbset m
        touch "$CONTROL_FILE"
        echo "MouseKeys turned on with specified settings."
    else
        echo "Error: Failed to turn on MouseKeys. Check XKB support on display: $DISPLAY"
    fi
}

# Toggle MouseKeys on/off based on the presence of the control file
if [ -f "$CONTROL_FILE" ]; then
    # MouseKeys are currently on, turn them off
    turn_off_mousekeys
else
    # MouseKeys are currently off, turn them on
    turn_on_mousekeys
fi

# Reset key repeat settings as needed
reset_key_repeat
