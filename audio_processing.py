import logging
import speech_recognition as sr
from pydub import AudioSegment

logging.basicConfig(level=logging.DEBUG)

def process_audio_chunk(chunk, recognizer):
    try:
        # Export the audio chunk to a temporary WAV file
        chunk.export("temp.wav", format="wav")

        # Recognize the audio using Google Speech Recognition for en-US
        with sr.AudioFile("temp.wav") as source:
            audio_data_us = recognizer.record(source)
        
        # Recognize the audio using Google Speech Recognition for en-UK
        with sr.AudioFile("temp.wav") as source:
            audio_data_uk = recognizer.record(source, language='en-UK')

        # Use a more robust recognition method to handle all alternatives for en-US
        text_us = ""
        try:
            response_us = recognizer.recognize_google(audio_data_us, show_all=True, language='en-US')
            
            if 'alternative' in response_us:
                alternatives_us = response_us['alternative']
                transcripts_us = [alt['transcript'] for alt in alternatives_us]
                text_us = " ".join(transcripts_us)
        except Exception as e:
            logging.error(f"Error recognizing alternatives for en-US: {e}")

        # Use a more robust recognition method to handle all alternatives for en-UK
        text_uk = ""
        try:
            response_uk = recognizer.recognize_google(audio_data_uk, show_all=True, language='en-UK')
            
            if 'alternative' in response_uk:
                alternatives_uk = response_uk['alternative']
                transcripts_uk = [alt['transcript'] for alt in alternatives_uk]
                text_uk = " ".join(transcripts_uk)
        except Exception as e:
            logging.error(f"Error recognizing alternatives for en-UK: {e}")

        return text_us, text_uk
    except Exception as e:
        logging.error(f"Error processing audio chunk: {e}")
        return "", ""
