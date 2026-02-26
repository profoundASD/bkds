###
parent script
###
#!/bin/bash

# Generate the pattern commands from a-z and 0-9 and submit them to the background
for char in {a..z} {0..9}; do
  echo "Starting process for pattern: gallery_wiki_${char}*"
  bash bkds_imgTagUpdate.sh "/home/aimless76/Documents/Sync/BKDS/BKDS-APP/BKDS-NODEJS/public/data/images/full_size/wiki/gallery_wiki_${char}*" > "log_${char}.txt" 2>&1 &
done

# Print a message to indicate that all commands have been submitted
echo "All background processes have been started for patterns a-z and 0-9."

# Wait for all background processes to finish
wait

echo "All background processes have completed."

