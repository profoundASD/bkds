#!/bin/bash
#####################################################################
# Script Description:
# This script automates the generation of audio from text using TTS (Text-To-Speech).
# It dynamically selects the latest 'tts_input_*.txt' file from a specified source directory unless a text string is provided.
# The output audio file's name is derived from the input file's name or a custom prefix if specified.
#
# Main Variables:
# - batch_id: Optional. If not specified, defaults to 'BKDS_AUDIO_GEN'.
# - out_prefix: Optional. Prefix for the output audio file, defaults to 'bkds_tts_' if not provided.
# - text_input: Optional. If provided, bypasses file lookup and uses the input text string directly.
#
# Usage:
# ./script_name.sh [batch_id] [out_prefix] [text_input]
# Example: ./script_name.sh BKDS123 custom_prefix_ "This is a test audio generation"
#
# Features:
# - Dynamically processes the latest TTS input file unless a text string is provided.
# - Logs key information and generates an output audio file.
#
#####################################################################
# Main Setup / Variables
program_name="$(basename "${0%.*}")"
batch_id=${1:-"DEVUTIL_AUDIO_GEN"}
out_prefix=${2:-"devutil_tts_"}
text_input=$3  # Third argument: Optional text string

# Directories and file paths
python_path="$BKDS_UTIL_PYTHON"
#tts_source="$DEVUTIL_AUDIO_GEN_TTS_SOURCE"
audio_data="$BKDS_UTIL_MP3"

# Scripts and files used
tts_gen_script="$python_path/bkds_AudioGen.py"
audio_warmup_file="$audio_data/clips/devutil_tts_audio_warmup_silence.mp3"
tts_prefix='bkds_tts_ui_audio_gen'

########################################################################
# Main logic and functions

# Bypass file lookup if a text string is provided
if [[ -n "$text_input" ]]; then
    echo "Text input detected. Bypassing file lookup."
    echo "Generating audio from text: $text_input"
    python3 $tts_gen_script --prefix $tts_prefix --text_string "$text_input"
    echo "Completed TTS conversion from text input."
    exit 0
fi

echo "Completed TTS conversion."