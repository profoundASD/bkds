#!/bin/bash

# Function to get the current mouse location
get_mouse_location() {
    xdotool getmouselocation --shell | awk -F'[: ]' '{print $2, $4}'
}

# Function to simulate a mouse click at given coordinates
#!/bin/bash

# Function to simulate a mouse click at given coordinates
simulate_mouse_click() {
    local x=$1
    local y=$2
    xdotool mousemove click 1
}

# Main loop
while true; do
    sleep 5 # Replace X with your desired interval in seconds
    # Get current mouse location
    mouse_location=$(xdotool getmouselocation --shell)
    
    # Extract X and Y coordinates
    mouse_x=$(awk -F'[: ]' '{print $2}' <<< "$mouse_location")
    mouse_y=$(awk -F'[: ]' '{print $4}' <<< "$mouse_location")

    # Simulate a mouse click at the current location
    simulate_mouse_click "$mouse_x" "$mouse_y"
    
    # Adjust sleep time as needed
    sleep 5 # Replace X with your desired interval in seconds
done
