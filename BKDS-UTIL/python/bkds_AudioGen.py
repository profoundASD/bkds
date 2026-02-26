#!/usr/bin/env python3
import os
import argparse
import hashlib
from google.cloud import texttospeech
from pydub import AudioSegment
import simpleaudio as sa
import gc  # Garbage collection
##############################################################################
# Global Variables for Default TTS Settings
DEFAULT_LANGUAGE_CODE = "en-GB"
DEFAULT_LANG_NAME = "en-GB-Neural2-B"  # Replace with the appropriate voice name from Google Cloud
DEFAULT_GENDER = "MALE"
DEFAULT_ENCODING = "MP3"
DEFAULT_SPEAKING_RATE = .55  # Normal speaking rate
DEFAULT_VOLUME_GAIN_DB = 0.0  # Normal volume gain
bkds_util_data = os.environ.get("BKDS_UTIL_DATA")
bkds_nodejs_data = os.environ.get("BKDS_NODEJS_DATA")

# Path to TTS API configuration file
TTS_API_CONFIG_FILE=os.path.join(bkds_nodejs_data, 'config', 'bkds_tts_api.json')

AUDIO_OUT_DIR = os.path.join(bkds_util_data, 'mp3', 'ui_tts_gen')

if not os.path.exists(AUDIO_OUT_DIR):
    os.makedirs(AUDIO_OUT_DIR)

audio_warmup_file = os.path.join(AUDIO_OUT_DIR, "clips", "bkds_tts_audio_warmup_silence.mp3")

##############################################################################
# Helper Functions

def hygiened_text(text):
    """Generate a hygiened version of the first 10 characters of a string."""
    return ''.join(c if c.isalnum() else '_' for c in text[:10])

def md5_hash(text):
    """Generate an MD5 hash of a string."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def generate_filename(prefix, text):
    """Generate a filename using the prefix, hygiened text, and MD5 hash."""
    hygiened = hygiened_text(text)
    md5 = md5_hash(text)
    return f"{prefix}_{hygiened}_{md5}.mp3"

def synthesize_speech(text, output_file, language_code, lang_name, gender, encoding, speaking_rate, volume_gain_db):
    """Synthesize speech from text using Google Cloud TTS."""

    # Check if the audio file already exists
    if os.path.exists(output_file):
        print(f"Audio file already exists: {output_file}. Skipping TTS generation.")
        play_audio(output_file)  # Play the existing audio
        return

    print(f"Synthesizing speech with {lang_name}, {gender}, {encoding}, {speaking_rate}, and {volume_gain_db}")
    valid_genders = ["MALE", "FEMALE", "NEUTRAL"]
    if gender not in valid_genders:
        raise ValueError(f"Invalid gender: {gender}")

    try:
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=lang_name,
            ssml_gender=getattr(texttospeech.SsmlVoiceGender, gender)
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=getattr(texttospeech.AudioEncoding, encoding),
            speaking_rate=float(speaking_rate),
            volume_gain_db=float(volume_gain_db)
        )
        client = texttospeech.TextToSpeechClient.from_service_account_file(TTS_API_CONFIG_FILE)
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        if write_audio_file(output_file, response.audio_content):
            play_audio(output_file)
            print('hello world')
        else:
            print("Failed to write the audio file. Playback aborted.")

    except Exception as e:
        print(f"An error occurred during TTS generation: {e}")


def write_audio_file(output_file, audio_content):
    """Write synthesized audio to a file."""
    print(f"Attempting to write audio file: {os.path.basename(output_file)}")
    try:
        with open(output_file, 'wb') as out:
            out.write(audio_content)
        return True
    except IOError as e:
        print(f"An error occurred while writing the file: {e}")
        return False

def play_audio(file_path):
    """Play the synthesized audio."""
    print(f"Attempting to play {os.path.basename(file_path)}")

    try:
        audio = AudioSegment.from_file(file_path, format="mp3")
        playback = sa.play_buffer(
            audio.raw_data,
            num_channels=audio.channels,
            bytes_per_sample=audio.sample_width,
            sample_rate=audio.frame_rate
        )
        
        # Non-blocking playback loop
        while playback.is_playing():
            pass
        
        print("Audio playback completed.")
        
        # Explicitly clean up memory
        del playback
        del audio
        gc.collect()

    except Exception as e:
        print(f"An error occurred during audio playback: {e}")

##############################################################################
# Main Function

def main():
    print('bkds_AudioGen.py main()')
    parser = argparse.ArgumentParser(description="Text to Speech Converter")
    parser.add_argument("--prefix", help="Prefix for the output file name")
    parser.add_argument("--text_string", help="Text string to be converted to speech")
    parser.add_argument("--language_code", default=DEFAULT_LANGUAGE_CODE, help="Language code for TTS")
    parser.add_argument("--lang_name", default=DEFAULT_LANG_NAME, help="Language name for TTS")
    parser.add_argument("--speaking_rate", type=float, default=DEFAULT_SPEAKING_RATE, help="Speaking rate for TTS")
    parser.add_argument("--volume_gain_db", type=float, default=DEFAULT_VOLUME_GAIN_DB, help="Volume gain in dB for TTS")
    parser.add_argument("--gender", default=DEFAULT_GENDER, help="Voice gender for TTS")
    parser.add_argument("--encoding", default=DEFAULT_ENCODING, help="Audio encoding for TTS")
    args = parser.parse_args()

    # Generate the output file name
    output_filename = generate_filename(args.prefix, args.text_string)
    audio_out_file = os.path.join(AUDIO_OUT_DIR, output_filename)
    print(f"Processing text string, outputting to {os.path.basename(audio_out_file)}")

    # Synthesize speech
    synthesize_speech(
        args.text_string, audio_out_file, args.language_code, args.lang_name, 
        args.gender, args.encoding, args.speaking_rate, args.volume_gain_db
    )

if __name__ == "__main__":
    main()
