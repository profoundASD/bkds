import argparse
import datetime
import logging
import os
import sys
from google.cloud import texttospeech
from pydub import AudioSegment
import simpleaudio as sa

# TTS Settings
tts_language_code = 'en-GB'
tts_lang_name = 'en-GB-Neural2-D'  # Example voice model
tts_gender = texttospeech.SsmlVoiceGender.MALE  # Change as needed
tts_encoding = texttospeech.AudioEncoding.MP3
tts_speaking_rate = 0.8
tts_volume_gain_db = -1

########################################################################
#  Main logic and functions


def setup_directories(audio_out_ref, text_in_ref):
    print(f"setting up {audio_out_ref} and {text_in_ref}")
    audio_out_dir = os.getenv(audio_out_ref)
    if audio_out_dir is None:
        raise EnvironmentError(f"{audio_out_ref} environment variable not set.")
    
    output_file_path = audio_out_dir
    if not os.path.exists(output_file_path):
        print('made directory, did not exist')
        os.makedirs(output_file_path)
    
    text_in_dir = os.getenv(text_in_ref)
    if text_in_dir is None:
        raise EnvironmentError(f"{text_in_ref} environment variable not set.")

    return output_file_path, text_in_dir

def read_text_file(file_path):
    print(f"reading from file_path {os.path.basename(file_path)}")
    with open(file_path, 'r') as file:
        return file.read()
    

def synthesize_speech(text, output_file, language_code, lang_name, gender, encoding, speaking_rate, volume_gain_db):
    print(f'synthesizing speech with {lang_name} {gender} {encoding} {speaking_rate} and {volume_gain_db}')
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=lang_name,
        ssml_gender=gender
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=encoding,
        speaking_rate=speaking_rate,
        volume_gain_db=volume_gain_db
    )
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    if write_audio_file(output_file, response.audio_content):
        play_audio(output_file)
    else:
        print("Failed to write the audio file. Playback aborted.")

def write_audio_file(output_file, audio_content):
    print(f"attempting to write audio file: {os.path.basename(output_file)}")
    try:
        with open(output_file, 'wb') as out:
            out.write(audio_content)
        return True
    except IOError as e:
        print(f"An error occurred while writing the file: {e}")
        return False
    
def play_audio(file_path):
    print(f"attempting to play ${os.path.basename(file_path)}")

    audio = AudioSegment.from_file(file_path, format="mp3")
    playback = sa.play_buffer(
        audio.raw_data, 
        num_channels=audio.channels, 
        bytes_per_sample=audio.sample_width, 
        sample_rate=audio.frame_rate
    )
    playback.wait_done()  # Wait for playback to finish


def main():
    print(f"inside {os.path.basename(sys.argv[0])}")
    parser = argparse.ArgumentParser(description="Text to Speech Converter")
    parser.add_argument("warmup_file", help="Path to the warmup MP3 file")
    parser.add_argument("input_file", help="Path to the input text file")
    parser.add_argument("output_file", help="Path to the output MP3 file")
    args = parser.parse_args()

    output_file_path, text_in_dir = setup_directories('DEVUTIL_AUDIO_GEN_MP3OUT', 'DEVUTIL_AUDIO_GEN_TTS_SOURCE')
    
    tts_input_file = os.path.join(text_in_dir, args.input_file)
    audio_warmup_file=os.path.join(text_in_dir, args.warmup_file)
    audio_out_file = os.path.join(output_file_path, args.output_file)
    print(f"using {os.path.basename(tts_input_file)}, \
                  {os.path.basename(audio_warmup_file)}, \
                  {os.path.basename(audio_out_file)}")

    play_audio(audio_warmup_file)
    text = read_text_file(tts_input_file)
    print("launching synth")
    synthesize_speech(text, audio_out_file, tts_language_code, tts_lang_name, tts_gender, tts_encoding, tts_speaking_rate, tts_volume_gain_db)

if __name__ == "__main__":
    main()
