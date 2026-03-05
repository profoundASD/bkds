#!/usr/bin/env python3
import os
import argparse
import json
import subprocess
import fnmatch
##############################################################################
"""
Text-to-Speech Conversion Script

This script processes text-to-speech (TTS) conversion requests. It reads TTS configurations from a JSON file and generates audio files using the Google Cloud Text-to-Speech API. The script supports processing a single TTS request or all requests specified in the JSON file.

Arguments:
- ttsID: The identifier of the TTS request to process, or 'all' to process all requests in the JSON file.

Environment Variables:
- DEVUTIL_AUDIO_GEN: Batch ID for the TTS process.
- BKDS_UTIL_PYTHON: Directory path for Python utilities.
- DEVUTIL_AUDIO_GEN_TTS_SOURCE: Directory containing the TTS JSON source files.
- DEVUTIL_AUDIO_GEN_MP3OUT: Output directory for the generated MP3 files.

The script uses 'bkdsAudioGen.py' for generating the audio files. The TTS configurations, including language code, voice model, speaking rate, volume, gender, and encoding, are specified in the JSON file.

Usage:
  python <script_name> [ttsID]

"""
##############################################################################
# Main Setup / Variables
batch_id = os.getenv("DEVUTIL_AUDIO_GEN", "DEVUTIL_AUDIO_GEN")

parser = argparse.ArgumentParser(description="Text to Speech Converter")
parser.add_argument("ttsID", help="TTS ID to process or 'all' for all phrases")
args = parser.parse_args()

# Directories and file paths
python_path = os.getenv("BKDS_UTIL_PYTHON")
tts_source = os.getenv("DEVUTIL_AUDIO_GEN_TTS_SOURCE")
audio_data = os.getenv("DEVUTIL_AUDIO_GEN_MP3OUT")
print (f'tts source: {tts_source}')
# Scripts used
tts_gen_script = os.path.join(python_path, "bkdsAudioGen.py")

# Other files/settings used
tts_key_pattern = "*tts_sources*.json"
out_type = "mp3"

DEFAULT_LANGUAGE_CODE = "en-GB"
DEFAULT_LANG_NAME = "en-GB-Neural2-D"
DEFAULT_SPEAKING_RATE = "0.8"
DEFAULT_VOLUME_GAIN_DB = "-1"
DEFAULT_GENDER = "texttospeech.SsmlVoiceGender.MALE"
DEFAULT_ENCODING = "texttospeech.AudioEncoding.MP3"

##############################################################################
#  Main logic and functions

# Find the latest JSON file using a wildcard pattern
json_files = sorted(
    [
        os.path.join(tts_source, f)
        for f in os.listdir(tts_source)
        if fnmatch.fnmatch(f, "*tts_sources*.json")
    ],
    key=lambda f: os.path.getmtime(f),
    reverse=True,
)
print(f"json files: {json_files}")
if not json_files:
    print(f"No input in {tts_source} with required pattern {tts_key_pattern}.")
    exit(1)

latest_json_file = json_files[0]

print(f"JSON input file used: {os.path.basename(latest_json_file)}")
print("Beginning TTS conversion from JSON data")

# Function to process a single phrase by ttsID
def process_phrase(entry):
    tts_text = entry["tts_text"]
    target_filename = entry["target_filename"]
    language_code = entry.get("tts_language_code", DEFAULT_LANGUAGE_CODE)
    lang_name = entry.get("tts_lang_name", DEFAULT_LANG_NAME)
    speaking_rate = entry.get("tts_speaking_rate", DEFAULT_SPEAKING_RATE)
    volume_gain_db = entry.get("tts_volume_gain_db", DEFAULT_VOLUME_GAIN_DB)
    gender = entry.get("tts_gender", DEFAULT_GENDER)
    encoding = entry.get("tts_encoding", DEFAULT_ENCODING)
    # Create the full path for the output audio file
    audio_output_file = os.path.join(
        audio_data, f"{target_filename}.{out_type}"
    )

    # Run the TTS generation script for the current phrase
    subprocess.run(
        [
            "python3",
            tts_gen_script,
            tts_text,
            audio_output_file,
            language_code,
            lang_name,
            speaking_rate,
            volume_gain_db,
            gender,
            encoding
        ]
    )
    print(f"Completed TTS conversion for: {target_filename}")

# Read the JSON data
with open(latest_json_file, "r") as json_file:
    data = json.load(json_file)

# Check if 'all' is specified as ttsID, process all phrases
# Check if 'all' is specified as ttsID, process all phrases
if args.ttsID == "all":
    for entry in data:
        process_phrase(entry)
# Process the specified ttsID
else:
    for entry in data:
        json_ttsID = entry.get("ttsID")
        if json_ttsID == args.ttsID:
            process_phrase(entry)
            break
    else:
        print(f"TTSID '{args.ttsID}' not found in the JSON file.")

print("TTS conversions from JSON completed")
