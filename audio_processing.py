import logging
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

logging.basicConfig(level=logging.DEBUG)

def preprocess_audio_chunk(chunk):
    # Normalize audio to a consistent volume level
    return chunk.normalize()

def process_audio_chunk(chunk, recognizer):
    try:
        # Preprocess the audio chunk
        chunk = preprocess_audio_chunk(chunk)

        # Recognize the audio using a streaming recognizer
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        recognizer.operation_timeout = 5
        audio_chunks = split_on_silence(chunk, min_silence_len=500, silence_thresh=-40)
        recognized_text = ""
        for audio_chunk in audio_chunks:
            with sr.AudioData(audio_chunk.raw_data, sample_rate=audio_chunk.frame_rate, sample_width=audio_chunk.sample_width):
                text = recognizer.recognize_google(audio_chunk, show_all=False, language='en-US')
                recognized_text += text + " "
        return recognized_text
    except Exception as e:
        logging.error(f"Error processing audio chunk: {e}")
        return ""
