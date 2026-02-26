#!/bin/bash
#####################################################################
# Script Description:
# This script automates the generation of audio from text using TTS (Text-To-Speech).
# It dynamically selects the latest 'tts_input_*.json' file from a specified source directory.
# It allows you to specify a 'ttsID' as an argument to process a specific phrase or "all" phrases from the JSON file.
# The output audio file's name is derived from the input file's name.
#
# Main Variables:
# - batch_id: Optional. If not specified, defaults to 'BKDS_AUDIO_GEN'.
# - out_prefix: Optional. Prefix for the output audio file, defaults to 'devutil_tts_' if not provided.
# - tts_source: Environment variable specifying the source directory for TTS input JSON files.
# - audio_data: Environment variable specifying the output directory for generated audio files.
#
# Usage:
# ./script_name.sh [batch_id] [out_prefix] [ttsID]
# Example: ./script_name.sh BKDS123 custom_prefix_ TTS000
# Example (process all phrases): ./script_name.sh BKDS123 custom_prefix_ all
#
# Features:
# - Automatically finds and processes the latest TTS input JSON file.
# - Logs key information, including input file details and a sample of input data.
# - Generates an output audio file for the specified 'ttsID' or for all phrases in the JSON file.
#
# Usage: bash $BKDS_UTIL_SHELL/bkdsAudioGen.sh output_Filename output_prefix_ ttsID
#####################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=${1:-"DEVUTIL_AUDIO_GEN"}
out_prefix=${2:-"devutil_tts_"}
ttsID=${3}
# Directories and file paths
python_path="$BKDS_UTIL_PYTHON"
tts_source="$DEVUTIL_AUDIO_GEN_TTS_SOURCE"
audio_data="$DEVUTIL_AUDIO_GEN_MP3OUT"
# Scripts used
tts_gen_script="$python_path/bkdsAudioGen.py"
# Other files/settings used
audio_warmup_file="$audio_data/clips/devutil_tts_audio_warmup_silence.mp3"
tts_key_pattern='*tts_sources*.json'
out_type='mp3'

# Find the latest JSON file
latest_json_file=$(ls -t ${tts_source}/${tts_key_pattern} | head -n 1)

# Check if the input JSON file exists
if [ ! -f "$latest_json_file" ]; then
    echo "File not found: $latest_json_file"
    echo "No input in $tts_source with required pattern $tts_key_pattern."
    exit 1
fi

echo $'JSON input file used:'"$(basename "$latest_json_file")"
echo "Beginning TTS conversion from JSON data"

# Function to process a single phrase by ttsID
process_single_phrase() {
    local ttsID="$1"
    while IFS= read -r line; do
        json_ttsID=$(echo "$line" | jq -r '.ttsID')
        if [ "$json_ttsID" == "$ttsID" ]; then
            tts_text=$(echo "$line" | jq -r '.tts_text')
            
            target_filename=$(echo "$line" | jq -r '.target_filename')

            # Create the full path for the output audio file
            audio_output_file="${audio_data}/${out_prefix}${target_filename}.${out_type}"

            # Run the TTS generation script for the current phrase
            python3 $tts_gen_script $audio_warmup_file "$tts_text" $audio_output_file
            echo "Completed TTS conversion for: $target_filename"
            return
        fi
    done < "$latest_json_file"

    echo "TTSID '$ttsID' not found in the JSON file."
}

# Check if 'all' is specified as ttsID, process all phrases
echo "checking all"
sleep 2
if [ "$ttsID" == "all" ]; then
echo "found all"
sleep 2
    while IFS= read -r line; do
       echo "reading line $line"
        sleep 2
        tts_text=$(echo "$line" | jq -r '.tts_text')
        
        target_filename=$(echo "$line" | jq -r '.target_filename')

        # Create the full path for the output audio file
        audio_output_file="${audio_data}/${out_prefix}${target_filename}.${out_type}"

        # Run the TTS generation script for the current phrase
        python3 $tts_gen_script $audio_warmup_file "$text" $audio_output_file
        echo "Completed TTS conversion for: $target_filename"
    done < "$latest_json_file"

# Process the specified ttsID
else
    process_single_phrase "$ttsID"
fi

echo "TTS conversions from JSON completed"
